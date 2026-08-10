from fastapi import APIRouter, Depends, HTTPException
from core.auth import require_admin, require_user
from core.logging import get_logger
from models.schemas import (
    GuildIn, GuildMemberProfileIn, GuildMemberAdminIn,
    GuildJoinRequestIn, GuildStatusIn, MemberRoleIn,
)
from services.guilds.service import guild_service
from services.common.members import member_service

router = APIRouter(tags=["guilds"])
logger = get_logger("blackrose.api.guilds")

# Public endpoints (prefix /api/guilds)
@router.get("/guilds")
async def list_guilds():
    try:
        guilds = await guild_service.get_all_guilds()
        return {"guilds": guilds}
    except Exception as e:
        logger.error(f"Error in list_guilds endpoint: {e}")
        return {"guilds": []}

@router.get("/guilds/{guild_id}/roster")
async def guild_roster(guild_id: int):
    try:
        data = await guild_service.get_guild_roster(guild_id)
        if not data:
            raise HTTPException(status_code=404, detail="Гильдия не найдена")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in guild_roster: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guilds/{guild_id}/statuses")
async def guild_statuses(guild_id: int):
    try:
        statuses = await guild_service.get_guild_statuses(guild_id)
        return {"statuses": statuses}
    except Exception as e:
        logger.error(f"Error in guild_statuses: {e}")
        return {"statuses": []}

# Member self-service endpoints
@router.get("/guilds/my/profile")
async def my_profile(user=Depends(require_user)):
    profile = await guild_service.get_my_profile(user["id"])
    return {"profile": profile}

@router.put("/guilds/my/profile")
async def update_my_profile(body: GuildMemberProfileIn, user=Depends(require_user)):
    result = await guild_service.update_my_profile(user["id"], body.nickname, body.stage)
    if not result:
        raise HTTPException(status_code=404, detail="Вы не состоите в гильдии")
    return {"ok": True}

@router.post("/guilds/join")
async def join_guild(body: GuildJoinRequestIn, user=Depends(require_user)):
    result = await guild_service.create_join_request(
        user_id=user["id"], guild_id=body.guild_id,
        nickname=body.nickname, message=body.message
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"ok": True, "request_id": result["id"]}

# Guild management (master/vice/admin)
@router.get("/guilds/{guild_id}/requests")
async def guild_requests(guild_id: int, user=Depends(require_user)):
    can = await guild_service.can_manage_guild(user["id"], guild_id)
    if not can:
        raise HTTPException(status_code=403, detail="Нет прав")
    requests = await guild_service.get_pending_requests(guild_id)
    return {"requests": requests}

@router.post("/guilds/requests/{request_id}/approve")
async def approve_request(request_id: int, user=Depends(require_user)):
    result = await guild_service.approve_request(request_id, user["id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"ok": True}

@router.post("/guilds/requests/{request_id}/reject")
async def reject_request(request_id: int, user=Depends(require_user)):
    result = await guild_service.reject_request(request_id, user["id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"ok": True}

@router.put("/guilds/members/{member_id}")
async def update_member(member_id: int, body: GuildMemberAdminIn, user=Depends(require_user)):
    result = await guild_service.update_member(member_id, body, user["id"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return {"ok": True}

@router.delete("/guilds/members/{member_id}")
async def remove_member(member_id: int, user=Depends(require_user)):
    result = await guild_service.remove_member(member_id, user["id"])
    if "error" in result:
        raise HTTPException(status_code=403, detail=result["error"])
    return {"ok": True}

@router.post("/guilds/{guild_id}/statuses")
async def add_status(guild_id: int, body: GuildStatusIn, user=Depends(require_user)):
    can = await guild_service.can_manage_guild(user["id"], guild_id)
    if not can:
        raise HTTPException(status_code=403, detail="Нет прав")
    result = await guild_service.add_custom_status(guild_id, body.key, body.label, body.color)
    return {"ok": True, "status_id": result["id"]}

@router.delete("/guilds/statuses/{status_id}")
async def remove_status(status_id: int, user=Depends(require_user)):
    await guild_service.remove_custom_status(status_id)
    return {"ok": True}

# Admin-only endpoints
@router.post("/admin/guilds")
async def create_guild(body: GuildIn, user=Depends(require_admin)):
    result = await guild_service.create_guild(
        name=body.name, icon_url=body.icon_url,
        description=body.description, max_members=body.max_members
    )
    return {"ok": True, "guild_id": result["id"]}

@router.put("/admin/guilds/{guild_id}")
async def update_guild(guild_id: int, body: GuildIn, user=Depends(require_admin)):
    result = await guild_service.update_guild(guild_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Гильдия не найдена")
    return {"ok": True}

@router.delete("/admin/guilds/{guild_id}")
async def delete_guild(guild_id: int, user=Depends(require_admin)):
    result = await guild_service.delete_guild(guild_id)
    if not result:
        raise HTTPException(status_code=404, detail="Гильдия не найдена")
    return {"ok": True}

@router.put("/admin/members/{user_id}/role")
async def update_member_role(user_id: int, body: MemberRoleIn, user=Depends(require_admin)):
    ok = await member_service.update_role(user_id, body.role)
    if not ok:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"ok": True}
