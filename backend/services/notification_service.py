import asyncio
import logging
import os

from utils import _notify_new_guide

logger = logging.getLogger("blackrose.services.notification")

async def enqueue_guide_notification(key: str, title: str, category_key: str) -> None:
    """Организует отправку уведомления о новом гайде. 
    Использует ARQ Redis, если доступен, иначе выполняет в фоне (inline)."""
    redis_url = os.getenv("REDIS_URL", "")
    
    if redis_url:
        try:
            from arq import create_pool as arq_pool
            from arq.connections import RedisSettings

            arq_redis = await arq_pool(RedisSettings.from_dsn(redis_url))
            await arq_redis.enqueue_job(
                "send_new_guide_notifications",
                key,
                title,
                category_key,
            )
            await arq_redis.aclose()
            return
        except Exception as e:
            logger.warning(f"enqueue notify failed, fallback inline: {e}")

    # Fallback to inline background task
    asyncio.create_task(_notify_new_guide(key, title, category_key))
