"""
PostgreSQL database layer for BlackRose Mini App.
Improvements over v1:
  - FTS full-text search (tsvector + GIN index, Russian + fallback ILIKE)
  - Audit log guide_history (create/update/delete/import)
  - preview + has_photo/video/document flags in get_guides_by_category
  - reorder_guides / reorder_categories for drag-and-drop
  - export_all / import_guides for JSON backup/restore
"""

import json
import logging
import os
import re

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
    """Инициализирует пул соединений.

    Схема БД управляется через Alembic миграции.
    Перед запуском приложения выполни: alembic upgrade head
    """
    await get_pool()
    logger.info("DB pool ready — schema managed by Alembic migrations")


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
        await conn.execute(
            """
            INSERT INTO categories(key, title, icon_url, sort_order)
            VALUES($1,$2,$3,$4)
            ON CONFLICT(key) DO UPDATE SET
                title=$2, icon_url=$3, sort_order=$4
        """,
            key,
            title,
            icon_url,
            sort_order,
        )


async def delete_category(key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM categories WHERE key=$1", key)


async def reorder_categories(order: list[dict]):
    """[{"key": "...", "sort_order": N}] — batch UNNEST UPDATE."""
    if not order:
        return
    pool = await get_pool()
    keys = [item["key"] for item in order]
    orders = [item["sort_order"] for item in order]
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE categories SET sort_order = v.so
            FROM UNNEST($1::text[], $2::int[]) AS v(k, so)
            WHERE categories.key = v.k
        """,
            keys,
            orders,
        )


# ── Guides ────────────────────────────────────────────


async def get_guides_by_category(category_key: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM guides WHERE category_key=$1 ORDER BY sort_order, key",
            category_key,
        )
        # Batch-fetch tags for all guides
        keys = [r["key"] for r in rows]
        tag_rows = (
            await conn.fetch(
                "SELECT guide_key, tag FROM guide_tags WHERE guide_key = ANY($1::text[])", keys
            )
            if keys
            else []
        )

    tags_by_key: dict[str, list[str]] = {}
    for tr in tag_rows:
        tags_by_key.setdefault(tr["guide_key"], []).append(tr["tag"])

    result = []
    for r in rows:
        d = dict(r)
        d["preview"] = _preview(d.get("text", ""))
        d["has_photo"] = bool(d.get("photo"))
        d["has_video"] = bool(d.get("video"))
        d["has_document"] = bool(d.get("document"))
        d["tags"] = sorted(tags_by_key.get(d["key"], []))
        result.append(d)
    return result


async def get_guide(key: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM guides WHERE key=$1", key)
    return dict(row) if row else None


async def upsert_guide(
    key: str,
    category_key: str,
    title: str,
    icon_url: str | None,
    text: str,
    photo: list,
    video: list,
    document: list,
    sort_order: int = 0,
    changed_by: int | None = None,
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT key FROM guides WHERE key=$1", key)
        action = "update" if existing else "create"

        await conn.execute(
            """
            INSERT INTO guides(key, category_key, title, icon_url, text,
                photo, video, document, sort_order, updated_at)
            VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW())
            ON CONFLICT(key) DO UPDATE SET
                category_key=$2, title=$3, icon_url=$4, text=$5,
                photo=$6, video=$7, document=$8, sort_order=$9, updated_at=NOW()
        """,
            key,
            category_key,
            title,
            icon_url,
            text,
            photo or [],
            video or [],
            document or [],
            sort_order,
        )

        snap = json.dumps(
            {
                "category_key": category_key,
                "title": title,
                "icon_url": icon_url,
                "sort_order": sort_order,
                "has_text": bool(text),
                "has_photo": bool(photo),
                "has_video": bool(video),
                "has_document": bool(document),
            }
        )
        await conn.execute(
            """
            INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
            VALUES($1,$2,$3,$4)
        """,
            key,
            action,
            changed_by,
            snap,
        )


async def delete_guide(key: str, changed_by: int | None = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT title, category_key FROM guides WHERE key=$1", key)
        if row:
            snap = json.dumps({"title": row["title"], "category_key": row["category_key"]})
            await conn.execute(
                """
                INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
                VALUES($1,'delete',$2,$3)
            """,
                key,
                changed_by,
                snap,
            )
        await conn.execute("DELETE FROM guides WHERE key=$1", key)


async def get_all_guides() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM guides ORDER BY category_key, sort_order, key")
    return [dict(r) for r in rows]


async def reorder_guides(order: list[dict]):
    """[{"key": "...", "sort_order": N}] — batch UNNEST UPDATE."""
    if not order:
        return
    pool = await get_pool()
    keys = [item["key"] for item in order]
    orders = [item["sort_order"] for item in order]
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE guides SET sort_order = v.so
            FROM UNNEST($1::text[], $2::int[]) AS v(k, so)
            WHERE guides.key = v.k
        """,
            keys,
            orders,
        )


