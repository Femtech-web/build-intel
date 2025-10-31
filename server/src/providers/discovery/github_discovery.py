import os
import httpx # type: ignore
import logging
from typing import List

logger = logging.getLogger(__name__)

GITHUB_API = os.getenv("GITHUB_API_URL", "https://api.github.com") 

class GitHubDiscovery:
    """High-accuracy GitHub repo discovery for a given project name."""

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN missing or not configured")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def discover(self, project_name: str, limit: int = 8) -> List[str]:
        """Return filtered repo URLs highly relevant to project_name."""
        q = f"{project_name} in:name"  # tighter search
        params = {"q": q, "sort": "stars", "order": "desc", "per_page": str(limit * 2)}

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{GITHUB_API}/search/repositories", headers=self.headers, params=params)
            r.raise_for_status()
            results = r.json().get("items", [])

        clean_urls = []
        project_lower = project_name.lower()

        for repo in results:
          _full_name = repo["full_name"].lower()
          owner = repo["owner"]["login"].lower()
          name = repo["name"].lower()
          topics = [t.lower() for t in repo.get("topics", [])]
          description = (repo.get("description") or "").lower()

          if (
              owner == project_lower
              or project_lower in owner
              or name == project_lower
              or name.startswith(project_lower)
              or project_lower in topics
              or project_lower in description
          ):
              clean_urls.append(repo["html_url"])


        # Deduplicate and limit
        return list(dict.fromkeys(clean_urls))[:limit]
