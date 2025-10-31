import os
import logging
import httpx # type: ignore
import re
from typing import List, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Crypto/web project–common TLDs
PREFERRED_TLDS = [
    ".co", ".com", ".org", ".io", ".app", ".ai", ".net", ".xyz",
    ".dev", ".tech", ".studio", ".systems", ".space", ".network",
    ".cloud", ".tools", ".so", ".sh", ".gg", ".build",
    ".eth", ".crypto", ".nft", ".dao", ".chain", ".sol", ".bnb"
]
DISALLOWED_DOMAINS = [
    "bulbapedia", "pokemon", "tradingview", "deloitte", "linkedin", "medium",
    "wikipedia", "youtube", "reddit", "facebook", "bloomberg", "forbes"
]

class WebsiteDiscovery:
    """Find and rank official websites and docs for a project."""

    def __init__(self, tavily_key: str | None = None):
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY")

    def _extract_domain(self, url: str) -> str:
        try:
            domain = urlparse(url).netloc.lower()
            # remove www.
            return domain[4:] if domain.startswith("www.") else domain
        except Exception:
            return ""

    def _score_url(self, project_name: str, url: str) -> int:
        """Assign a relevance score to each URL."""
        low = url.lower()
        domain = self._extract_domain(url)
        score = 0

        # Direct domain match boost (e.g. zora.co)
        if project_name.lower() in domain:
            score += 10

        # Preferred TLD boost
        if any(domain.endswith(tld) for tld in PREFERRED_TLDS):
            score += 3

        # Penalize bad/irrelevant sources
        if any(bad in low for bad in DISALLOWED_DOMAINS):
            score -= 20

        # Boost URLs containing "app", "docs", "www", etc. (subdomains of same org)
        if re.search(rf"(app|docs|portal)\.{project_name.lower()}", domain):
            score += 5

        # Title hints
        if "official" in low:
            score += 5

        return score

    async def discover(self, project_name: str, limit: int = 6) -> Dict[str, List[str]]:
        results = {"websites": [], "others": []}
        if not self.tavily_key:
            logger.warning("WebsiteDiscovery: TAVILY_API_KEY not configured; skipping discovery")
            return results

        q = (
            f'"{project_name}" official website OR homepage OR documentation '
            f'-site:github.com -site:twitter.com -site:crunchbase.com -site:medium.com'
        )
        payload = {"api_key": self.tavily_key, "query": q, "num_results": 25}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(TAVILY_SEARCH_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()

            raw_urls = [r.get("url") for r in data.get("results", []) if r.get("url")]
            scored = []
            for u in raw_urls:
                if not u or not u.startswith("http"):
                    continue
                s = self._score_url(project_name, u)
                scored.append((u, s))

            # Sort by score (descending) + dedup
            scored.sort(key=lambda x: x[1], reverse=True)
            seen = set()
            ranked = []
            for u, s in scored:
                domain = self._extract_domain(u)
                if domain not in seen:
                    seen.add(domain)
                    ranked.append(u)

            # Optional HEAD validation
            validated = []
            async with httpx.AsyncClient(timeout=6.0) as client:
                for u in ranked[:10]:
                    try:
                        r = await client.head(u, follow_redirects=True)
                        if r.status_code < 400:
                            validated.append(u)
                    except Exception:
                        continue

            # Classify top results
            for u in validated[:limit]:
                domain = self._extract_domain(u)
                if project_name.lower() in domain:
                    results["websites"].append(u)
                else:
                    results["others"].append(u)

            logger.info("🌐 WebsiteDiscovery found %d websites for %s", len(results["websites"]), project_name)
            return results

        except Exception as e:
            logger.error("WebsiteDiscovery error: %s", e)
            return results
