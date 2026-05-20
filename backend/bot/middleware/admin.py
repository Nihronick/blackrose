from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from loguru import logger
from core.config import settings

class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        if not user or user.id not in settings.admin_user_ids:
            logger.warning(f"🚫 /admin action denied uid={user.id if user else 'Unknown'}")
            await event.answer("❌ У вас нет прав администратора.")
            return None
        return await handler(event, data)
