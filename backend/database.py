"""
PostgreSQL database layer for BlackRose Mini App.
Improvements over v1:
  - FTS full-text search (tsvector + GIN index, Russian + fallback ILIKE)
  - Audit log guide_history (create/update/delete/import)
  - preview + has_photo/video/document flags in get_guides_by_category
  - reorder_guides / reorder_categories for drag-and-drop
  - export_all / import_guides for JSON backup/restore
"""
import os
import json
import re
import logging
import asyncpg

logger = logging.getLogger("blackrose.db")

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
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
                updated_at   TIMESTAMPTZ DEFAULT NOW(),
                search_vec   TSVECTOR
            )
        """)
        # Migration: add search_vec to existing tables
        await conn.execute(
            "ALTER TABLE guides ADD COLUMN IF NOT EXISTS search_vec TSVECTOR"
        )
        # Audit log
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS guide_history (
                id          BIGSERIAL PRIMARY KEY,
                guide_key   TEXT NOT NULL,
                action      TEXT NOT NULL,
                changed_by  BIGINT,
                changed_at  TIMESTAMPTZ DEFAULT NOW(),
                snapshot    JSONB
            )
        """)
        # Indexes
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_guides_category ON guides(category_key)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_guides_fts ON guides USING GIN(search_vec)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_guide_history_key ON guide_history(guide_key)"
        )
        # FTS trigger
        await conn.execute("""
            CREATE OR REPLACE FUNCTION guides_fts_update() RETURNS trigger AS $$
            BEGIN
                NEW.search_vec :=
                    setweight(to_tsvector('russian', coalesce(NEW.title, '')), 'A') ||
                    setweight(to_tsvector('russian', coalesce(NEW.key,   '')), 'B') ||
                    setweight(to_tsvector('russian', coalesce(
                        regexp_replace(NEW.text, '<[^>]+>', '', 'g'), ''
                    )), 'C');
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """)
        await conn.execute("""
            CREATE OR REPLACE TRIGGER guides_fts_trigger
            BEFORE INSERT OR UPDATE ON guides
            FOR EACH ROW EXECUTE FUNCTION guides_fts_update();
        """)
        # Backfill existing rows
        await conn.execute("""
            UPDATE guides SET search_vec =
                setweight(to_tsvector('russian', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(key,   '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(
                    regexp_replace(text, '<[^>]+>', '', 'g'), ''
                )), 'C')
            WHERE search_vec IS NULL
        """)
    logger.info("DB ready: FTS + audit enabled")


# ── helpers ───────────────────────────────────────────

def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()

def _preview(text: str, n: int = 80) -> str:
    s = _strip_html(text)
    return s[:n] + ("…" if len(s) > n else "")

def _to_tsquery(q: str) -> str:
    words = re.findall(r"\w+", q)
    return " & ".join(f"{w}:*" for w in words) or q


# ── Categories ────────────────────────────────────────

async def get_categories() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM categories ORDER BY sort_order, key")
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
            VALUES($1,$2,$3,$4)
            ON CONFLICT(key) DO UPDATE SET
                title=$2, icon_url=$3, sort_order=$4
        """, key, title, icon_url, sort_order)


async def delete_category(key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM categories WHERE key=$1", key)


async def reorder_categories(order: list[dict]):
    """[{"key": "...", "sort_order": N}]"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for item in order:
                await conn.execute(
                    "UPDATE categories SET sort_order=$1 WHERE key=$2",
                    item["sort_order"], item["key"]
                )


# ── Guides ────────────────────────────────────────────

async def get_guides_by_category(category_key: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM guides WHERE category_key=$1 ORDER BY sort_order, key",
            category_key,
        )
    result = []
    for r in rows:
        d = dict(r)
        d["preview"]      = _preview(d.get("text", ""))
        d["has_photo"]    = bool(d.get("photo"))
        d["has_video"]    = bool(d.get("video"))
        d["has_document"] = bool(d.get("document"))
        result.append(d)
    return result


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
    changed_by: int | None = None,
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT key FROM guides WHERE key=$1", key)
        action = "update" if existing else "create"

        await conn.execute("""
            INSERT INTO guides(key, category_key, title, icon_url, text,
                photo, video, document, sort_order, updated_at)
            VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW())
            ON CONFLICT(key) DO UPDATE SET
                category_key=$2, title=$3, icon_url=$4, text=$5,
                photo=$6, video=$7, document=$8, sort_order=$9, updated_at=NOW()
        """, key, category_key, title, icon_url, text,
            photo or [], video or [], document or [], sort_order)

        snap = json.dumps({
            "category_key": category_key, "title": title,
            "icon_url": icon_url, "sort_order": sort_order,
            "has_text": bool(text), "has_photo": bool(photo),
            "has_video": bool(video), "has_document": bool(document),
        })
        await conn.execute("""
            INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
            VALUES($1,$2,$3,$4)
        """, key, action, changed_by, snap)


