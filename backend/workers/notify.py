"""
ARQ worker — асинхронная рассылка уведомлений о новых гайдах.
Запуск: arq workers.notify.WorkerSettings
"""

import logging
import os
from arq.connections import RedisSettings

logger = logging.getLogger("blackrose.worker")


async def send_new_guide_notifications(
    ctx: dict,
    guide_key: str,
    guide_title: str,
    category_key: str,
) -> dict:
    from services.notifications.telegram_service import _telegram_send_new_guide_notifications
    logger.info(f"[worker] notify start: guide={guide_key} category={category_key}")
    sent, total = await _telegram_send_new_guide_notifications(
        guide_key, guide_title, category_key
    )
    logger.info(f"[worker] notify done: sent={sent}/{total}")
    return {"sent": sent, "total": total}


async def startup(ctx: dict) -> None:
    from core.db import init_db
    await init_db()
    logger.info("[worker] started")


async def shutdown(ctx: dict) -> None:
    from core.db import close_pool
    from services.cache.redis_cache import close_redis
    await close_pool()
    await close_redis()
    logger.info("[worker] stopped")


class WorkerSettings:
    functions = [send_new_guide_notifications]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379"))

    # Оптимизация для Upstash Free Tier
    max_tries = 3
    job_timeout = 120
    poll_delay = 10.0  # Проверять задачи раз в 10 секунд (экономим команды Redis)
    keep_result = 600 # Хранить результат 10 минут вместо часа
    log_results = True
