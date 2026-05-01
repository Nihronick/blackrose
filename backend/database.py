import asyncio
import logging
import os
import re
from datetime import datetime

from db_models import (
    Category,
    Guide,
    GuideComment,
    GuideHistory,
    GuideTag,
    LocalAdmin,
    Member,
    UserSubscription,
)
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger("blackrose.db")

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_init_lock = asyncio.Lock()


async def get_pool():
    pass


def _normalize_db_url(url: str) -> str:
    """Конвертирует DATABASE_URL в формат asyncpg."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    # asyncpg использует ssl=require, не sslmode=require
    url = url.replace("sslmode=require", "ssl=require")
    # убираем channel_binding — asyncpg не поддерживает
    url = re.sub(r"[&?]channel_binding=[^&]*", "", url)
    url = re.sub(r"\?&", "?", url)
    return url


async def init_db():
    """
    Initializes the global SQLAlchemy engine and sessionmaker.
    Uses a lock to prevent concurrent initialization.
    """
    global _engine, _sessionmaker
    
    async with _init_lock:
        if _engine is not None:
            return  # Already initialized
            
        raw_url = os.getenv("DATABASE_URL", "")
        if not raw_url:
            raise RuntimeError("DATABASE_URL не задан")
        url = _normalize_db_url(raw_url)

        logger.info("Connecting to Database: %s", url.split("@")[-1])
        
        try:
            _engine = create_async_engine(
                url,
                pool_size=15,
                max_overflow=10,
                pool_recycle=300,
                pool_pre_ping=True,
            )
            _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize database: %s", e)
            _engine = None
            _sessionmaker = None
            raise


async def close_pool():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Returns the global sessionmaker. 
    Raises RuntimeError if init_db() was not called or failed.
    """
    if _sessionmaker is None:
        raise RuntimeError("Database not initialized. Ensure init_db() was awaited during startup.")
    return _sessionmaker


def is_db_ready() -> bool:
    """Check if the database engine is initialized."""
    return _engine is not None and _sessionmaker is not None


# ── helpers ───────────────────────────────────────────


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _strip_markdown(text: str) -> str:
    s = text or ""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"\{\{[\w]+\}\}", "", s)
    s = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", s)
    return s.strip()


# ── Categories ────────────────────────────────────────


async def get_categories() -> list[dict]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Category).order_by(Category.sort_order, Category.created_at)
        )
        return [
            {"key": c.key, "title": c.title, "icon": c.icon_url, "sort_order": c.sort_order}
            for c in result.scalars()
        ]


async def get_categories_with_counts() -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(
                Category.key,
                Category.title,
                Category.icon_url,
                Category.sort_order,
                func.count(Guide.key).label("count"),
            )
            .outerjoin(Guide, Guide.category_key == Category.key)
            .group_by(
                Category.key,
                Category.title,
                Category.icon_url,
                Category.sort_order,
                Category.created_at,
            )
            .order_by(Category.sort_order, Category.created_at)
        )
        rows = await session.execute(stmt)
        return [
            {"key": r.key, "title": r.title, "icon": r.icon_url, "sort_order": r.sort_order, "count": r.count}
            for r in rows
        ]


async def get_category(key: str) -> dict | None:
    async with get_sessionmaker()() as session:
        result = await session.execute(select(Category).where(Category.key == key))
        cat = result.scalar_one_or_none()
        if not cat:
            return None
        return {"key": cat.key, "title": cat.title, "icon": cat.icon_url}


async def upsert_category(
    key: str, title: str, icon_url: str | None, sort_order: int = 0
):
    async with get_sessionmaker()() as session:
        stmt = (
            insert(Category)
            .values(key=key, title=title, icon_url=icon_url, sort_order=sort_order)
            .on_conflict_do_update(
                index_elements=["key"],
                set_={"title": title, "icon_url": icon_url, "sort_order": sort_order},
            )
        )
        await session.execute(stmt)
        await session.commit()


async def delete_category(key: str):
    async with get_sessionmaker()() as session:
        await session.execute(delete(Category).where(Category.key == key))
        await session.commit()


async def reorder_categories(items: list[dict]):
    async with get_sessionmaker()() as session:
        for item in items:
            await session.execute(
                update(Category)
                .where(Category.key == item["key"])
                .values(sort_order=item["sort_order"])
            )
        await session.commit()


# ── Guides ────────────────────────────────────────────


