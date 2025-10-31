import os
import logging
import httpx # type: ignore
import base64
import re
import asyncio
from typing import List

logger = logging.getLogger(__name__)

TAVILY_SEARCH_URL = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com/search")
GITHUB_API = os.getenv("GITHUB_API_URL", "https://api.github.com") 


class FundingDiscovery:
    """
    Discover funding and investor-related pages for a given project.

    Sources:
    - Tavily (Crunchbase, AngelList, CBInsights, Tracxn, Dealroom)
    - GitHub FUNDING.yml (for open-source projects)
    Returns: List[str] of unique funding-related URLs
    """

    def __init__(self, tavily_key: str | None = None, github_token: str | None = None):
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY")
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.tavily_key:
            logger.warning("FundingDiscovery: TAVILY_API_KEY not configured; Tavily search disabled.")
        if not self.github_token:
            logger.warning("FundingDiscovery: GITHUB_TOKEN not configured; GitHub funding lookup disabled.")

    async def _fetch_github_funding(self, repo_full_name: str) -> List[str]:
        """Try to fetch funding URLs from a repo’s FUNDING.yml (if exists)."""
        if not self.github_token:
            return []

        url = f"{GITHUB_API}/repos/{repo_full_name}/contents/.github/FUNDING.yml"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(url, headers=headers)
                if r.status_code == 404:
                    return []
                r.raise_for_status()
                data = r.json()
                content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")

                # Extract sponsor URLs
                urls = re.findall(r"(https?://[^\s]+)", content)

                # Map known sponsor handles to URLs
                for match in re.finditer(
                    r"(?m)^(github|open_collective|patreon|ko_fi|buy_me_a_coffee):\s*(.+)$", content
                ):
                    platform, handle = match.groups()
                    handle = handle.strip()
                    if platform == "github":
                        urls.append(f"https://github.com/sponsors/{handle}")
                    elif platform == "open_collective":
                        urls.append(f"https://opencollective.com/{handle}")
                    elif platform == "patreon":
                        urls.append(f"https://patreon.com/{handle}")
                    elif platform == "ko_fi":
                        urls.append(f"https://ko-fi.com/{handle}")
                    elif platform == "buy_me_a_coffee":
                        urls.append(f"https://buymeacoffee.com/{handle}")

                return [u.strip() for u in urls if u.startswith("http")]
        except Exception as e:
            logger.error(f"FundingDiscovery GitHub funding error for {repo_full_name}: {e}")
            return []

    async def _tavily_funding_search(self, project_name: str, limit: int = 10) -> List[str]:
        """Discover external funding profiles via Tavily."""
        if not self.tavily_key:
            return []

        q = (
            f'"{project_name}" site:crunchbase.com OR site:angel.co '
            f'OR site:cbinsights.com OR site:tracxn.com OR site:dealroom.co'
        )
        payload = {"api_key": self.tavily_key, "query": q, "num_results": 15}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(TAVILY_SEARCH_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()

            urls = []
            for r in data.get("results", []):
                u = r.get("url")
                if not u:
                    continue
                low = u.lower()
                if any(d in low for d in ["crunchbase.com", "angel.co", "cbinsights.com", "tracxn.com", "dealroom.co"]):
                    if u not in urls:
                        urls.append(u)
                if len(urls) >= limit:
                    break
            return urls

        except Exception as e:
            logger.error("FundingDiscovery Tavily error: %s", e)
            return []

    async def discover(self, project_name: str, github_repos: List[str] | None = None, limit: int = 10) -> List[str]:
        """
        Perform multi-source funding discovery:
        - Tavily (for company/investor profiles)
        - GitHub FUNDING.yml (if repos provided)
        Returns: List[str] of URLs
        """
        logger.info(f"🔎 Starting FundingDiscovery for '{project_name}'")

        tavily_task = asyncio.create_task(self._tavily_funding_search(project_name, limit=limit))
        github_funding_tasks = []

        if github_repos:
            for repo_url in github_repos[:3]:  # limit to top 3 repos for rate safety
                if "github.com" in repo_url:
                    full_name = repo_url.replace("https://github.com/", "").strip("/")
                    github_funding_tasks.append(
                        asyncio.create_task(self._fetch_github_funding(full_name))
                    )

        github_results = await asyncio.gather(*github_funding_tasks, return_exceptions=True)
        tavily_urls = await tavily_task

        # Flatten and merge
        github_urls = []
        for g in github_results:
            if isinstance(g, list):
                github_urls.extend(g)

        all_urls = list({*tavily_urls, *github_urls})[:limit]

        logger.info("💰 FundingDiscovery complete for %s → %d total URLs", project_name, len(all_urls))
        return all_urls