async def get_guide_history(guide_key: str, limit: int = 30) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, guide_key, action, changed_by, changed_at, snapshot
            FROM guide_history WHERE guide_key=$1
            ORDER BY changed_at DESC LIMIT $2
        """,
            guide_key,
            limit,
        )
    return [dict(r) for r in rows]


# ── Search ────────────────────────────────────────────


async def search_guides(query: str, limit: int = 15) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        # FTS first
        rows = await conn.fetch(
            """
            SELECT key, title, icon_url, category_key,
                   ts_rank(search_vec, q) AS rank
            FROM guides, to_tsquery('russian', $1) q
            WHERE search_vec @@ q
            ORDER BY rank DESC
            LIMIT $2
        """,
            _to_tsquery(query),
            limit,
        )

        # Fallback ILIKE
        if not rows:
            q = f"%{query.lower()}%"
            rows = await conn.fetch(
                """
                SELECT key, title, icon_url, category_key, 0::float AS rank
                FROM guides
                WHERE lower(key) LIKE $1 OR lower(title) LIKE $1 OR lower(text) LIKE $1
                LIMIT $2
            """,
                q,
                limit,
            )

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
            {
                **dict(r),
                "photo": list(r["photo"]),
                "video": list(r["video"]),
                "document": list(r["document"]),
            }
            for r in guides
        ],
    }


async def import_guides(data: dict, changed_by: int | None = None) -> dict:
    cats = data.get("categories", [])
    guides = data.get("guides", [])

    # Pre-validate: all guide category_keys must exist in import or DB
    cat_keys_in_import = {c["key"] for c in cats}
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing_cats = {r["key"] for r in await conn.fetch("SELECT key FROM categories")}
    all_known_cats = cat_keys_in_import | existing_cats
    missing = [g["key"] for g in guides if g.get("category_key") not in all_known_cats]
    if missing:
        raise ValueError(
            f"Гайды ссылаются на несуществующие категории: {missing[:5]}"
            + (" и ещё..." if len(missing) > 5 else "")
        )

    async with pool.acquire() as conn:
        async with conn.transaction():
            for c in cats:
                await conn.execute(
                    """
                    INSERT INTO categories(key, title, icon_url, sort_order)
                    VALUES($1,$2,$3,$4)
                    ON CONFLICT(key) DO UPDATE SET
                        title=$2, icon_url=$3, sort_order=$4
                """,
                    c["key"],
                    c["title"],
                    c.get("icon_url"),
                    c.get("sort_order", 0),
                )

            for g in guides:
                await conn.execute(
                    """
                    INSERT INTO guides(key, category_key, title, icon_url, text,
                        photo, video, document, sort_order, updated_at)
                    VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW())
                    ON CONFLICT(key) DO UPDATE SET
                        category_key=$2, title=$3, icon_url=$4, text=$5,
                        photo=$6, video=$7, document=$8, sort_order=$9, updated_at=NOW()
                """,
                    g["key"],
                    g["category_key"],
                    g["title"],
                    g.get("icon_url"),
                    g.get("text", ""),
                    g.get("photo", []),
                    g.get("video", []),
                    g.get("document", []),
                    g.get("sort_order", 0),
                )
                await conn.execute(
                    """
                    INSERT INTO guide_history(guide_key, action, changed_by, snapshot)
                    VALUES($1,'import',$2,$3)
                """,
                    g["key"],
                    changed_by,
                    json.dumps({"title": g["title"]}),
                )

    return {"categories": len(cats), "guides": len(guides)}


# ── Tags ──────────────────────────────────────────────────────


async def get_guide_tags(guide_key: str) -> list[str]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT tag FROM guide_tags WHERE guide_key=$1 ORDER BY tag", guide_key
        )
    return [r["tag"] for r in rows]


async def set_guide_tags(guide_key: str, tags: list[str]):
    pool = await get_pool()
    clean = list({t.strip().lower() for t in tags if t.strip()})[:20]
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("DELETE FROM guide_tags WHERE guide_key=$1", guide_key)
            if clean:
                await conn.executemany(
                    "INSERT INTO guide_tags(guide_key, tag) VALUES($1,$2) ON CONFLICT DO NOTHING",
                    [(guide_key, tag) for tag in clean],
                )


async def get_all_tags() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT tag, COUNT(*) AS count
            FROM guide_tags GROUP BY tag ORDER BY count DESC, tag
        """)
    return [{"tag": r["tag"], "count": r["count"]} for r in rows]