def _guide_to_dict(g: Guide) -> dict:
    d = {
        "key": g.key,
        "category_key": g.category_key,
        "title": g.title,
        "icon_url": g.icon_url,
        "text": g.text,
        "photo": g.photo or [],
        "video": g.video or [],
        "document": g.document or [],
        "sort_order": g.sort_order,
        "views": g.views or 0,
        "has_photo": bool(g.photo),
        "has_video": bool(g.video),
        "has_document": bool(g.document),
        "preview": _strip_markdown(g.text)[:200],
    }
    # If tags relationship was pre-loaded, include them
    try:
        d["tags"] = [t.tag for t in g.tags]
    except Exception:
        d["tags"] = []
    return d


async def get_guide(key: str) -> dict | None:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Guide).options(selectinload(Guide.tags)).where(Guide.key == key)
        )
        g = result.scalar_one_or_none()
        return _guide_to_dict(g) if g else None


async def get_guides_by_category(category_key: str) -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(Guide)
            .options(selectinload(Guide.tags))
            .where(Guide.category_key == category_key)
            .order_by(Guide.sort_order, Guide.created_at)
        )
        result = await session.execute(stmt)
        return [_guide_to_dict(g) for g in result.scalars()]


async def get_all_guides() -> list[dict]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Guide).order_by(Guide.category_key, Guide.sort_order)
        )
        return [_guide_to_dict(g) for g in result.scalars()]


async def upsert_guide(
    key: str,
    category_key: str,
    title: str,
    icon_url: str | None,
    text: str,
    photo: list[str],
    video: list[str],
    document: list[str],
    sort_order: int = 0,
    changed_by: int | None = None,
) -> bool:
    async with get_sessionmaker()() as session:
        existing_result = await session.execute(select(Guide).where(Guide.key == key))
        existing_guide = existing_result.scalar_one_or_none()
        is_new = existing_guide is None
        old_snapshot = _guide_to_dict(existing_guide) if not is_new else None

        stmt = insert(Guide).values(
            key=key,
            category_key=category_key,
            title=title,
            icon_url=icon_url,
            text=text,
            photo=photo,
            video=video,
            document=document,
            sort_order=sort_order,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Guide.key],
            set_={
                Guide.category_key: stmt.excluded.category_key,
                Guide.title: stmt.excluded.title,
                Guide.icon_url: stmt.excluded.icon_url,
                Guide.text: stmt.excluded.text,
                Guide.photo: stmt.excluded.photo,
                Guide.video: stmt.excluded.video,
                Guide.document: stmt.excluded.document,
                Guide.sort_order: stmt.excluded.sort_order,
                Guide.updated_at: func.now(),
            },
        )
        await session.execute(stmt)

        history = GuideHistory(
            guide_key=key,
            action="created" if is_new else "updated",
            changed_by=changed_by,
            snapshot=old_snapshot,
        )
        session.add(history)
        await session.commit()
        return is_new


async def delete_guide(key: str, changed_by: int | None = None):
    async with get_sessionmaker()() as session:
        g = (
            await session.execute(select(Guide).where(Guide.key == key))
        ).scalar_one_or_none()
        if g:
            history = GuideHistory(
                guide_key=key,
                action="deleted",
                changed_by=changed_by,
                snapshot=_guide_to_dict(g),
            )
            session.add(history)
        await session.execute(delete(Guide).where(Guide.key == key))
        await session.commit()


async def reorder_guides(items: list[dict]):
    async with get_sessionmaker()() as session:
        for item in items:
            await session.execute(
                update(Guide)
                .where(Guide.key == item["key"])
                .values(sort_order=item["sort_order"])
            )
        await session.commit()


async def search_guides(q: str) -> list[dict]:
    async with get_sessionmaker()() as session:
        # Escape LIKE wildcards to prevent unintended matches
        safe_q = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{safe_q}%"
        stmt = (
            select(Guide)
            .options(selectinload(Guide.tags))
            .where(Guide.title.ilike(pattern))
            .order_by(Guide.sort_order)
            .limit(20)
        )
        result = await session.execute(stmt)
        return [_guide_to_dict(g) for g in result.scalars()]


async def increment_views(key: str) -> int:
    from db_models import ViewLog
    async with get_sessionmaker()() as session:
        # 1. Update total counter
        result = await session.execute(
            update(Guide)
            .where(Guide.key == key)
            .values(views=Guide.views + 1)
            .returning(Guide.views)
        )
        # 2. Log individual view for analytics
        session.add(ViewLog(guide_key=key))
        await session.commit()
        return result.scalar_one_or_none() or 0


async def get_top_guides(limit: int = 10) -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(Guide)
            .options(selectinload(Guide.tags))
            .order_by(desc(Guide.views))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [_guide_to_dict(g) for g in result.scalars()]


