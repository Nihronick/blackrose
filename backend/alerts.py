import logging
import aiohttp
import asyncio
from typing import Optional
from dependencies import BOT_TOKEN

logger = logging.getLogger("blackrose.alerts")

# Cache for admin IDs to avoid circular imports or frequent DB hits
_admin_cache = set()

async def _get_admin_ids() -> set[int]:
    global _admin_cache
    if _admin_cache:
        return _admin_cache
    
    try:
        from dependencies import get_admin_users
        _admin_cache = await get_admin_users()
        return _admin_cache
    except Exception as e:
        logger.error(f"Failed to get admin ids for alerts: {e}")
        return set()

async def send_telegram_alert(message: str, level: str = "INFO"):
    """
    Sends an asynchronous alert to all admin users via Telegram Bot API.
    """
    if not BOT_TOKEN:
        logger.debug("Alert skipped: No BOT_TOKEN configured")
        return

    admin_ids = await _get_admin_ids()
    if not admin_ids:
        logger.debug("Alert skipped: No admin users found")
        return

    emoji = "🚨" if level in ("ERROR", "CRITICAL") else "⚠️" if level == "WARNING" else "ℹ️"
    full_text = f"{emoji} **BlackRose [{level}]**\n\n{message}"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for uid in admin_ids:
            tasks.append(
                session.post(url, json={
                    "chat_id": uid,
                    "text": full_text,
                    "parse_mode": "Markdown"
                })
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Failed to send alert to {list(admin_ids)[i]}: {res}")

def notify_error(message: str):
    """Fire-and-forget error notification."""
    asyncio.create_task(send_telegram_alert(message, level="ERROR"))

def notify_warning(message: str):
    """Fire-and-forget warning notification."""
    asyncio.create_task(send_telegram_alert(message, level="WARNING"))
