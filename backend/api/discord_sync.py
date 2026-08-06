from fastapi import APIRouter, Depends, HTTPException
from core.auth import require_admin
from core.logging import get_logger
from models.schemas import DiscordSyncChannelIn, DiscordSyncTokenIn
from services.discord_sync.service import discord_sync_service
from services.discord_sync.worker import stealth_discord_worker

router = APIRouter(prefix="/admin/discord-sync", tags=["discord_sync"])
logger = get_logger("blackrose.api.discord_sync")


@router.get("/status")
async def get_sync_status(user=Depends(require_admin)):
    channels = await discord_sync_service.get_all_channels()
    return {
        "running": stealth_discord_worker.running,
        "channels_count": len(channels),
        "has_token": bool(stealth_discord_worker.user_token),
    }


@router.post("/start")
async def start_worker(body: DiscordSyncTokenIn, user=Depends(require_admin)):
    ok = await stealth_discord_worker.start(body.user_token)
    if not ok:
        raise HTTPException(status_code=400, detail="Не удалось запустить воркер")
    return {"ok": True, "message": "Слушатель Discord успешно запущен"}


@router.post("/stop")
async def stop_worker(user=Depends(require_admin)):
    await stealth_discord_worker.stop()
    return {"ok": True, "message": "Слушатель Discord остановлен"}


@router.get("/channels")
async def list_channels(user=Depends(require_admin)):
    channels = await discord_sync_service.get_all_channels()
    return {"channels": channels}


@router.post("/channels")
async def add_channel(body: DiscordSyncChannelIn, user=Depends(require_admin)):
    res = await discord_sync_service.add_channel(
        channel_id=body.channel_id,
        category_key=body.category_key,
        channel_name=body.channel_name,
        auto_translate=body.auto_translate,
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return {"ok": True, "channel": res}


@router.delete("/channels/{channel_id}")
async def remove_channel(channel_id: str, user=Depends(require_admin)):
    ok = await discord_sync_service.remove_channel(channel_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Канал не найден")
    return {"ok": True}
