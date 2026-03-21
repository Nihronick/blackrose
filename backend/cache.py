"""
Redis cache layer for BlackRose.

Используется вместо in-process dict кеша — работает при scale-out
(несколько инстансов Railway) и не теряет данные при рестарте.

Если REDIS_URL не задан — автоматически падает обратно на no-op кеш
(полезно для локальной разработки без Redis).
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger("blackrose.cache")

# TTL в секундах
TTL_CATEGORIES = int(os.getenv("CACHE_TTL_CATEGORIES", 60))
TTL_GUIDE = int(os.getenv("CACHE_TTL_GUIDE", 120))

# Префиксы ключей
_PREFIX_CATS = "br:cats"
_PREFIX_GUIDE = "br:guide:"

_redis: Any = None  # redis.asyncio.Redis | None


async def get_redis():
    """Возвращает Redis клиент или None если REDIS_URL не задан."""
    global _redis
    if _redis is not None:
        return _redis

    url = os.getenv("REDIS_URL", "")
    if not url:
        return None

    try:
        import redis.asyncio as aioredis

        _redis = aioredis.from_url(url, decode_responses=True, socket_timeout=2)
        await _redis.ping()
        logger.info("Redis connected: %s", url.split("@")[-1])
    except Exception as e:
        logger.warning("Redis unavailable, falling back to no-op cache: %s", e)
        _redis = None

    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


# ── Categories cache ──────────────────────────────────────────


async def get_categories_cache() -> dict | None:
    r = await get_redis()
    if not r:
        return None
    try:
        raw = await r.get(_PREFIX_CATS)
        return json.loads(raw) if raw else None
    except Exception as e:
        logger.warning("cache get_categories: %s", e)
        return None


async def set_categories_cache(data: dict) -> None:
    r = await get_redis()
    if not r:
        return
    try:
        await r.setex(_PREFIX_CATS, TTL_CATEGORIES, json.dumps(data))
    except Exception as e:
        logger.warning("cache set_categories: %s", e)


async def invalidate_categories_cache() -> None:
    r = await get_redis()
    if not r:
        return
    try:
        await r.delete(_PREFIX_CATS)
    except Exception as e:
        logger.warning("cache invalidate_categories: %s", e)


# ── Guide cache ───────────────────────────────────────────────


async def get_guide_cache(key: str) -> dict | None:
    r = await get_redis()
    if not r:
        return None
    try:
        raw = await r.get(f"{_PREFIX_GUIDE}{key}")
        return json.loads(raw) if raw else None
    except Exception as e:
        logger.warning("cache get_guide(%s): %s", key, e)
        return None


async def set_guide_cache(key: str, data: dict) -> None:
    r = await get_redis()
    if not r:
        return
    try:
        await r.setex(f"{_PREFIX_GUIDE}{key}", TTL_GUIDE, json.dumps(data))
    except Exception as e:
        logger.warning("cache set_guide(%s): %s", key, e)


async def invalidate_guide_cache(key: str) -> None:
    r = await get_redis()
    if not r:
        return
    try:
        await r.delete(f"{_PREFIX_GUIDE}{key}")
    except Exception as e:
        logger.warning("cache invalidate_guide(%s): %s", key, e)


async def invalidate_all() -> None:
    """Сбрасывает весь кеш приложения (категории + все гайды)."""
    r = await get_redis()
    if not r:
        return
    try:
        # Удаляем категории
        await r.delete(_PREFIX_CATS)
        # Удаляем все гайды через SCAN (не KEYS — безопасно для prod)
        async for guide_key in r.scan_iter(f"{_PREFIX_GUIDE}*"):
            await r.delete(guide_key)
    except Exception as e:
        logger.warning("cache invalidate_all: %s", e)
