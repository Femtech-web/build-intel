
import os
import logging
import httpx # type: ignore
from typing import List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SERPAPI_URL = os.getenv("SERP_BASE_URL", "https://serpapi.com/search.json")
TAVILY_SEARCH_URL = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com/search")


def _normalize_twitter_url(u: str) -> str | None:
    """Normalize various twitter/x URL shapes to canonical https://twitter.com/<handle> or https://x.com/<handle>"""
    if not u:
        return None
    u = u.split("?")[0].rstrip("/")
    parsed = urlparse(u)
    netloc = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if not path:
        return None
    # Accept twitter.com or x.com (also mobile.twitter.com)
    if "twitter.com" in netloc or "x.com" in netloc:
        handle = path.split("/")[0]
        scheme = "https"
        domain = "x.com" if "x.com" in netloc else "twitter.com"
        return f"{scheme}://{domain}/{handle}"

    if u.startswith("@"):
        return f"https://twitter.com/{u.lstrip('@')}"

    if "/" not in u and " " not in u and len(u) <= 50:
        return f"https://twitter.com/{u}"
    return None

def _score_twitter_url(project_name: str, url: str) -> int:
    """Score likely relevance of a Twitter/X URL"""
    u = url.lower()
    score = 0
    if f"/{project_name.lower()}" in u:
        score += 10
    if "official" in u:
        score += 5
    if u.endswith(f"/{project_name.lower()}"):
        score += 10
    if any(k in u for k in ("support", "team", "labs", "protocol")):
        score += 3
    return score


async def _head_ok(client: httpx.AsyncClient, url: str) -> bool:
    try:
        r = await client.head(url, follow_redirects=True, timeout=6.0)
        return r.status_code < 400
    except Exception:
        return False


class TwitterDiscovery:
    """
    Discover Twitter / X profile URLs for a project name.

    Strategy:
    1) Try SerpAPI 'twitter' engine (best structured results) if SERPAPI_KEY provided.
    2) Fallback to Tavily search for twitter/x links if TAVILY_API_KEY provided.
    3) If both available, also try SerpAPI 'google' site:twitter.com search.
    4) Normalize, validate with HEAD checks, dedupe and return up to `limit` urls.
    """

    def __init__(self):
        self.serp_key = os.getenv("SERPAPI_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

    async def _serpapi_twitter_search(self, project_name: str, limit: int = 6) -> List[str]:
        if not self.serp_key:
            return []

        params = {
            "engine": "X",
            "q": project_name,
            "api_key": self.serp_key,
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(SERPAPI_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.debug("SerpAPI twitter search failed: %s", e)
            return []

        urls = []
        twitter_results = data.get("twitter_results") or {}
        profile = twitter_results.get("profile")
        if profile:
            canonical = profile.get("profile_url") or profile.get("username") or profile.get("permalink")
            if canonical:
                norm = _normalize_twitter_url(canonical)
                if norm:
                    urls.append(norm)
        # check for items in 'users' or 'data' or 'organic_results'
        for key in ("users", "data", "organic_results", "timeline"):
            items = twitter_results.get(key) or data.get(key) or []
            if isinstance(items, dict):
                items = [items]
            for it in items:
                if not it:
                    continue

                candidate = it.get("profile_url") or it.get("url") or it.get("permalink") or it.get("username")
                if candidate:
                    norm = _normalize_twitter_url(candidate)
                    if norm and norm not in urls:
                        urls.append(norm)

                uname = it.get("username") or it.get("screen_name")
                if uname:
                    norm = _normalize_twitter_url(uname)
                    if norm and norm not in urls:
                        urls.append(norm)
      
        return urls[:limit]

    async def _serpapi_google_site_search(self, project_name: str, limit: int = 6) -> List[str]:
        """Use SerpAPI's google engine to search site:twitter.com for the project"""
        if not self.serp_key:
            return []
        q = f'{project_name} site:x.com "official" OR "official account"'
        params = {"engine": "google", "q": q, "api_key": self.serp_key, "num": limit}
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(SERPAPI_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.debug("SerpAPI google site search failed: %s", e)
            return []

        urls = []
        for item in data.get("organic_results", []) + data.get("top_results", []):
            u = item.get("link") or item.get("url")
            norm = _normalize_twitter_url(u)
            if norm and norm not in urls:
                urls.append(norm)
            if len(urls) >= limit:
                break
        return urls[:limit]

    async def _tavily_search_for_twitter(self, project_name: str, limit: int = 8) -> List[str]:
        if not self.tavily_key:
            return []
        payload = {
            "api_key": self.tavily_key,
            "query": f'{project_name} official X site:x.com',
            "num_results": 12,
        }
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(TAVILY_SEARCH_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.debug("Tavily twitter search failed: %s", e)
            return []

        urls = []
        for r in data.get("results", []):
            u = r.get("url")
            norm = _normalize_twitter_url(u)
            if norm and norm not in urls:
                urls.append(norm)
            if len(urls) >= limit:
                break
        return urls

    async def discover(self, project_name: str, limit: int = 6) -> List[str]:
        """Discover likely Twitter/X profile URLs for a project name."""
        logger.info("TwitterDiscovery: searching for %s", project_name)
        candidates: List[str] = []

        # SerpAPI twitter engine (best structured if available)
        if self.serp_key:
            try:
                serp_urls = await self._serpapi_twitter_search(project_name, limit=limit)
                logger.info("TwitterDiscovery: SerpAPI twitter found %d", len(serp_urls))
                candidates.extend(serp_urls)
            except Exception as e:
                logger.debug("TwitterDiscovery SerpAPI twitter step failed: %s", e)

        # Tavily fallback to find twitter links
        if len(candidates) < limit and self.tavily_key:
            try:
                tavily_urls = await self._tavily_search_for_twitter(project_name, limit=limit)
                logger.info("TwitterDiscovery: Tavily found %d", len(tavily_urls))
                for u in tavily_urls:
                    if u not in candidates:
                        candidates.append(u)
            except Exception as e:
                logger.debug("TwitterDiscovery Tavily step failed: %s", e)

        # SerpAPI google site:twitter search as extra fallback (if serp key present)
        if len(candidates) < limit and self.serp_key:
            try:
                google_urls = await self._serpapi_google_site_search(project_name, limit=limit)
                logger.info("TwitterDiscovery: SerpAPI google-site found %d", len(google_urls))
                for u in google_urls:
                    if u not in candidates:
                        candidates.append(u)
            except Exception as e:
                logger.debug("TwitterDiscovery SerpAPI google step failed: %s", e)

        # Normalize/dedupe
        unique = []
        for u in candidates:
            if not u:
                continue
            norm = _normalize_twitter_url(u)
            if norm and norm not in unique:
                unique.append(norm)

        # Validate candidates with HEAD checks (cheap)
        validated = []
        async with httpx.AsyncClient(timeout=8.0) as client:
            for u in unique:
                ok = await _head_ok(client, u)
                if ok:
                    validated.append(u)
                else:
                    logger.debug("TwitterDiscovery: HEAD check failed for %s", u)

        final = validated or unique  
        logger.info("TwitterDiscovery: returning %d profile(s) for %s", len(final[:limit]), project_name)

        scored = sorted(final, key=lambda u: _score_twitter_url(project_name, u), reverse=True)
        return scored[:limit]
