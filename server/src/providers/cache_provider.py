import time
import logging
import json
import os
from redis import asyncio as aioredis # type: ignore

logger = logging.getLogger(__name__)

class CacheProvider:
    """
    Redis-backed async cache provider with metadata sync.
    Each cached entry includes _meta info:
        {
            "_meta": {
                "expires": <unix timestamp>,
                "ttl": <seconds>
            },
            ... actual cached data ...
        }

    Falls back to in-memory cache if Redis is unavailable.
    """

    def __init__(self, redis_url: str = os.getenv("REDIS_URL"), default_ttl: int = 3600):
        self._cache = {}
        self.default_ttl = default_ttl
        self.redis_url = redis_url
        self._redis = None

    # ─────────────────────────────
    # Initialization
    # ─────────────────────────────
    async def connect(self):
        """Connect to Redis if available."""
        try:
            self._redis = await aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            logger.info("✅ Connected to Redis cache at %s", self.redis_url)
        except Exception as e:
            logger.warning("⚠️ Redis unavailable, using in-memory cache only: %s", e)
            self._redis = None

    # ─────────────────────────────
    # Get / Set
    # ─────────────────────────────
    async def get(self, key: str):
        """Get cached value (tries Redis first, then in-memory)."""
        # Try Redis
        if self._redis:
            try:
                value = await self._redis.get(key)
                if value:
                    data = json.loads(value)
                    # Sync TTL metadata if Redis supports TTL
                    ttl = await self._redis.ttl(key)
                    if ttl and "_meta" in data:
                        data["_meta"]["ttl"] = ttl
                        data["_meta"]["expires"] = time.time() + ttl
                    return data
            except Exception as e:
                logger.warning("Redis get failed (%s), falling back to memory.", e)

        # Fallback to in-memory
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry["expires"]:
            del self._cache[key]
            return None
        return entry["value"]

    async def set(self, key: str, value, ttl: int = None):
        """Set a cached value with metadata."""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl

        # Attach metadata to the stored object
        if isinstance(value, dict):
            value["_meta"] = {"expires": expires_at, "ttl": ttl}
        else:
            value = {"value": value, "_meta": {"expires": expires_at, "ttl": ttl}}

        # Try Redis
        if self._redis:
            try:
                await self._redis.setex(key, ttl, json.dumps(value))
                return
            except Exception as e:
                logger.warning("Redis set failed (%s), falling back to memory.", e)

        # Fallback to in-memory cache
        self._cache[key] = {"value": value, "expires": expires_at}

    # ─────────────────────────────
    # Maintenance
    # ─────────────────────────────
    async def delete(self, key: str):
        """Delete a cached key from Redis and memory."""
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception as e:
                logger.warning("Redis delete failed (%s).", e)
        self._cache.pop(key, None)

    async def close(self):
        """Gracefully close Redis connection."""
        if self._redis:
            await self._redis.close()
