from sqlalchemy import select, update, delete, desc, func, case, text
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert
import asyncio
from core.db import get_sessionmaker
from models.db_models import Guide, GuideHistory, GuideComment, Category, Member
from core.logging import get_logger

logger = get_logger("blackrose.services.guides")

class GuideService:
    @staticmethod
    def _to_dict(g: Guide) -> dict:
        if not g: return {}
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
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "views": g.views,
            "tags": [t.tag for t in g.tags] if hasattr(g, "tags") and g.tags else [],
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
        if not query or len(query) < 2: return []
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
            stmt = select(Guide).order_by(Guide.sort_order)
            if category_key:
                stmt = stmt.where(Guide.category_key == category_key)
            result = await session.execute(stmt)
            return [cls._to_dict(g) for g in result.scalars()]

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
            if not g: return None
            
            snapshot = cls._to_dict(g)
            history = GuideHistory(guide_key=key, action="deleted", changed_by=changed_by, snapshot=snapshot)
            session.add(history)
            await session.delete(g)
            await session.commit()
            return snapshot

    @classmethod
    async def reorder(cls, order: list[dict]):
        async with get_sessionmaker()() as session:
            for item in order:
                await session.execute(
                    update(Guide).where(Guide.key == item["key"]).values(sort_order=item["sort_order"])
                )
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
            if not c: return False
            await session.delete(c)
            await session.commit()
            return True

category_service = CategoryService()
