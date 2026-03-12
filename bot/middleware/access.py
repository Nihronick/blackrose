import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from config import ACCESS_MODE, ALLOWED_CHATS, ALLOWED_USERS

logger = logging.getLogger(__name__)


class AccessMiddleware(BaseMiddleware):
    def __init__(self):
        self.allowed_users = ALLOWED_USERS
        self.allowed_chats = ALLOWED_CHATS
        self.mode = ACCESS_MODE

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id if event.message else None
        else:
            return await handler(event, data)

        logger.info(f"🔒 Проверка доступа: user_id={user_id}, mode={self.mode}")

        if self.mode == "users" and user_id not in self.allowed_users:
            logger.warning(f"🚫 Доступ запрещён: user_id={user_id}")
            if isinstance(event, CallbackQuery):
                await event.answer("❌ Нет доступа", show_alert=True)
            else:
                await event.answer("❌ У вас нет доступа к этому боту.")
            return

        if self.mode == "chats" and chat_id not in self.allowed_chats:
            logger.warning(f"🚫 Доступ запрещён: chat_id={chat_id}")
            if isinstance(event, CallbackQuery):
                await event.answer("❌ Нет доступа", show_alert=True)
            else:
                await event.answer("❌ У вас нет доступа к этому боту.")
            return

        logger.info(f"✅ Доступ разрешён: user_id={user_id}")
        return await handler(event, data)