async def delete_guide(key: str, changed_by: int | None = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT title, category_key FROM guides WHERE key=$1", key
        )
        if row:
            snap = json.dumps({"title": row["title"], "category_key": row["category_key"]})
            await conn.execute("""
                INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
                VALUES($1,'delete',$2,$3)
            """, key, changed_by, snap)
        await conn.execute("DELETE FROM guides WHERE key=$1", key)


async def get_all_guides() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM guides ORDER BY category_key, sort_order, key"
        )
    return [dict(r) for r in rows]


async def reorder_guides(order: list[dict]):
    """[{"key": "...", "sort_order": N}]"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for item in order:
                await conn.execute(
                    "UPDATE guides SET sort_order=$1 WHERE key=$2",
                    item["sort_order"], item["key"]
                )


async def get_guide_history(guide_key: str, limit: int = 30) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, guide_key, action, changed_by, changed_at, snapshot
            FROM guide_history WHERE guide_key=$1
            ORDER BY changed_at DESC LIMIT $2
        """, guide_key, limit)
    return [dict(r) for r in rows]


# ── Search ────────────────────────────────────────────

async def search_guides(query: str, limit: int = 15) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # FTS first
        rows = await conn.fetch("""
            SELECT key, title, icon_url, category_key,
                   ts_rank(search_vec, q) AS rank
            FROM guides, to_tsquery('russian', $1) q
            WHERE search_vec @@ q
            ORDER BY rank DESC
            LIMIT $2
        """, _to_tsquery(query), limit)

        # Fallback ILIKE
        if not rows:
            q = f"%{query.lower()}%"
            rows = await conn.fetch("""
                SELECT key, title, icon_url, category_key, 0::float AS rank
                FROM guides
                WHERE lower(key) LIKE $1 OR lower(title) LIKE $1 OR lower(text) LIKE $1
                LIMIT $2
            """, q, limit)

    return [dict(r) for r in rows]


# ── Export / Import ───────────────────────────────────

async def export_all() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        cats = await conn.fetch(
            "SELECT key, title, icon_url, sort_order FROM categories ORDER BY sort_order, key"
        )
        guides = await conn.fetch("""
            SELECT key, category_key, title, icon_url, text,
                   photo, video, document, sort_order
            FROM guides ORDER BY category_key, sort_order, key
        """)
    return {
        "version": 1,
        "categories": [dict(r) for r in cats],
        "guides": [
            {**dict(r),
             "photo":    list(r["photo"]),
             "video":    list(r["video"]),
             "document": list(r["document"])}
            for r in guides
        ],
    }


async def import_guides(data: dict, changed_by: int | None = None) -> dict:
    cats   = data.get("categories", [])
    guides = data.get("guides", [])
    pool   = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            for c in cats:
                await conn.execute("""
                    INSERT INTO categories(key, title, icon_url, sort_order)
                    VALUES($1,$2,$3,$4)
                    ON CONFLICT(key) DO UPDATE SET
                        title=$2, icon_url=$3, sort_order=$4
                """, c["key"], c["title"], c.get("icon_url"), c.get("sort_order", 0))

            for g in guides:
                await conn.execute("""
                    INSERT INTO guides(key, category_key, title, icon_url, text,
                        photo, video, document, sort_order, updated_at)
                    VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW())
                    ON CONFLICT(key) DO UPDATE SET
                        category_key=$2, title=$3, icon_url=$4, text=$5,
                        photo=$6, video=$7, document=$8, sort_order=$9, updated_at=NOW()
                """, g["key"], g["category_key"], g["title"], g.get("icon_url"),
                    g.get("text", ""),
                    g.get("photo", []), g.get("video", []), g.get("document", []),
                    g.get("sort_order", 0))
                await conn.execute("""
                    INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
                    VALUES($1,'import',$2,$3)
                """, g["key"], changed_by,
                    json.dumps({"title": g["title"]}))

    return {"categories": len(cats), "guides": len(guides)}
