import logging
import json
import httpx # type: ignore
import os
from typing import Any, Dict, Optional

from src.providers.cache_provider import CacheProvider
from src.providers.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class FundingProvider:
    """Aggregates and interprets funding data for a given project."""

    def __init__(self):
        self.llm = LLMProvider()
        self.cache = CacheProvider()
        self.serpapi_key = os.getenv("SERPAPI_KEY")

    async def get_funding_info(self, project_name: str, funding_urls: list[str]) -> Dict[str, Any]:
        """Main orchestration method for funding discovery and synthesis."""
        cache_key = f"funding:{project_name.lower()}"
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"♻️ Using cached funding info for {project_name}")
            return json.loads(cached)

        logger.info(f"💰 Aggregating funding info for {project_name}")

        # 1️⃣ Gather raw data from all sources
        defillama_data = await self._try_defillama(project_name)
        coingecko_data = await self._try_coingecko(project_name)
        serpapi_data = await self._try_serpapi(project_name) if self.serpapi_key else None

        raw_sources = {
            "defillama": defillama_data,
            "coingecko": coingecko_data,
            "serpapi": serpapi_data,
        }

        # Filter out None
        raw_sources = {k: v for k, v in raw_sources.items() if v}

        # 2️⃣ Let LLM synthesize a clean JSON summary
        summary = await self.llm.extract_funding_details(project_name, raw_sources)

        result = {
            "project": project_name,
            "funding_sources": funding_urls,
            "raw_data": raw_sources,
            "funding_details": summary,
        }

        # 3️⃣ Cache for 24 hours
        await self.cache.set(cache_key, json.dumps(result), ttl=86400)
        logger.info(f"✅ Funding aggregation complete for {project_name}")

        return result

    # ----------------------------
    # Individual Data Sources
    # ----------------------------

    async def _get_defillama_protocols(self) -> list[Dict[str, Any]]:
        """Fetch and cache the full DeFiLlama protocol index (24h)."""
        cache_key = "defillama:protocols"
        cached = await self.cache.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass  # ignore malformed cache

        url = "https://api.llama.fi/protocols"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    protocols = resp.json()
                    await self.cache.set(cache_key, json.dumps(protocols), ttl=86400)
                    logger.info(f"📥 Cached {len(protocols)} DeFiLlama protocols list")
                    return protocols
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch DeFiLlama protocols list: {e}")

        return []  # fallback empty list


    async def _try_defillama(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Fetch funding info from DeFiLlama API with fuzzy slug matching."""
        try:
            project_key = project_name.lower().strip()
            protocols = await self._get_defillama_protocols()

            if not protocols:
                logger.warning("⚠️ Empty DeFiLlama protocols list — skipping")
                return None

            logger.debug(f"🔍 Searching {len(protocols)} DeFiLlama protocols for '{project_key}'")

            # Safe fuzzy match
            match = next(
                (
                    p for p in protocols
                    if project_key in str(p.get("name", "")).lower()
                    or project_key in str(p.get("slug", "")).lower()
                ),
                None,
            )

            if not match:
                logger.info(f"⚠️ No DeFiLlama slug match found for {project_name}")
                return None

            slug = match.get("slug")
            if not slug:
                logger.warning(f"⚠️ Matched entry has no slug for {project_name}")
                return None

            url = f"https://api.llama.fi/protocol/{slug}"
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
                resp = await client.get(url)
                logger.info(f"🌐 DeFiLlama lookup for {url} → {resp.status_code}")

                if resp.status_code != 200:
                    logger.warning(f"⚠️ DeFiLlama returned {resp.status_code} for {slug}")
                    return None

                data = resp.json()
                logger.info(f"✅ Fetched DeFiLlama data for {data.get('name', slug)}")

                return {
                    "source": "defillama",
                    "name": data.get("name"),
                    "slug": data.get("slug"),
                    "category": data.get("category"),
                    "chains": data.get("chains"),
                    "mcap": data.get("mcap"),
                    "funding": data.get("funding", {}),
                    "url": url,
                }

        except Exception as e:
            import traceback
            logger.warning(f"⚠️ DeFiLlama lookup failed for {project_name}: {e}\n{traceback.format_exc()}")
            return None



    async def _try_coingecko(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Fetch funding/market info from CoinGecko API (trimmed version)."""
        try:
            search_url = f"https://api.coingecko.com/api/v3/search?query={project_name}"
            async with httpx.AsyncClient(timeout=10) as client:
                search_resp = await client.get(search_url)
                if search_resp.status_code != 200:
                    return None

                results = search_resp.json().get("coins", [])
                if not results:
                    return None

                coin_id = results[0]["id"]
                detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                detail_resp = await client.get(detail_url)
                if detail_resp.status_code != 200:
                    return None

                detail = detail_resp.json()

                market_data = detail.get("market_data", {})
                return {
                    "source": "coingecko",
                    "id": coin_id,
                    "symbol": detail.get("symbol"),
                    "name": detail.get("name"),
                    "description": (detail.get("description", {}) or {}).get("en", "")[:400],
                    "market": {
                        "current_price_usd": market_data.get("current_price", {}).get("usd"),
                        "market_cap_usd": market_data.get("market_cap", {}).get("usd"),
                        "total_volume_usd": market_data.get("total_volume", {}).get("usd"),
                        "price_change_24h": market_data.get("price_change_percentage_24h"),
                    },
                    "links": {
                        "homepage": (detail.get("links", {}).get("homepage") or [None])[0],
                        "twitter": detail.get("links", {}).get("twitter_screen_name"),
                        "repos": detail.get("links", {}).get("repos_url", {}).get("github", []),
                    },
                }
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko lookup failed for {project_name}: {e}")
            return None


    async def _try_serpapi(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Fallback search using SerpAPI for funding announcements."""
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google",
                "q": f"{project_name} funding site:crunchbase.com OR site:techcrunch.com OR site:cointelegraph.com",
                "api_key": self.serpapi_key,
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                results = data.get("organic_results", [])
                return {
                    "source": "serpapi",
                    "results": [
                        {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
                        for r in results[:5]
                    ],
                }
        except Exception as e:
            logger.warning(f"⚠️ SerpAPI lookup failed for {project_name}: {e}")
            return None