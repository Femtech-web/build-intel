import asyncio
import logging
from typing import Dict

from .github_discovery import GitHubDiscovery
from .funding_discovery import FundingDiscovery
from .website_discovery import WebsiteDiscovery
from .twitter_discovery import TwitterDiscovery
from .utils import refine_discovery

logger = logging.getLogger(__name__)


class DiscoveryProvider:
    """Orchestrates all discovery modules for maximum discovery accuracy."""

    def __init__(self):
        self.github = GitHubDiscovery()
        self.funding = FundingDiscovery()
        self.website = WebsiteDiscovery()
        self.twitter = TwitterDiscovery()

    async def discover_project(self, project_name: str) -> Dict[str, list]:
        """Runs all discoverers concurrently and merges results with high accuracy."""
        logger.info("🚀 Starting discovery for project: %s", project_name)

        # Run all discovery modules concurrently
        github_task = asyncio.create_task(self.github.discover(project_name))
        funding_task = asyncio.create_task(self.funding.discover(project_name))
        website_task = asyncio.create_task(self.website.discover(project_name))
        twitter_task = asyncio.create_task(self.twitter.discover(project_name))

        githubs, fundings, website_data, twitters = await asyncio.gather(
            github_task, funding_task, website_task, twitter_task
        )

        websites = website_data.get("websites", [])
        others = website_data.get("others", [])

        # Deduplicate globally
        def unique(seq):
            seen = set()
            out = []
            for x in seq:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        result = {
            "websites": unique(websites),
            "githubs": unique(githubs),
            "fundings": unique(fundings),
            "twitters": unique(twitters),
            "others": unique(others),
        }

        result = refine_discovery(result)

        logger.info(
            "✅ Discovery completed for %s → %s websites, %s githubs, %s fundings, %s twitters, %s others",
            project_name,
            len(result["websites"]),
            len(result["githubs"]),
            len(result["fundings"]),
            len(result["twitters"]),
            len(result["others"]),
        )
        return result
