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
    saved_token = await discord_sync_service.get_setting("discord_user_token")
    active_token = stealth_discord_worker.user_token or saved_token
    token_preview = f"{active_token[:10]}...••••" if active_token and len(active_token) > 10 else None
    return {
        "running": stealth_discord_worker.running,
        "channels_count": len(channels),
        "has_token": bool(active_token),
        "has_saved_token": bool(saved_token),
        "token_preview": token_preview,
    }


@router.post("/start")
async def start_worker(body: DiscordSyncTokenIn, user=Depends(require_admin)):
    token_to_use = body.user_token.strip() if body.user_token else None
    if not token_to_use:
        token_to_use = await discord_sync_service.get_setting("discord_user_token")
    
    if not token_to_use:
        raise HTTPException(status_code=400, detail="Токен Discord не указан и не найден в сохраненных настройках")

    # Permanently save to system_settings for future sessions
    if body.user_token and body.user_token.strip():
        await discord_sync_service.set_setting("discord_user_token", body.user_token.strip())

    ok = await stealth_discord_worker.start(token_to_use)
    if not ok:
        raise HTTPException(status_code=400, detail="Не удалось запустить воркер")
    return {"ok": True, "message": "Слушатель Discord успешно запущен и закреплён за вашей учётной записью"}


@router.post("/stop")
async def stop_worker(user=Depends(require_admin)):
    await stealth_discord_worker.stop()
    return {"ok": True, "message": "Слушатель Discord остановлен"}


@router.post("/clear-token")
async def clear_saved_token(user=Depends(require_admin)):
    await stealth_discord_worker.stop()
    await discord_sync_service.set_setting("discord_user_token", None)
    return {"ok": True, "message": "Сохраненный токен отвязан от учетной записи"}


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


@router.get("/synced-guides")
async def list_synced_guides(user=Depends(require_admin)):
    guides = await discord_sync_service.get_synced_guides(limit=50)
    return {"synced_guides": guides}


@router.post("/channels/{channel_id}/backfill")
async def backfill_channel(channel_id: str, user=Depends(require_admin)):
    active_token = stealth_discord_worker.user_token or await discord_sync_service.get_setting("discord_user_token")
    if not active_token:
        raise HTTPException(
            status_code=400,
            detail="Токен Discord не обнаружен. Нажмите 'Привязать токен' или 'Запустить слушатель'."
        )
    stealth_discord_worker.set_token(active_token)

    ok = await stealth_discord_worker.fetch_channel_history(channel_id, limit=30)
    if not ok:
        raise HTTPException(status_code=400, detail="Ошибка загрузки истории канала (проверьте доступ к каналу и валидность токена)")
    return {"ok": True, "message": f"Сканирование истории канала {channel_id} успешно завершено"}


@router.post("/backfill-all")
async def backfill_all_channels(user=Depends(require_admin)):
    active_token = stealth_discord_worker.user_token or await discord_sync_service.get_setting("discord_user_token")
    if not active_token:
        raise HTTPException(
            status_code=400,
            detail="Токен Discord не обнаружен. Нажмите 'Привязать токен' или 'Запустить слушатель'."
        )
    stealth_discord_worker.set_token(active_token)

    channels = await discord_sync_service.get_all_channels()
    if not channels:
        return {"ok": True, "message": "Список каналов пуст"}

    success_count = 0
    failed_count = 0

    for ch in channels:
        ch_id = ch["channel_id"]
        ok = await stealth_discord_worker.fetch_channel_history(ch_id, limit=30)
        if ok:
            success_count += 1
        else:
            failed_count += 1

    return {
        "ok": True,
        "message": f"Сканирование всех каналов завершено: {success_count} из {len(channels)} каналов успешно обработано"
    }

