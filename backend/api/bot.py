from fastapi import APIRouter, Request, HTTPException
from aiogram import types
from core.config import settings
from core.logging import get_logger
from services.notifications.bot_service import bot_service

router = APIRouter(tags=["bot"])
logger = get_logger("blackrose.api.bot")

@router.post(settings.WEBHOOK_PATH)
async def bot_webhook(request: Request):
    """Endpoint for Telegram Webhooks."""
    if settings.WEBHOOK_SECRET:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.WEBHOOK_SECRET:
            logger.warning("Unauthorized webhook request (invalid secret token)")
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        if not bot_service.bot or not bot_service.dp:
            raise HTTPException(status_code=503, detail="Bot not initialized")

        update_data = await request.json()
        update = types.Update(**update_data)
        await bot_service.dp.feed_update(bot_service.bot, update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing bot update: {e}", exc_info=True)
        # Return 200 to Telegram to prevent retry loops
        return {"status": "error", "detail": str(e)}
