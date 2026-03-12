import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import ACCESS_MODE, API_TOKEN
from handlers.errors import router as errors_router
from handlers.miniapp import miniapp_router
from loguru import logger
from middleware import AccessMiddleware

# ── Логи ────────────────────────────────────────────
Path("logs").mkdir(exist_ok=True)
logger.remove()

logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan> | "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)
logger.add(
    "logs/bot_{time:YYYY-MM-DD}.log",
    rotation="00:00", retention="7 days", level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name} | {message}",
    encoding="utf-8",
)
logger.add(
    "logs/errors_{time:YYYY-MM-DD}.log",
    rotation="00:00", retention="7 days", level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name} | {message} | {exception}",
    encoding="utf-8",
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# ── Bot + Dispatcher ─────────────────────────────────
logger.info("🚀 Инициализация бота...")
bot = Bot(token=API_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

if ACCESS_MODE and ACCESS_MODE != "off":
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

dp.include_router(errors_router)
dp.include_router(miniapp_router)


# ── Lifecycle ────────────────────────────────────────
async def shutdown():
    logger.info("🛑 Завершение работы...")
    await bot.session.close()
    await dp.storage.close()
    logger.info("✅ Соединения закрыты")


async def main():
    try:
        logger.info("🚀 Запуск polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("🛑 Остановлен (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
