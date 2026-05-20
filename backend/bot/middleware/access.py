import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class AccessMiddleware(BaseMiddleware):
    """
    Middleware-заглушка — сайт открыт для всех.
    Оставлен для совместимости; при необходимости можно добавить
    логику ограничения доступа.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        return await handler(event, data)