async def get_recent_guides(limit: int = 10) -> list[dict]:
    """Returns guides sorted by updated_at (or created_at) descending."""
    async with get_sessionmaker()() as session:
        stmt = (
            select(Guide)
            .options(selectinload(Guide.tags))
            .order_by(desc(Guide.updated_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [_guide_to_dict(g) for g in result.scalars()]


async def get_global_recent_comments(limit: int = 10) -> list[dict]:
    """Returns latest comments across all guides."""
    async with get_sessionmaker()() as session:
        stmt = (
            select(GuideComment, Guide.title.label("guide_title"))
            .join(Guide, Guide.key == GuideComment.guide_key)
            .order_by(desc(GuideComment.created_at))
            .limit(limit)
        )
        rows = await session.execute(stmt)
        return [
            {
                "id": r.GuideComment.id,
                "guide_key": r.GuideComment.guide_key,
                "guide_title": r.guide_title,
                "user_id": r.GuideComment.user_id,
                "username": r.GuideComment.username,
                "first_name": r.GuideComment.first_name,
                "text": r.GuideComment.text,
                "created_at": r.GuideComment.created_at,
            }
            for r in rows
        ]


async def get_daily_analytics(days: int = 30) -> list[dict]:
    from datetime import datetime, timedelta, timezone
    from db_models import ViewLog
    async with get_sessionmaker()() as session:
        # Group views by day
        day_trunc = func.date_trunc('day', ViewLog.viewed_at)
        stmt = (
            select(day_trunc.label("day"), func.count(ViewLog.id).label("count"))
            .where(ViewLog.viewed_at >= datetime.now(timezone.utc) - timedelta(days=days))
            .group_by(day_trunc)
            .order_by(day_trunc)
        )
        result = await session.execute(stmt)
        return [{"day": r.day.isoformat(), "count": r.count} for r in result]


# ── Guide History ─────────────────────────────────────


async def get_guide_history(key: str) -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(GuideHistory)
            .where(GuideHistory.guide_key == key)
            .order_by(desc(GuideHistory.changed_at))
            .limit(20)
        )
        result = await session.execute(stmt)
        return [
            {
                "id": h.id,
                "action": h.action,
                "changed_by": h.changed_by,
                "changed_at": h.changed_at,
                "snapshot": h.snapshot,
            }
            for h in result.scalars()
        ]


# ── Tags ──────────────────────────────────────────────


async def get_guide_tags(guide_key: str) -> list[str]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(GuideTag.tag).where(GuideTag.guide_key == guide_key)
        )
        return list(result.scalars())


async def set_guide_tags(guide_key: str, tags: list[str]):
    async with get_sessionmaker()() as session:
        await session.execute(delete(GuideTag).where(GuideTag.guide_key == guide_key))
        for tag in tags:
            session.add(GuideTag(guide_key=guide_key, tag=tag.lower().strip()))
        await session.commit()


async def get_all_tags() -> list[str]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(GuideTag.tag).distinct().order_by(GuideTag.tag)
        )
        return list(result.scalars())


async def get_guides_by_tag(tag: str) -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(Guide)
            .join(GuideTag, GuideTag.guide_key == Guide.key)
            .where(GuideTag.tag == tag.lower())
            .order_by(Guide.sort_order)
        )
        result = await session.execute(stmt)
        return [_guide_to_dict(g) for g in result.scalars()]


# ── Comments ──────────────────────────────────────────


async def get_comments(guide_key: str) -> list[dict]:
    async with get_sessionmaker()() as session:
        stmt = (
            select(GuideComment)
            .where(GuideComment.guide_key == guide_key)
            .order_by(GuideComment.created_at)
        )
        result = await session.execute(stmt)
        return [
            {
                "id": c.id,
                "user_id": c.user_id,
                "username": c.username,
                "first_name": c.first_name,
                "text": c.text,
                "created_at": c.created_at,
            }
            for c in result.scalars()
        ]


async def add_comment(
    guide_key: str,
    user_id: int,
    username: str,
    first_name: str,
    text: str,
) -> dict:
    async with get_sessionmaker()() as session:
        comment = GuideComment(
            guide_key=guide_key,
            user_id=user_id,
            username=username,
            first_name=first_name,
            text=text,
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "first_name": comment.first_name,
            "text": comment.text,
            "created_at": comment.created_at,
        }


async def delete_comment(comment_id: int, user_id: int, is_admin: bool = False) -> bool:
    async with get_sessionmaker()() as session:
        stmt = select(GuideComment).where(GuideComment.id == comment_id)
        if not is_admin:
            stmt = stmt.where(GuideComment.user_id == user_id)
        result = await session.execute(stmt)
        comment = result.scalar_one_or_none()
        if not comment:
            return False
        await session.delete(comment)
        await session.commit()
        return True


