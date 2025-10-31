import os
import httpx # type: ignore
import logging
import asyncio
import random
import time
from urllib.parse import urlparse
from .cache_provider import CacheProvider
import re

logger = logging.getLogger(__name__)

SERP_API_URL = os.getenv("SERP_BASE_URL", "https://serpapi.com/search.json")
TWITTER_API_URL = os.getenv("TWITTER_API_URL", "https://api.x.com/2/users/by/username/{}") 
TWITTER_BASE_URL = os.getenv("TWITTER_BASE_URL", "https://x.com")
TAVILY_API_URL = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com/search")
DUCKDUCKGO_API_URL = os.getenv("DUCKDUCKGO_API_URL", "https://duckduckgo.com/html/")
TWITTER_USER_FIELDS = "description,public_metrics,profile_image_url"


class TwitterProvider:
    """Fetch Twitter profile data with caching, retry, fallback, and auto-refresh."""

    def __init__(self, refresh_threshold=0.9, max_fetch_attempts=3, cooldown_seconds=3600):
        self.cache = CacheProvider()
        self.twitter_bearer = os.getenv("TWITTER_BEARER_TOKEN")
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.timeout = 20.0
        self.refresh_threshold = refresh_threshold  
        self.max_fetch_attempts = max_fetch_attempts
        self.cooldown_seconds = cooldown_seconds

    async def initialize(self):
        """Ensure cache provider is connected to Redis."""
        await self.cache.connect()

    # ─────────────────────────────
    # Retry + rate limit guard
    # ─────────────────────────────
    async def _should_refetch(self, username: str) -> bool:
        """Decide whether to allow a new fetch for this username."""
        key = f"twitter:fetch_attempts:{username.lower()}"
        data = await self.cache.get(key)
        if not data:
            return True  # No prior failures

        attempts = data.get("attempts", 0)
        last_attempt = data.get("last_attempt", 0)
        now = time.time()

        if attempts >= self.max_fetch_attempts and (now - last_attempt) < self.cooldown_seconds:
            logger.warning(f"🚫 Skipping @{username} (max fetch attempts reached, cooling down).")
            return False

        return True

    async def _record_failed_fetch(self, username: str):
        """Increment failure count for a username."""
        key = f"twitter:fetch_attempts:{username.lower()}"
        data = await self.cache.get(key) or {"attempts": 0, "last_attempt": 0}
        data["attempts"] += 1
        data["last_attempt"] = time.time()
        await self.cache.set(key, data, ttl=self.cooldown_seconds)

    async def _reset_fetch_attempts(self, username: str):
        """Reset failure tracker after success."""
        key = f"twitter:fetch_attempts:{username.lower()}"
        await self.cache.set(key, {"attempts": 0, "last_attempt": time.time()}, ttl=self.cooldown_seconds)


    # ─────────────────────────────
    # Internal utilities
    # ─────────────────────────────
    async def _safe_get(self, client, url, headers=None, params=None, retries=1, base_delay=2):
        """Retry GET with exponential backoff + jitter for 429/5xx"""
        for i in range(retries):
            try:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code in (200, 404):
                    return resp

                if resp.status_code in (429,) or resp.status_code >= 500:
                    wait = base_delay * (2 ** i) + random.uniform(0, 1)
                    logger.warning(f"⚠️ {resp.status_code} from {url}, retrying in {wait:.1f}s…")
                    await asyncio.sleep(wait)
                    continue

                return resp
            except Exception as e:
                logger.error(f"❌ HTTP GET failed: {e}")
                await asyncio.sleep(base_delay)
        return None


    # ─────────────────────────────
    # Public main methods
    # ─────────────────────────────
    async def get_twitter_stats(self, twitter_urls, force_refresh: bool = False):
        """
        Fetch Twitter profile data for one or multiple URLs.
        Auto-refreshes cache if data is stale.
        """
        if not twitter_urls:
            logger.warning("⚠️ No Twitter URLs provided.")
            return None
        if isinstance(twitter_urls, str):
            twitter_urls = [twitter_urls]

        results = []
        now = time.time()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for url in twitter_urls:
                username = urlparse(url).path.strip("/")
                if not username:
                    continue

                cache_key = f"twitter:{username.lower()}"
                cached = None if force_refresh else await self.cache.get(cache_key)

                # ── Cache hit
                if cached:
                    results.append(cached)
                    logger.info(f"💾 Cache hit for @{username}")

                    # Auto-refresh if cache is nearing expiry (background task)
                    expires_at = cached.get("_meta", {}).get("expires")
                    if expires_at and now > expires_at * self.refresh_threshold:
                        asyncio.create_task(self._auto_refresh(username))
                    continue

                # ── No cache, fetch live
                data = await self._fetch_live_data(client, username)
                if data:
                    await self.cache.set(cache_key, data, ttl=6 * 3600)
                    results.append(data)

        if not results:
            logger.warning("⚠️ No Twitter data fetched.")
            return None

        logger.info(f"✅ Retrieved Twitter data for {len(results)} profiles.")
        return results

    async def refresh_cache(self, username: str):
        """Manually refresh cache for a username."""
        username = username.strip("@")
        cache_key = f"twitter:{username.lower()}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = await self._fetch_live_data(client, username)
            if data:
                await self.cache.set(cache_key, data, ttl=6 * 3600)
                logger.info(f"🔄 Cache manually refreshed for @{username}")
                return data

            logger.warning(f"⚠️ Could not refresh cache for @{username}")
            return None

    # ─────────────────────────────
    # Internal helpers
    # ─────────────────────────────
    async def _auto_refresh(self, username):
        """Background task to refresh near-expired cache entries."""
        try:
            logger.info(f"🕐 Auto-refreshing cache for @{username} …")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = await self._fetch_live_data(client, username)
                if data:
                    await self.cache.set(f"twitter:{username.lower()}", data, ttl=6 * 3600)
                    logger.info(f"✅ Auto-refresh completed for @{username}")
        except Exception as e:
            logger.warning(f"⚠️ Auto-refresh failed for @{username}: {e}")

    @staticmethod
    def _parse_metric(text: str, pattern: str):
        """Extracts numeric-like text and normalizes (e.g., '182.2K' → 182200)."""
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None

        raw = match.group(1).replace(",", "")
        multiplier = 1
        if raw.lower().endswith("k"):
            multiplier = 1_000
            raw = raw[:-1]
        elif raw.lower().endswith("m"):
            multiplier = 1_000_000
            raw = raw[:-1]

        try:
            return int(float(raw) * multiplier)
        except ValueError:
            return None

    async def _fetch_live_data(self, client, username):
        """Try Twitter API, then fallbacks."""
        if not await self._should_refetch(username):
            return None

        data = (
            await self._fetch_twitter_profile(client, username)
            or await self._fetch_via_tavily(client, username)
            or await self._fetch_via_serpapi(client, username)
            or await self._fetch_via_duckduckgo(client, username)
        )

        if data:
            await self._reset_fetch_attempts(username)
            data["_meta"] = {"expires": time.time() + 6 * 3600}
        else:
            await self._record_failed_fetch(username)

        return data

    async def _fetch_twitter_profile(self, client, username):
        """Primary: Twitter API v2."""
        if not self.twitter_bearer:
            logger.debug("No TWITTER_BEARER_TOKEN configured.")
            return None

        url = TWITTER_API_URL.format(username)
        headers = {"Authorization": f"Bearer {self.twitter_bearer}"}
        params = {"user.fields": TWITTER_USER_FIELDS}

        resp = await self._safe_get(client, url, headers=headers, params=params)
        if not resp or resp.status_code != 200:
            logger.warning(f"⚠️ Twitter API failed for @{username} ({resp.status_code if resp else 'no resp'})")
            return None

        try:
            data = resp.json().get("data", {})
            metrics = data.get("public_metrics", {})
            return {
                "username": data.get("username"),
                "bio": data.get("description"),
                "followers": metrics.get("followers_count"),
                "following": metrics.get("following_count"),
                "tweets": metrics.get("tweet_count"),
                "profile_image": data.get("profile_image_url"),
                "verified": data.get("verified", False),  
                "verified_type": data.get("verified_type"), 
                "source": "twitter-api",
            }
        except Exception as e:
            logger.error(f"❌ Failed parsing Twitter API response for @{username}: {e}")
            return None

    # ----------------------------
    # fallbacks
    # ----------------------------

    async def _fetch_via_serpapi(self, client, username):
        """Fetch basic X/Twitter profile info using SerpAPI (Google engine only)."""
        if not self.serp_api_key:
            logger.debug("No SERPAPI_KEY configured.")
            return None

        params = {
            "engine": "google",
            "q": f"site:x.com OR site:twitter.com @{username}",
            "api_key": self.serp_api_key,
            "num": 3,
        }

        resp = await self._safe_get(client, SERP_API_URL, params=params)

        if not resp or resp.status_code != 200:
            logger.warning(f"⚠️ SerpAPI Google search failed for @{username}")
            return None

        logger.warning(f"SERPAPI (google engine) raw response for @{username}: {resp.text[:400]}")

        try:
            data = resp.json()
            snippet = next(
                (r for r in data.get("organic_results", []) if "x.com/" in r.get("link", "")), None
            )
            if not snippet:
                return None

            return {
                "username": username,
                "bio": snippet.get("snippet", "")[:280],
                "profile_url": snippet.get("link"),
                "source": "serpapi-google",
            }

        except Exception as e:
            logger.error(f"❌ Failed parsing SerpAPI Google response for @{username}: {e}")
            return None


    async def _fetch_via_tavily(self, client, username):
        """Fallback: Tavily search for Twitter/X profile data (with light metric parsing)."""
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            logger.debug("No TAVILY_API_KEY configured.")
            return None

        try:
            payload = {
                "api_key": tavily_key,
                "query": f"Twitter profile @{username} site:x.com OR site:twitter.com",
                "max_results": 5,
            }
            resp = await client.post(TAVILY_API_URL, json=payload)
            if resp.status_code != 200:
                logger.warning(f"⚠️ Tavily fallback failed for @{username} ({resp.status_code})")
                return None

            data = resp.json()
            result = next(
                (r for r in data.get("results", []) if "x.com/" in r.get("url", "")), None
            )
            if not result:
                logger.info(f"ℹ️ Tavily returned no X.com results for @{username}")
                return None

            content = result.get("content", "") or ""

            # ── Try to extract numeric metrics from text like "182.2K Followers · 300 Following · 12K Posts"
            followers = self._parse_metric(content, r"([\d,.KkMm]+)\s*Followers")
            following = self._parse_metric(content, r"([\d,.KkMm]+)\s*Following")
            tweets = self._parse_metric(content, r"([\d,.KkMm]+)\s*(Tweets|Posts)")

            return {
                "username": username,
                "bio": content[:300],
                "profile_url": result.get("url"),
                "followers": followers,
                "following": following,
                "tweets": tweets,
                "source": "tavily",
            }

        except Exception as e:
            logger.error(f"❌ Tavily fallback error for @{username}: {e}")
            return None
        

    async def _fetch_via_duckduckgo(self, client, username):
        """Last-resort fallback: DuckDuckGo HTML scrape (no key)."""
        try:
            q = f"site:twitter.com @{username}"
            url = f"{DUCKDUCKGO_API_URL}?q={q}"
            resp = await client.get(url)
            if resp.status_code != 200:
                return None

            html = resp.text
            import re
            match = re.search(r"https://x\.com/([A-Za-z0-9_]+)", html)
            if not match:
                return None

            return {
                "username": username,
                "bio": "Fetched via DuckDuckGo search (limited details)",
                "profile_url": f"{TWITTER_BASE_URL}/{username}",
                "source": "duckduckgo",
            }
        except Exception as e:
            logger.error(f"❌ DuckDuckGo fallback failed for @{username}: {e}")
            return None




