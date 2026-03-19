"""
PostgreSQL database layer for BlackRose Mini App.
Tables: categories, guides
"""
import os
import logging
import asyncpg

logger = logging.getLogger("blackrose.db")

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=5,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    """Create tables if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                key         TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                icon_url    TEXT,
                sort_order  INTEGER DEFAULT 0,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS guides (
                key          TEXT PRIMARY KEY,
                category_key TEXT NOT NULL REFERENCES categories(key) ON DELETE CASCADE,
                title        TEXT NOT NULL,
                icon_url     TEXT,
                text         TEXT DEFAULT '',
                photo        TEXT[] DEFAULT '{}',
                video        TEXT[] DEFAULT '{}',
                document     TEXT[] DEFAULT '{}',
                sort_order   INTEGER DEFAULT 0,
                created_at   TIMESTAMPTZ DEFAULT NOW(),
                updated_at   TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_guides_category
            ON guides(category_key)
        """)
    logger.info("Database schema ready")


# ── Categories ────────────────────────────────────────
async def get_categories() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM categories ORDER BY sort_order, key"
        )
    return [dict(r) for r in rows]


async def get_category(key: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM categories WHERE key=$1", key)
    return dict(row) if row else None


async def upsert_category(key: str, title: str, icon_url: str | None, sort_order: int = 0):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO categories(key, title, icon_url, sort_order)
            VALUES($1, $2, $3, $4)
            ON CONFLICT(key) DO UPDATE SET
                title      = EXCLUDED.title,
                icon_url   = EXCLUDED.icon_url,
                sort_order = EXCLUDED.sort_order
        """, key, title, icon_url, sort_order)


async def delete_category(key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM categories WHERE key=$1", key)


# ── Guides ────────────────────────────────────────────
async def get_guides_by_category(category_key: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM guides WHERE category_key=$1 ORDER BY sort_order, key",
            category_key,
        )
    return [dict(r) for r in rows]


async def get_guide(key: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM guides WHERE key=$1", key)
    return dict(row) if row else None


async def upsert_guide(
    key: str, category_key: str, title: str,
    icon_url: str | None, text: str,
    photo: list, video: list, document: list,
    sort_order: int = 0,
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO guides(key, category_key, title, icon_url, text, photo, video, document, sort_order, updated_at)
            VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW())
            ON CONFLICT(key) DO UPDATE SET
                category_key = EXCLUDED.category_key,
                title        = EXCLUDED.title,
                icon_url     = EXCLUDED.icon_url,
                text         = EXCLUDED.text,
                photo        = EXCLUDED.photo,
                video        = EXCLUDED.video,
                document     = EXCLUDED.document,
                sort_order   = EXCLUDED.sort_order,
                updated_at   = NOW()
        """, key, category_key, title, icon_url, text,
            photo or [], video or [], document or [], sort_order)


async def delete_guide(key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM guides WHERE key=$1", key)


async def get_all_guides() -> list[dict]:
    """Все гайды одним запросом — для admin panel."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM guides ORDER BY category_key, sort_order, key"
        )
    return [dict(r) for r in rows]


async def search_guides(query: str) -> list[dict]:
    pool = await get_pool()
    q = f"%{query.lower()}%"
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM guides
            WHERE lower(key) LIKE $1
               OR lower(title) LIKE $1
               OR lower(text) LIKE $1
            LIMIT 10
        """, q)
    return [dict(r) for r in rows]