async def get_guides_by_tag(tag: str, limit: int = 50) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT g.key, g.title, g.icon_url, g.category_key
            FROM guides g
            JOIN guide_tags t ON g.key = t.guide_key
            WHERE t.tag = $1
            ORDER BY g.sort_order, g.key
            LIMIT $2
        """,
            tag,
            limit,
        )
    return [dict(r) for r in rows]


# ── Views ─────────────────────────────────────────────────────


async def increment_views(guide_key: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE guides SET views = views + 1 WHERE key=$1 RETURNING views", guide_key
        )
    return row["views"] if row else 0


async def get_top_guides(limit: int = 10) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT key, title, icon_url, category_key, views
            FROM guides ORDER BY views DESC NULLS LAST LIMIT $1
        """,
            limit,
        )
    return [dict(r) for r in rows]


# ── Comments ──────────────────────────────────────────────────


async def get_comments(guide_key: str, limit: int = 50) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, user_id, username, first_name, text, created_at
            FROM guide_comments
            WHERE guide_key=$1
            ORDER BY created_at ASC
            LIMIT $2
        """,
            guide_key,
            limit,
        )
    return [dict(r) for r in rows]


async def add_comment(
    guide_key: str, user_id: int, username: str | None, first_name: str | None, text: str
) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO guide_comments(guide_key, user_id, username, first_name, text)
            VALUES($1,$2,$3,$4,$5) RETURNING id, created_at
        """,
            guide_key,
            user_id,
            username,
            first_name,
            text,
        )
    return {"id": row["id"], "created_at": row["created_at"].isoformat()}


async def delete_comment(
    comment_id: int, user_id: int | None = None, is_admin: bool = False
) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if is_admin:
            r = await conn.execute("DELETE FROM guide_comments WHERE id=$1", comment_id)
        else:
            r = await conn.execute(
                "DELETE FROM guide_comments WHERE id=$1 AND user_id=$2", comment_id, user_id
            )
    return r != "DELETE 0"


# ── Subscriptions (notifications) ────────────────────────────


async def subscribe(user_id: int, category_key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_subscriptions(user_id, category_key)
            VALUES($1,$2) ON CONFLICT DO NOTHING
        """,
            user_id,
            category_key,
        )


async def unsubscribe(user_id: int, category_key: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM user_subscriptions WHERE user_id=$1 AND category_key=$2",
            user_id,
            category_key,
        )


async def get_user_subscriptions(user_id: int) -> list[str]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT category_key FROM user_subscriptions WHERE user_id=$1", user_id
        )
    return [r["category_key"] for r in rows]


async def get_subscribers(category_key: str) -> list[int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM user_subscriptions WHERE category_key=$1", category_key
        )
    return [r["user_id"] for r in rows]
