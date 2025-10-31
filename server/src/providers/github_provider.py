import os
import asyncio
import logging
from github import Github  # type: ignore
from typing import Any, Dict, List, Optional
from .cache_provider import CacheProvider

logger = logging.getLogger(__name__)

class GitHubProvider:
    """GitHub API Provider with caching, async concurrency, and rate limit handling."""

    def __init__(self, token: str | None = None, cache_ttl: int = 6 * 3600):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN is not configured.")

        self.client = Github(self.token)
        self.cache = CacheProvider()
        self.cache_ttl = cache_ttl
        logger.info("✅ GitHubProvider initialized successfully")

    async def init_cache(self):
        """Ensure cache connection is established."""
        await self.cache.connect()

    # ─────────────────────────────
    # Utility
    # ─────────────────────────────
    def _extract_owner_repo(self, github_url: str) -> tuple[str, Optional[str]]:
        """Extract owner and repo from URL or path"""
        github_url = github_url.replace("https://github.com/", "").replace("http://github.com/", "")
        parts = github_url.strip("/").split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return parts[0], None

    # ─────────────────────────────
    # Repo Sub-fetchers
    # ─────────────────────────────
    async def _get_activity_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository activity metrics"""
        try:
            repo_obj = await asyncio.to_thread(self.client.get_repo, f"{owner}/{repo}")

            def _metrics():
                commits = list(repo_obj.get_commits()[:100])
                contributors_count = repo_obj.get_contributors().totalCount
                return {
                    "total_commits": repo_obj.get_commits().totalCount,
                    "recent_commits_count": len(commits),
                    "contributors": contributors_count,
                    "open_issues": repo_obj.open_issues_count,
                    "last_commit": {
                        "date": commits[0].commit.author.date.isoformat() if commits else None,
                        "message": commits[0].commit.message if commits else None,
                        "author": commits[0].commit.author.name if commits else None,
                    },
                }

            return await asyncio.to_thread(_metrics)
        except Exception as e:
            logger.error(f"Error getting activity metrics for {owner}/{repo}: {e}")
            return {"error": str(e)}

    async def _get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get language breakdown"""
        try:
            repo_obj = await asyncio.to_thread(self.client.get_repo, f"{owner}/{repo}")
            return await asyncio.to_thread(repo_obj.get_languages)
        except Exception as e:
            logger.error(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}
    
    async def _detect_infrastructure(self, owner: str, repo: str) -> list[str]:
        """
        Detect infrastructure tools by scanning repo files and topics.
        Looks for Docker, Kubernetes, Terraform, AWS, IPFS, etc.
        """
        try:
            repo_obj = await asyncio.to_thread(self.client.get_repo, f"{owner}/{repo}")

            # ─── Detect from topics ────────────────────────
            topics = repo_obj.get_topics()
            infra_tools = set()

            topic_text = " ".join(topics).lower()
            if "docker" in topic_text:
                infra_tools.add("Docker")
            if "kubernetes" in topic_text or "helm" in topic_text:
                infra_tools.add("Kubernetes")
            if "terraform" in topic_text:
                infra_tools.add("Terraform")
            if "aws" in topic_text or "s3" in topic_text:
                infra_tools.add("AWS")
            if "ipfs" in topic_text:
                infra_tools.add("IPFS")

            # ─── Detect from repo files ────────────────────
            contents = await asyncio.to_thread(repo_obj.get_contents, "")
            filenames = [c.name.lower() for c in contents]

            if "dockerfile" in filenames or any("docker-compose" in f for f in filenames):
                infra_tools.add("Docker")
            if any("terraform" in f for f in filenames):
                infra_tools.add("Terraform")
            if any("k8s" in f or "kubernetes" in f for f in filenames):
                infra_tools.add("Kubernetes")
            if any("aws" in f for f in filenames):
                infra_tools.add("AWS")
            if any("ipfs" in f for f in filenames):
                infra_tools.add("IPFS")

            # ─── Detect from README (for keywords) ─────────
            try:
                readme = await asyncio.to_thread(repo_obj.get_readme)
                readme_text = readme.decoded_content.decode("utf-8").lower()
                for keyword, label in [
                    ("docker", "Docker"),
                    ("kubernetes", "Kubernetes"),
                    ("terraform", "Terraform"),
                    ("aws", "AWS"),
                    ("ipfs", "IPFS"),
                    ("GitHub Actions", "CircleCI", "Jenkins", "jenkins"),
                    ("Prometheus", "Grafana", "prometheus", "grafana"),
                    ("Ansible", "ansible"),
                    ("Puppet", "puppet"),
                    ("Chef", "chef"),
                    ("OpenShift", "openshift"),
                    ("Helm", "helm"),
                    ("Nomad", "nomad"),
                    ("S3", "Pinata", "s3", "pinata"),
                ]:
                    if keyword in readme_text:
                        infra_tools.add(label)
            except Exception:
                pass  # README not found, ignore

            return sorted(list(infra_tools))

        except Exception as e:
            logger.error(f"Error detecting infrastructure for {owner}/{repo}: {e}")
            return []


    def check_rate_limit(self) -> Dict[str, Any]:
        """Check GitHub API rate limit"""
        try:
            rate_limit = self.client.get_rate_limit()
            core = rate_limit.core
            return {
                "remaining": core.remaining,
                "limit": core.limit,
                "reset": core.reset.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return {"error": str(e)}

    # ─────────────────────────────
    # Main Aggregator
    # ─────────────────────────────
    async def get_repo_stats(self, github_urls: str | List[str], force_refresh: bool = False) -> Dict[str, Any]:
        """Aggregate rich stats for one or more GitHub repos (with caching)."""
        if not github_urls:
            logger.warning("⚠️ No GitHub URLs provided to fetch stats.")
            return {}

        if isinstance(github_urls, str):
            github_urls = [github_urls]

        logger.info(f"🔍 Fetching GitHub stats for {len(github_urls)} repo(s).")

        repos_data = []
        total_stars, total_commits = 0, 0

        async def fetch_repo(owner: str, repo: str):
            cache_key = f"github:{owner}:{repo}"
            cached = None if force_refresh else await self.cache.get(cache_key)

            if cached:
                logger.info(f"💾 Cache hit for {owner}/{repo}")
                return cached

            try:
                repo_obj = await asyncio.to_thread(self.client.get_repo, f"{owner}/{repo}")
                logger.info(f"✅ Fetched {owner}/{repo} from GitHub API")

                activity = await self._get_activity_metrics(owner, repo)
                languages = await self._get_languages(owner, repo)
                infrastructure = await self._detect_infrastructure(owner, repo)

                data = {
                    "name": repo,
                    "owner": owner,
                    "stars": repo_obj.stargazers_count,
                    "forks": repo_obj.forks_count,
                    "watchers": repo_obj.watchers_count,
                    "open_issues": repo_obj.open_issues_count,
                    "language": repo_obj.language,
                    "topics": repo_obj.get_topics(),
                    "activity": activity,
                    "languages": languages,
                    "infrastructure": infrastructure,
                    "source": "github-api",
                }

                await self.cache.set(cache_key, data, ttl=self.cache_ttl)
                return data

            except Exception as e:
                logger.error(f"❌ Error fetching repo {owner}/{repo}: {e}")
                return None

        # Run all requests concurrently
        tasks = []
        for gh_url in github_urls:
            owner, repo = self._extract_owner_repo(gh_url)
            if not owner or not repo:
                logger.warning(f"⚠️ Invalid GitHub URL: {gh_url}")
                continue
            tasks.append(fetch_repo(owner, repo))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        for data in results:
            if not data or isinstance(data, Exception):
                continue
            repos_data.append(data)
            total_stars += data.get("stars", 0)
            total_commits += data.get("activity", {}).get("total_commits", 0)

        final_stats = {
            "total_stars": total_stars,
            "total_commits": total_commits,
            "repos": repos_data,
        }

        logger.info(f"📊 Aggregated GitHub stats: {final_stats}")
        return final_stats

    # ─────────────────────────────
    # Maintenance
    # ─────────────────────────────
    async def refresh_cache(self, owner: str, repo: str):
        """Force-refresh a single repo in cache."""
        _cache_key = f"github:{owner}:{repo}"
        logger.info(f"🔄 Refreshing GitHub cache for {owner}/{repo}")
        return await self.get_repo_stats([f"https://github.com/{owner}/{repo}"], force_refresh=True)
