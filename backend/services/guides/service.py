from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, desc, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
import asyncio
from core.db import get_sessionmaker
from models.db_models import (
    Guide,
    GuideHistory,
    GuideComment,
    Category,
    Member,
    GuideTag,
    UserSubscription,
    ViewLog,
)
from core.logging import get_logger
from services.common.utils import _strip_markdown

logger = get_logger("blackrose.services.guides")

class GuideService:
    @staticmethod
    def _safe_tags(g) -> list[str]:
        """Safely extract tags, returning [] on lazy-load failures."""
        try:
            return [t.tag for t in g.tags] if g.tags else []
        except Exception:
            return []

    @staticmethod
    def _to_dict(g: Guide) -> dict:
        if not g:
            return {}
        return {
            "key": g.key,
            "category_key": g.category_key,
            "title": g.title,
            "icon_url": g.icon_url,
            "text": g.text,
            "photo": g.photo or [],
            "video": g.video or [],
            "document": g.document or [],
            "sort_order": g.sort_order,
            "created_at": g.created_at.isoformat() if g.created_at else None,
            "updated_at": g.updated_at.isoformat() if g.updated_at else None,
            "views": g.views or 0,
            "tags": GuideService._safe_tags(g),
            "preview": _strip_markdown(g.text)[:200],
            "has_photo": bool(g.photo),
            "has_video": bool(g.video),
            "has_document": bool(g.document),
        }

    @classmethod
    async def get_by_key(cls, key: str) -> dict | None:
        async with get_sessionmaker()() as session:
            result = await session.execute(
                select(Guide).options(selectinload(Guide.tags)).where(Guide.key == key)
            )
            g = result.scalar_one_or_none()
            return cls._to_dict(g) if g else None

    @classmethod
    async def search(cls, query: str) -> list[dict]:
        if not query or len(query) < 2:
            return []
        async with get_sessionmaker()() as session:
            # We use plainto_tsquery for natural language search
            # and rank the results by relevance
            stmt = (
                select(Guide)
                .options(selectinload(Guide.tags))
                .where(Guide.search_vec.bool_op("@@")(func.plainto_tsquery("russian", query)))
                .order_by(desc(func.ts_rank(Guide.search_vec, func.plainto_tsquery("russian", query))))
                .limit(20)
            )
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

    @classmethod
    async def get_all(cls, category_key: str | None = None) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = select(Guide).options(selectinload(Guide.tags)).order_by(Guide.sort_order)
            if category_key:
                stmt = stmt.where(Guide.category_key == category_key)
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

    @classmethod
    async def get_top_guides(cls, limit: int = 10) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = select(Guide).options(selectinload(Guide.tags)).order_by(desc(Guide.views)).limit(limit)
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

    @classmethod
    async def get_recent_guides(cls, limit: int = 10) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = select(Guide).options(selectinload(Guide.tags)).order_by(desc(Guide.updated_at)).limit(limit)
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

    @classmethod
    async def get_recent_comments(cls, limit: int = 10) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = (
                select(GuideComment, Guide.title)
                .join(Guide, GuideComment.guide_key == Guide.key)
                .order_by(desc(GuideComment.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            comments = []
            for comment, guide_title in result.all():
                comments.append({
                    "id": comment.id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                    "user_id": comment.user_id,
                    "first_name": comment.first_name,
                    "username": comment.username,
                    "guide_key": comment.guide_key,
                    "guide_title": guide_title
                })
            return comments

    @classmethod
    async def upsert(cls, key: str, data: dict, changed_by: int | None = None) -> bool:
        async with get_sessionmaker()() as session:
            existing = await session.execute(select(Guide).where(Guide.key == key))
            existing_guide = existing.scalar_one_or_none()
            is_new = existing_guide is None

            old_snapshot = cls._to_dict(existing_guide) if not is_new else None

            stmt = insert(Guide).values(key=key, **data)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Guide.key],
                set_={k: getattr(stmt.excluded, k) for k in data.keys()}
            )
            await session.execute(stmt)

            history = GuideHistory(
                guide_key=key,
                action="created" if is_new else "updated",
                changed_by=changed_by,
                snapshot=old_snapshot
            )
            session.add(history)
            await session.commit()

            # Trigger Git Sync (non-blocking)
            try:
                from services.storage.git_sync import git_sync_service
                asyncio.create_task(git_sync_service.sync_guide(
                    key=key,
                    title=data.get("title", "Guide"),
                    content=data.get("text", ""),
                    category=data.get("category_key", "general")
                ))
            except Exception as e:
                logger.error(f"Git sync trigger failed: {e}")

            return is_new

    @classmethod
    async def delete(cls, key: str, changed_by: int | None = None) -> dict | None:
        async with get_sessionmaker()() as session:
            result = await session.execute(select(Guide).where(Guide.key == key))
            g = result.scalar_one_or_none()
            if not g:
                return None

            snapshot = cls._to_dict(g)
            history = GuideHistory(guide_key=key, action="deleted", changed_by=changed_by, snapshot=snapshot)
            session.add(history)
            await session.delete(g)
            await session.commit()
            return snapshot

    @classmethod
    async def get_by_category(cls, category_key: str) -> list[dict]:
        return await cls.get_all(category_key=category_key)

    @classmethod
    async def get_by_tag(cls, tag: str) -> list[dict]:
        if not tag:
            return []
        async with get_sessionmaker()() as session:
            stmt = (
                select(Guide)
                .join(GuideTag, GuideTag.guide_key == Guide.key)
                .options(selectinload(Guide.tags))
                .where(GuideTag.tag == tag)
                .order_by(desc(Guide.updated_at))
            )
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

    @classmethod
    async def get_tags(cls) -> list[str]:
        async with get_sessionmaker()() as session:
            stmt = select(GuideTag.tag).distinct().order_by(GuideTag.tag.asc())
            result = await session.execute(stmt)
            return [t for t in result.scalars() if t]

    @classmethod
    async def set_tags(cls, key: str, tags: list[str]) -> bool:
        normalized = sorted({(t or "").strip().lower() for t in tags if (t or "").strip()})
        async with get_sessionmaker()() as session:
            exists = await session.execute(select(Guide.key).where(Guide.key == key))
            if exists.scalar_one_or_none() is None:
                return False
            await session.execute(delete(GuideTag).where(GuideTag.guide_key == key))
            if normalized:
                await session.execute(
                    insert(GuideTag),
                    [{"guide_key": key, "tag": t} for t in normalized],
                )
            await session.commit()
            return True

    @classmethod
    async def get_comments(cls, guide_key: str) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = (
                select(GuideComment)
                .where(GuideComment.guide_key == guide_key)
                .order_by(desc(GuideComment.created_at))
            )
            result = await session.execute(stmt)
            return [
                {
                    "id": c.id,
                    "guide_key": c.guide_key,
                    "text": c.text,
                    "created_at": c.created_at,
                    "user_id": c.user_id,
                    "first_name": c.first_name,
                    "username": c.username,
                }
                for c in result.scalars()
            ]

    @classmethod
    async def add_comment(cls, guide_key: str, user: dict, text: str) -> dict:
        async with get_sessionmaker()() as session:
            row = GuideComment(
                guide_key=guide_key,
                user_id=int(user.get("id", 0) or 0),
                username=user.get("username", ""),
                first_name=user.get("first_name", ""),
                text=text,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return {
                "id": row.id,
                "guide_key": row.guide_key,
                "text": row.text,
                "created_at": row.created_at,
                "user_id": row.user_id,
                "first_name": row.first_name,
                "username": row.username,
            }

    @classmethod
    async def delete_comment(cls, guide_key: str, comment_id: int, user: dict) -> bool:
        async with get_sessionmaker()() as session:
            result = await session.execute(
                select(GuideComment).where(
                    GuideComment.id == comment_id, GuideComment.guide_key == guide_key
                )
            )
            row = result.scalar_one_or_none()
            if not row:
                return False
            user_id = int(user.get("id", 0) or 0)
            is_admin = bool(user.get("is_local_admin") or user.get("is_admin"))
            if not is_admin and row.user_id != user_id:
                return False
            await session.delete(row)
            await session.commit()
            return True

    @classmethod
    async def record_view(cls, guide_key: str) -> None:
        async with get_sessionmaker()() as session:
            await session.execute(
                update(Guide).where(Guide.key == guide_key).values(views=Guide.views + 1)
            )
            session.add(ViewLog(guide_key=guide_key))
            await session.commit()

    @classmethod
    async def get_history(cls, guide_key: str) -> list[dict]:
        async with get_sessionmaker()() as session:
            stmt = (
                select(GuideHistory)
                .where(GuideHistory.guide_key == guide_key)
                .order_by(desc(GuideHistory.changed_at))
            )
            result = await session.execute(stmt)
            return [
                {
                    "id": h.id,
                    "guide_key": h.guide_key,
                    "action": h.action,
                    "changed_by": h.changed_by,
                    "changed_at": h.changed_at,
                    "snapshot": h.snapshot,
                }
                for h in result.scalars()
            ]

    @classmethod
    async def get_analytics(cls, days: int = 30) -> list[dict]:
        safe_days = max(1, min(int(days or 30), 365))
        since = datetime.now(timezone.utc) - timedelta(days=safe_days)
        async with get_sessionmaker()() as session:
            try:
                stmt = (
                    select(
                        func.date_trunc("day", ViewLog.viewed_at).label("day"),
                        func.count(ViewLog.id).label("count"),
                    )
                    .where(ViewLog.viewed_at >= since)
                    .group_by(func.date_trunc("day", ViewLog.viewed_at))
                    .order_by(func.date_trunc("day", ViewLog.viewed_at).asc())
                )
                result = await session.execute(stmt)
                return [
                    {"day": day.isoformat() if hasattr(day, "isoformat") else str(day), "count": int(count or 0)}
                    for day, count in result.all()
                ]
            except Exception as err:
                logger.warning(f"date_trunc analytics fallback triggered: {err}")
                stmt = select(ViewLog.viewed_at).where(ViewLog.viewed_at >= since)
                res = await session.execute(stmt)
                counts: dict[str, int] = {}
                for viewed_at in res.scalars():
                    if viewed_at:
                        day_str = viewed_at.strftime("%Y-%m-%d")
                        counts[day_str] = counts.get(day_str, 0) + 1
                return [{"day": d, "count": c} for d, c in sorted(counts.items())]

    @classmethod
    async def reorder(cls, order: list[dict]):
        if not order:
            return
        async with get_sessionmaker()() as session:
            await session.execute(update(Guide), order)
            await session.commit()

    @classmethod
    async def get_stats(cls) -> dict:
        async with get_sessionmaker()() as session:
            stmt = select(
                select(func.count(Category.key)).scalar_subquery(),
                select(func.count(Guide.key)).scalar_subquery(),
                select(func.count(Member.user_id)).scalar_subquery(),
                select(func.sum(Guide.views)).scalar_subquery(),
                select(func.count(GuideComment.id)).scalar_subquery(),
            )
            res = await session.execute(stmt)
            row = res.fetchone()
            if not row:
                return {
                    "categories": 0, "guides": 0, "members": 0, "views": 0, "comments": 0
                }
            return {
                "categories": int(row[0] or 0),
                "guides": int(row[1] or 0),
                "members": int(row[2] or 0),
                "views": int(row[3] or 0),
                "comments": int(row[4] or 0),
            }

guide_service = GuideService()

class CategoryService:
    @classmethod
    async def get_all(cls):
        async with get_sessionmaker()() as session:
            res = await session.execute(select(Category).order_by(Category.sort_order))
            return [dict(key=c.key, title=c.title, icon_url=c.icon_url, sort_order=c.sort_order) for c in res.scalars()]

    @classmethod
    async def upsert(cls, key: str, title: str, icon_url: str | None, sort_order: int):
        async with get_sessionmaker()() as session:
            stmt = insert(Category).values(key=key, title=title, icon_url=icon_url, sort_order=sort_order)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Category.key],
                set_={"title": title, "icon_url": icon_url, "sort_order": sort_order}
            )
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete(cls, key: str):
        async with get_sessionmaker()() as session:
            result = await session.execute(select(Category).where(Category.key == key))
            c = result.scalar_one_or_none()
            if not c:
                return False
            await session.delete(c)
            await session.commit()
            return True

    @classmethod
    async def reorder(cls, order: list[dict]):
        if not order:
            return
        async with get_sessionmaker()() as session:
            await session.execute(update(Category), order)
            await session.commit()

    @classmethod
    async def get_subscriptions(cls, user_id: int) -> list[str]:
        async with get_sessionmaker()() as session:
            stmt = (
                select(UserSubscription.category_key)
                .where(UserSubscription.user_id == user_id)
                .order_by(UserSubscription.category_key.asc())
            )
            result = await session.execute(stmt)
            return [k for k in result.scalars() if k]

    @classmethod
    async def subscribe(cls, user_id: int, category_key: str) -> None:
        async with get_sessionmaker()() as session:
            stmt = insert(UserSubscription).values(user_id=user_id, category_key=category_key)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[UserSubscription.user_id, UserSubscription.category_key]
            )
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def unsubscribe(cls, user_id: int, category_key: str) -> None:
        async with get_sessionmaker()() as session:
            await session.execute(
                delete(UserSubscription).where(
                    UserSubscription.user_id == user_id,
                    UserSubscription.category_key == category_key,
                )
            )
            await session.commit()

    @classmethod
    async def get_subscriber_ids(cls, category_key: str) -> list[int]:
        async with get_sessionmaker()() as session:
            stmt = select(UserSubscription.user_id).where(
                UserSubscription.category_key == category_key
            )
            result = await session.execute(stmt)
            return [int(uid) for uid in result.scalars()]

category_service = CategoryService()
