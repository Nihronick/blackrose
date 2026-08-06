from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from core.db import get_sessionmaker
from models.db_models import Member

class MemberService:
    @classmethod
    async def list_members(cls):
        async with get_sessionmaker()() as session:
            res = await session.execute(select(Member).order_by(Member.created_at.desc()))
            return [
                {
                    "user_id": m.user_id,
                    "username": m.username,
                    "first_name": m.first_name,
                    "role": m.role,
                    "added_at": m.created_at.isoformat() if m.created_at else None,
                    "is_active": m.is_active
                }
                for m in res.scalars()
            ]

    @classmethod
    async def upsert(cls, user_id: int, username: str, first_name: str, role: str, added_by: int | None = None):
        async with get_sessionmaker()() as session:
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

    ROLE_HIERARCHY = {
        "project_admin": 5,
        "admin": 4,
        "editor": 3,
        "moderator": 2,
        "member": 1,
    }

    @classmethod
    async def get_role(cls, user_id: int) -> str:
        """Returns the global role of a user"""
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(Member.role).where(Member.user_id == user_id)
            )
            role = res.scalar_one_or_none()
            return role or "member"

    @classmethod
    async def is_moderator_or_above(cls, user_id: int) -> bool:
        role = await cls.get_role(user_id)
        return cls.ROLE_HIERARCHY.get(role, 0) >= cls.ROLE_HIERARCHY["moderator"]

    @classmethod
    async def is_editor_or_above(cls, user_id: int) -> bool:
        role = await cls.get_role(user_id)
        return cls.ROLE_HIERARCHY.get(role, 0) >= cls.ROLE_HIERARCHY["editor"]

    @classmethod
    async def update_role(cls, user_id: int, role: str) -> bool:
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(Member).where(Member.user_id == user_id)
            )
            member = res.scalar_one_or_none()
            if not member:
                return False
            member.role = role
            await session.commit()
            return True

member_service = MemberService()
