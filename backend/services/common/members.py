from sqlalchemy import select, update
from core.db import get_sessionmaker
from models.db_models import Member

class MemberService:
    @classmethod
    async def list_members(cls):
        async with get_sessionmaker()() as session:
            res = await session.execute(select(Member).order_by(Member.added_at.desc()))
            return [
                {
                    "user_id": m.user_id,
                    "username": m.username,
                    "first_name": m.first_name,
                    "role": m.role,
                    "added_at": m.added_at.isoformat() if m.added_at else None,
                    "is_active": m.is_active
                }
                for m in res.scalars()
            ]

    @classmethod
    async def upsert(cls, user_id: int, username: str, first_name: str, role: str, added_by: int | None = None):
        async with get_sessionmaker()() as session:
            from sqlalchemy.dialects.postgresql import insert
            stmt = insert(Member).values(
                user_id=user_id, username=username, first_name=first_name, role=role, added_by=added_by
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[Member.user_id],
                set_={"username": username, "first_name": first_name, "role": role, "is_active": True}
            )
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete(cls, user_id: int):
        async with get_sessionmaker()() as session:
            await session.execute(delete(Member).where(Member.user_id == user_id))
            await session.commit()

    @classmethod
    async def is_admin(cls, user_id: int) -> bool:
        async with get_sessionmaker()() as session:
            res = await session.execute(select(Member).where(Member.user_id == user_id, Member.role == "admin"))
            return res.scalar_one_or_none() is not None

member_service = MemberService()
