from fastapi import APIRouter, Depends, HTTPException
from core.auth import require_admin
from core.logging import get_logger
from pydantic import BaseModel
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


@router.delete("/synced-guides/{synced_id}")
async def remove_synced_guide(synced_id: int, delete_guide: bool = False, user=Depends(require_admin)):
    ok = await discord_sync_service.remove_synced_guide(synced_id, delete_guide=delete_guide)
    if not ok:
        raise HTTPException(status_code=404, detail="Запись в очереди не найдена")
    return {"ok": True, "message": "Запись успешно удалена из очереди"}


@router.post("/synced-guides/clear")
async def clear_synced_guides(delete_guides: bool = False, user=Depends(require_admin)):
    count = await discord_sync_service.clear_synced_guides(delete_guides=delete_guides)
    return {"ok": True, "message": f"Журнал очереди очищен (удалено записей: {count})"}


@router.post("/channels/{channel_id}/backfill")
async def backfill_channel(channel_id: str, user=Depends(require_admin)):
    active_token = stealth_discord_worker.user_token or await discord_sync_service.get_setting("discord_user_token")
    if not active_token:
        raise HTTPException(
            status_code=400,
            detail="Токен Discord не обнаружен. Нажмите 'Привязать токен' или 'Запустить слушатель'."
        )
    stealth_discord_worker.set_token(active_token)

    res = await stealth_discord_worker.fetch_channel_history(channel_id, limit=30)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error", "Ошибка загрузки истории канала"))
    return {"ok": True, "message": res.get("message", f"Сканирование канала {channel_id} успешно завершено")}


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
    total_guides = 0
    errors = []

    for ch in channels:
        ch_id = ch["channel_id"]
        res = await stealth_discord_worker.fetch_channel_history(ch_id, limit=30)
        if res.get("ok"):
            success_count += 1
            total_guides += res.get("processed", 0)
        else:
            failed_count += 1
            err_msg = res.get("error", "Неизвестная ошибка")
            errors.append(f"Канал {ch_id}: {err_msg}")

    msg = f"Сканирование завершено: {success_count} из {len(channels)} каналов успешно обработано (импортировано {total_guides} гайдов)."
    if errors:
        msg += f"\nПричины ошибок: {' | '.join(errors)}"

    return {
        "ok": True,
        "message": msg,
    }


class DiscordLinkImportIn(BaseModel):
    link: str


@router.post("/import-link")
async def import_discord_link(body: DiscordLinkImportIn, user=Depends(require_admin)):
    import re
    link = body.link.strip()
    match = re.search(r"channels/\d+/(\d+)(?:/(\d+))?", link)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="Неверная ссылка Discord. Нажмите правой кнопкой по сообщению/теме и выберите 'Копировать ссылку'."
        )

    channel_or_thread_id = match.group(1)

    active_token = stealth_discord_worker.user_token or await discord_sync_service.get_setting("discord_user_token")
    if not active_token:
        raise HTTPException(
            status_code=400,
            detail="Токен Discord не привязан. Нажмите 'Привязать токен' перед импортом по ссылке."
        )
    stealth_discord_worker.set_token(active_token)

    res = await stealth_discord_worker.fetch_channel_history(channel_or_thread_id, limit=30)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error", "Не удалось забрать гайд по ссылке"))

    return {
        "ok": True,
        "message": f"Гайд по ссылке успешно импортирован! ({res.get('message')})"
    }


@router.post("/sanitize-all-existing")
async def sanitize_all_existing(user=Depends(require_admin)):
    try:
        result = await discord_sync_service.sanitize_all_existing_guides()
        return {
            "ok": True,
            "message": f"Очистка завершена: обновлено {result.get('updated_guides')} гайдов, удалено {result.get('deleted_placeholders')} заглушек.",
            "data": result,
        }
    except Exception as e:
        logger.error(f"Error in sanitize_all_existing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка очистки: {str(e)}")


@router.post("/discover-server-channels")
async def discover_server_channels(user=Depends(require_admin)):
    """Discovers all channels, forums, and threads on accessible Discord servers."""
    active_token = stealth_discord_worker.user_token or await discord_sync_service.get_setting("discord_user_token")
    if not active_token:
        raise HTTPException(status_code=400, detail="Токен Discord не привязан")

    headers = stealth_discord_worker._build_headers()
    session = await stealth_discord_worker._get_session()
    
    # 1. Fetch guilds
    status, guilds = await stealth_discord_worker._get_json(session, "https://discord.com/api/v10/users/@me/guilds", headers)
    if status != 200 or not isinstance(guilds, list):
        return {"ok": False, "error": f"Failed to fetch guilds (HTTP {status}): {guilds}"}

    discovered = []
    for g in guilds:
        gid = g.get("id")
        gname = g.get("name")
        c_status, channels = await stealth_discord_worker._get_json(session, f"https://discord.com/api/v10/guilds/{gid}/channels", headers)
        if c_status == 200 and isinstance(channels, list):
            for c in channels:
                discovered.append({
                    "guild_id": gid,
                    "guild_name": gname,
                    "channel_id": c.get("id"),
                    "name": c.get("name"),
                    "type": c.get("type"),
                    "parent_id": c.get("parent_id"),
                    "position": c.get("position"),
                })

    return {
        "ok": True,
        "guilds_count": len(guilds),
        "channels_count": len(discovered),
        "channels": discovered,
    }




