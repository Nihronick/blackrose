from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import select, func
from core.auth import require_admin
from core.db import get_sessionmaker
from core.logging import get_logger
from models.db_models import Member

router = APIRouter(prefix="/admin/users", tags=["admin_users"])
logger = get_logger("blackrose.api.users_admin")


class UserRoleUpdateIn(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = {"project_admin", "admin", "editor", "moderator", "member"}
        if v not in valid_roles:
            raise ValueError("Недопустимая роль")
        return v


class UserStatusUpdateIn(BaseModel):
    is_active: bool


@router.get("")
async def list_users(
    query: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(require_admin),
):
    async with get_sessionmaker()() as session:
        stmt = select(Member).order_by(Member.created_at.desc())
        if query and query.strip():
            q = f"%{query.strip()}%"
            stmt = stmt.where(
                (Member.username.ilike(q)) | (Member.first_name.ilike(q))
            )
        stmt = stmt.limit(limit)
        res = await session.execute(stmt)
        members = res.scalars().all()

        total_res = await session.execute(select(func.count(Member.user_id)))
        total_count = total_res.scalar() or 0

        return {
            "total": total_count,
            "users": [
                {
                    "user_id": m.user_id,
                    "username": m.username,
                    "first_name": m.first_name,
                    "role": m.role,
                    "is_active": m.is_active,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in members
            ],
        }


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int, body: UserRoleUpdateIn, user=Depends(require_admin)
):
    async with get_sessionmaker()() as session:
        res = await session.execute(select(Member).where(Member.user_id == user_id))
        member = res.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        member.role = body.role
        await session.commit()
        logger.info(f"Admin {user['id']} updated role of user {user_id} to {body.role}")
        return {"ok": True, "user_id": user_id, "role": body.role}


@router.put("/{user_id}/status")
async def toggle_user_status(
    user_id: int, body: UserStatusUpdateIn, user=Depends(require_admin)
):
    async with get_sessionmaker()() as session:
        res = await session.execute(select(Member).where(Member.user_id == user_id))
        member = res.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        member.is_active = body.is_active
        await session.commit()
        logger.info(f"Admin {user['id']} set active status of user {user_id} to {body.is_active}")
        return {"ok": True, "user_id": user_id, "is_active": body.is_active}