# ── Subscriptions ─────────────────────────────────────


async def get_subscribers(category_key: str) -> list[int]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(UserSubscription.user_id).where(
                UserSubscription.category_key == category_key
            )
        )
        return list(result.scalars())


async def get_user_subscriptions(user_id: int) -> list[str]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(UserSubscription.category_key).where(
                UserSubscription.user_id == user_id
            )
        )
        return list(result.scalars())


async def subscribe(user_id: int, category_key: str):
    async with get_sessionmaker()() as session:
        stmt = (
            insert(UserSubscription)
            .values(user_id=user_id, category_key=category_key)
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)
        await session.commit()


async def unsubscribe(user_id: int, category_key: str):
    async with get_sessionmaker()() as session:
        await session.execute(
            delete(UserSubscription).where(
                UserSubscription.user_id == user_id,
                UserSubscription.category_key == category_key,
            )
        )
        await session.commit()


# ── Members ───────────────────────────────────────────


async def list_members() -> list[dict]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Member).where(Member.is_active).order_by(Member.created_at)
        )
        return [
            {
                "user_id": m.user_id,
                "username": m.username,
                "first_name": m.first_name,
                "role": m.role,
                "added_by": m.added_by,
                "created_at": m.created_at,
            }
            for m in result.scalars()
        ]


async def upsert_member(
    user_id: int,
    username: str | None,
    first_name: str | None,
    role: str = "member",
    added_by: int | None = None,
) -> bool:
    async with get_sessionmaker()() as session:
        existing = await session.execute(
            select(Member).where(Member.user_id == user_id)
        )
        is_new = existing.scalar_one_or_none() is None
        stmt = (
            insert(Member)
            .values(
                user_id=user_id,
                username=username,
                first_name=first_name,
                role=role,
                added_by=added_by,
                is_active=True,
            )
            .on_conflict_do_update(
                index_elements=["user_id"],
                set_={
                    "username": username,
                    "first_name": first_name,
                    "role": role,
                    "is_active": True,
                },
            )
        )
        await session.execute(stmt)
        await session.commit()
        return is_new


async def deactivate_member(user_id: int) -> bool:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Member).where(Member.user_id == user_id, Member.is_active)
        )
        m = result.scalar_one_or_none()
        if not m:
            return False
        await session.execute(
            update(Member).where(Member.user_id == user_id).values(is_active=False)
        )
        await session.commit()
        return True


async def get_admin_member_ids() -> set[int]:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(Member.user_id).where(
                Member.role == "admin", Member.is_active
            )
        )
        return set(result.scalars())


# ── Local Admins ──────────────────────────────────────


async def get_local_admin(username: str) -> dict | None:
    async with get_sessionmaker()() as session:
        result = await session.execute(
            select(LocalAdmin).where(LocalAdmin.username == username)
        )
        a = result.scalar_one_or_none()
        if not a:
            return None
        return {"username": a.username, "password_hash": a.password_hash}


async def upsert_local_admin(username: str, password_hash: str):
    async with get_sessionmaker()() as session:
        stmt = (
            insert(LocalAdmin)
            .values(username=username, password_hash=password_hash)
            .on_conflict_do_update(
                index_elements=["username"],
                set_={"password_hash": password_hash},
            )
        )
        await session.execute(stmt)
        await session.commit()


# ── Export / Import ───────────────────────────────────


async def export_all() -> dict:
    cats = await get_categories()
    guides = await get_all_guides()
    return {"categories": cats, "guides": guides}


async def import_guides(data: dict, changed_by: int | None = None) -> dict:
    created_cats = updated_cats = created_guides = updated_guides = 0
    for cat in data.get("categories", []):
        existing = await get_category(cat["key"])
        await upsert_category(
            cat["key"], cat["title"], cat.get("icon"), cat.get("sort_order", 0)
        )
        if existing:
            updated_cats += 1
        else:
            created_cats += 1
    for g in data.get("guides", []):
        existing = await get_guide(g["key"])
        await upsert_guide(
            key=g["key"],
            category_key=g["category_key"],
            title=g["title"],
            icon_url=g.get("icon_url"),
            text=g.get("text", ""),
            photo=g.get("photo", []),
            video=g.get("video", []),
            document=g.get("document", []),
            sort_order=g.get("sort_order", 0),
            changed_by=changed_by,
        )
        if existing:
            updated_guides += 1
        else:
            created_guides += 1
    return {
        "categories_created": created_cats,
        "categories_updated": updated_cats,
        "guides_created": created_guides,
        "guides_updated": updated_guides,
    }
