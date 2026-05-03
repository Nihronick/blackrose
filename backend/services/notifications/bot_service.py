import socket
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from core.config import settings
from core.logging import get_logger

logger = get_logger("blackrose.services.bot")

class BotService:
    def __init__(self):
        self.bot = None
        self.dp = None
        self._session = None

    def init_bot(self):
        if self.bot:
            return
        
        session = AiohttpSession(timeout=40.0)
        session._connector_init = {"family": socket.AF_INET}
        
        # Use token from settings
        token = settings.BOT_TOKEN
        if not token:
            logger.warning("BOT_TOKEN not set in config.")
            return

        self.bot = Bot(token=token, session=session)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Register routers (Lazy import to avoid cycles)
        try:
            from bot.handlers.errors import router as errors_router
            from bot.handlers.miniapp import miniapp_router
            from bot.handlers.admin import admin_router
            
            self.dp.include_router(errors_router)
            self.dp.include_router(miniapp_router)
            self.dp.include_router(admin_router)
            logger.info("Bot routers registered.")
        except ImportError as e:
            logger.error(f"Failed to import bot handlers: {e}")

    async def close(self):
        if self.bot:
            await self.bot.session.close()
        if self.dp:
            await self.dp.storage.close()

bot_service = BotService()
