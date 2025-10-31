import logging
import os
import json
import asyncio
from ulid import ULID # type: ignore
from sentient_agent_framework import AbstractAgent, Session, Query, ResponseHandler # type: ignore
from sentient_agent_framework.implementation.default_hook import DefaultHook # type: ignore
from sentient_agent_framework.implementation.default_response_handler import DefaultResponseHandler # type: ignore
from sentient_agent_framework.implementation.default_session import DefaultSession # type: ignore
from sentient_agent_framework.interface.identity import Identity # type: ignore

from src.providers.discovery.base_discovery import DiscoveryProvider
from src.providers.github_provider import GitHubProvider
from src.providers.twitter_provider import TwitterProvider
from src.providers.funding_provider import FundingProvider
from src.providers.llm_provider import LLMProvider
from src.providers.cache_provider import CacheProvider

# 🪵 Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def safe_json(obj):
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


class MockSessionObject:
    """Minimal mock to simulate SessionObject for offline analysis."""
    def __init__(self):
        self.processor_id = "local-processor"
        self.activity_id = ULID()
        self.request_id = ULID()
        self.interactions = []


class BuildIntelAgent(AbstractAgent):
    """
    BuildIntel Agent 🧱
    - Discovers project URLs
    - Aggregates GitHub, Twitter & Funding data
    - Generates LLM-based insight summaries
    """

    def __init__(self, name: str = "BuildIntelAgent"):
        super().__init__(name)

        # Initialize providers
        self.discovery = DiscoveryProvider()
        self.github = GitHubProvider(GITHUB_TOKEN)
        self.twitter = TwitterProvider()
        self.funding = FundingProvider()
        self.llm = LLMProvider()
        self.cache = CacheProvider()

        logger.info("✅ BuildIntel Agent initialized successfully")

    async def setup(self):
        """Async setup for providers that need connections."""

        await self.cache.connect()
        logger.info("✅ BuildIntelAgent fully initialized and connected.")

    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """Triggered when a user sends a query like 'Analyze Solana project'."""

        project_name = query.prompt.strip()
        logger.info(f"🎯 Received query: {project_name}")

        await response_handler.emit_text_block("STATUS", f"🔍 Analyzing {project_name}...")

        # 1️⃣ Try cache first
        cached_data = await self.cache.get(project_name)
        if cached_data:
            logger.info("⚡ Using cached result")
            await response_handler.emit_json("CACHED_RESULT", cached_data)
            await response_handler.complete()
            return

        # 2️⃣ Discovery
        await response_handler.emit_text_block("STATUS", "🌐 Discovering project URLs...")
        discovered = await self.discovery.discover_project(project_name)

        if not discovered:
            await response_handler.emit_text_block("ERROR", "❌ Could not discover project URLs")
            await response_handler.complete()
            return

        logger.info(f"discovered projects ${discovered}")
        await response_handler.emit_json("DISCOVERY", discovered)

        # Normalize discovery keys (support plural arrays and legacy singular keys)
        def _get_list(d, *keys):
            for k in keys:
                v = d.get(k)
                if v:
                    return v if isinstance(v, list) else [v]
            return []

        github_urls = _get_list(discovered, "githubs", "github")
        twitter_urls = _get_list(discovered, "twitters", "twitter")
        funding_urls = _get_list(discovered, "fundings", "funding")

        # 3️⃣ Aggregation (run only available tasks concurrently)
        await response_handler.emit_text_block("STATUS", "📊 Aggregating project data...")

        tasks = []
        labels = []

        if github_urls:
            tasks.append(self.github.get_repo_stats(github_urls))
            labels.append("github")
            logger.info(f"🔍 Scheduled GitHub aggregation for: {github_urls}")
        else:
            logger.info("⚠️ No GitHub URLs discovered; skipping GitHub aggregation.")

        if twitter_urls:
            tasks.append(self.twitter.get_twitter_stats(twitter_urls))
            labels.append("twitter")
            logger.info(f"🔍 Scheduled Twitter aggregation for: {twitter_urls}")
        else:
            logger.info("⚠️ No Twitter URLs discovered; skipping Twitter aggregation.")

        if funding_urls:
            tasks.append(self.funding.get_funding_info(project_name, funding_urls))
            labels.append("funding")
            logger.info(f"🔍 Scheduled Funding aggregation for project: {funding_urls}")
        else:
            logger.info("⚠️ No funding URLs discovered; skipping funding aggregation.")

        # Run tasks concurrently but only if there are tasks
        github_stats = twitter_stats = funding_info = None
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for lbl, res in zip(labels, results):
                if isinstance(res, Exception):
                    logger.error(f"❌ Aggregation task '{lbl}' failed: {res}", exc_info=True)
                    if lbl == "github":
                        github_stats = None
                    elif lbl == "twitter":
                        twitter_stats = None
                    elif lbl == "funding":
                        funding_info = None
                else:
                    if lbl == "github":
                        github_stats = res
                    elif lbl == "twitter":
                        twitter_stats = res
                    elif lbl == "funding":
                        funding_info = res
        else:
            logger.info("ℹ️ No aggregation tasks to run (no discovered urls).")

        await response_handler.emit_json("AGGREGATION", {
            "github": github_stats,
            "twitter": twitter_stats,
            "funding": funding_info
        })

        # 4️⃣ Compute composite activity metrics
        activity_metrics = self._compute_activity_metrics(github_stats, twitter_stats, funding_info)


        # 5️⃣ Generate Insight
        await response_handler.emit_text_block("STATUS", "🧠 Generating insights...")
        try:
            insight = await self.llm.generate_insight(project_name, github_stats, twitter_stats, funding_info)
        except Exception as e:
            logger.error(f"Insight generation failed: {e}", exc_info=True)
            insight = f"⚠️ Insight generation failed: {str(e)}"

        # 6 Final structured result
        result = {
            "project": project_name,
            "discovery": discovered,
            "aggregation": {
                "github": github_stats,
                "twitter": twitter_stats,
                "funding": funding_info
            },
            "activity_metrics": activity_metrics,
            "insight": insight
        }

        # 6️⃣ Cache results
        await self.cache.set(project_name, result, ttl=3600)

        # 7️⃣ Return and complete
        await response_handler.emit_json("RESULT", result)
        await response_handler.emit_text_block("STATUS", "✅ Analysis complete")
        await response_handler.complete()

        logger.info(f"✅ Analysis fully complete for {project_name}")
        logger.info(f"📦 Final result: {result}")
    
    def _compute_activity_metrics(self, github_stats, twitter_stats, funding_info):
        """
        Compute composite activity scores based on multiple sources.
        Returns a dict like:
        {
            "github_score": 82,
            "twitter_score": 75,
            "community_score": 80,
            "overall_score": 79
        }
        """
        if not github_stats:
            github_score = 0
        else:
            total_commits = github_stats.get("total_commits", 0)
            total_stars = github_stats.get("total_stars", 0)

            # Compute recency weighting from repos
            last_commits = []
            for repo in github_stats.get("repos", []):
                try:
                    date = repo["activity"]["last_commit"]["date"]
                    last_commits.append(date)
                except Exception:
                    pass

            recency_bonus = 0
            if last_commits:
                # recent commits (last 30 days = +20 bonus)
                from datetime import datetime, timezone
                recent_count = sum(
                    1 for d in last_commits
                    if (datetime.now(timezone.utc) - datetime.fromisoformat(d)).days < 30
                )
                recency_bonus = min(20, recent_count * 2)

            github_score = min(
                100,
                int((total_commits / 100) + (total_stars / 200) + recency_bonus)
            )

        # ─── Twitter Score ─────────────────────────────
        twitter_score = 0
        if twitter_stats and isinstance(twitter_stats, list):
            followers = [
                tw.get("followers") or 0 for tw in twitter_stats if isinstance(tw, dict)
            ]
            max_followers = max(followers) if followers else 0
            twitter_score = min(100, int(max_followers / 200))  # heuristic
            # optionally factor tweets
            tweets = [
                tw.get("tweets") or 0 for tw in twitter_stats if isinstance(tw, dict)
            ]
            avg_tweets = sum(tweets) / len(tweets) if tweets else 0
            twitter_score += min(20, int(avg_tweets / 1000))
            twitter_score = min(100, twitter_score)

        # ─── Community Score ──────────────────────────
        community_score = int((github_score * 0.6) + (twitter_score * 0.4))

        # ─── Overall Score ────────────────────────────
        overall_score = int(
            (github_score + twitter_score + community_score) / 3
        )

        return {
          "github_score": github_score,
          "twitter_score": twitter_score,
          "community_score": community_score,
          "overall_score": overall_score
        }

    
    async def analyze_project(self, project_name: str):
        """Run the agent directly and capture its output."""

        # 1️⃣ Setup a fake session
        session_obj = MockSessionObject()
        session = DefaultSession(session_obj)

        # 2️⃣ Create a simple response queue
        queue = asyncio.Queue()

        # 3️⃣ Hook + Identity + ResponseHandler
        hook = DefaultHook(queue)
        identity = Identity(id=session.processor_id, name=self.name)
        handler = DefaultResponseHandler(identity, hook)

        # 4️⃣ Prepare a Query
        query = Query(id=str(ULID()), prompt=project_name)

        # 5️⃣ Run the assist logic
        asyncio.create_task(self.assist(session, query, handler))

        # 6️⃣ Collect events from queue
        results = {}
        while True:
            event = await queue.get()
            results[event.event_name] = (
                event.model_dump() if hasattr(event, "model_dump") else str(event)
            )
            queue.task_done()

            # The DoneEvent signals completion
            if event.__class__.__name__ == "DoneEvent":
                break

        return json.loads(json.dumps(results, default=str))
