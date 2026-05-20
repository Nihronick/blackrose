import asyncio
import json
import logging
import time
from typing import Any
import redis.asyncio as aioredis
from core.config import settings

logger = logging.getLogger("blackrose.services.cache")

class RedisCacheService:
    def __init__(self):
        self._redis: Any = None
        self._disabled_until: float = 0
        self._lock = asyncio.Lock()
        self.ttl_cats = int(settings.INIT_DATA_MAX_AGE / 1440) # 60s default approx
        self.ttl_guide = 120
        self.prefix_cats = "br:cats"
        self.prefix_guide = "br:guide:"

    async def get_client(self):
        if self._disabled_until > time.time():
            return None
        if self._redis:
            return self._redis

        url = settings.REDIS_URL
        if not url:
            return None

        async with self._lock:
            if self._redis:
                return self._redis
            try:
                self._redis = aioredis.from_url(url, decode_responses=True, socket_timeout=1)
                await self._redis.ping()
                return self._redis
            except Exception as e:
                if "limit exceeded" in str(e).lower():
                    self._disabled_until = time.time() + 300
                self._redis = None
                return None

    async def get(self, key: str) -> Any | None:
        r = await self.get_client()
        if not r:
            return None
        try:
            raw = await r.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.error(f"Redis GET error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 300):
        r = await self.get_client()
        if not r:
            return
        try:
            await r.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis SET error for {key}: {e}")

    async def delete(self, key: str):
        r = await self.get_client()
        if not r:
            return
        try:
            await r.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error for {key}: {e}")

    async def get_categories(self) -> dict | None:
        r = await self.get_client()
        if not r:
            return None
        try:
            raw = await r.get(self.prefix_cats)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    async def set_categories(self, data: dict):
        r = await self.get_client()
        if not r:
            return
        try:
            await r.setex(self.prefix_cats, self.ttl_cats, json.dumps(data))
        except Exception:
            pass

    async def ping(self) -> dict:
        r = await self.get_client()
        if not r:
            return {"status": "disabled/missing"}
        import time
        start = time.perf_counter()
        try:
            await r.ping()
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {"status": "healthy", "latency_ms": latency}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def invalidate_guide(self, key: str):
        r = await self.get_client()
        if not r:
            return
        try:
            await r.delete(f"{self.prefix_guide}{key}")
            keys = await r.keys(f"cache:*/guide/{key}*")
            if keys:
                await r.delete(*keys)
        except Exception:
            pass

    async def invalidate_all(self):
        r = await self.get_client()
        if not r:
            return
        try:
            # We use keys with prefix to avoid clearing other data if shared
            keys = await r.keys(f"{self.prefix_cats}*")
            if keys:
                await r.delete(*keys)
            keys = await r.keys(f"{self.prefix_guide}*")
            if keys:
                await r.delete(*keys)
            
            # Clear API cached responses
            api_keys = await r.keys("cache:*")
            if api_keys:
                await r.delete(*api_keys)
        except Exception:
            pass

    async def close(self):
        if self._redis:
            await self._redis.aclose()
            self._redis = None

async def close_redis():
    await cache_service.close()

cache_service = RedisCacheService()
