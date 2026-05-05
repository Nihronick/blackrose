import asyncio
import logging
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger("blackrose.core.db")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_init_lock = asyncio.Lock()

def _normalize_db_url(url: str) -> str:
    if not url:
        return url
    url = url.strip().strip("'").strip('"')
    if url.startswith("postgresql+asyncpg://"):
        pass  # already correct
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif "@" in url and not url.startswith(("http://", "https://")):
        # Bare URL without scheme: user:pass@host/db
        url = "postgresql+asyncpg://" + url
    url = url.replace("sslmode=require", "ssl=require")
    url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
    return url

async def init_db():
    global _engine, _sessionmaker
    async with _init_lock:
        if _engine is not None:
            return
        from core.config import settings
        url = _normalize_db_url(settings.DATABASE_URL)
        try:
            _engine = create_async_engine(
                url,
                pool_size=15,
                max_overflow=10,
                pool_recycle=300,
                pool_pre_ping=True,
            )
            _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
            async with _engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection verified.")
        except Exception as e:
            logger.error("Failed to initialize database: %s", e)
            raise

async def close_pool():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None

def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Database not initialized.")
    return _sessionmaker

async def get_health() -> dict:
    if _engine is None or _sessionmaker is None:
        return {"status": "uninitialized", "latency_ms": None}

    import time
    start = time.perf_counter()
    try:
        async with _engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency}
    except Exception as e:
        logger.error("DB Health check failed: %s", e)
        return {"status": "unhealthy", "error": str(e), "latency_ms": None}

def is_db_ready() -> bool:
    return _engine is not None and _sessionmaker is not None
