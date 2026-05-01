"""
Structured logging для BlackRose backend.

Использует structlog — каждый лог это JSON с полями:
  request_id, user_id, path, duration_ms, status и т.д.

Это позволяет в Sentry/Honeybadger видеть полный контекст ошибки,
а в логах Railway — искать по полям а не парсить строки.
"""

import logging
import os
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def configure_logging() -> None:
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # JSON в проде, красивый вывод локально
            structlog.dev.ConsoleRenderer()
            if os.getenv("ENVIRONMENT", "production") == "development"
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=log_level,
    )
    # Глушим шумные библиотеки
    for noisy in ("uvicorn.access", "asyncio", "aiohttp.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = "blackrose"):
    return structlog.get_logger(name)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Добавляет request_id к каждому запросу.
    Прокидывается в логи через contextvars.
    """

    async def dispatch(self, request: Request, call_next):
        import time
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Get Real IP (Hugging Face / Cloudflare support)
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host if request.client else "unknown"

        log = get_logger("blackrose.http").bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            ip=real_ip,
        )

        t0 = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - t0) * 1000, 1)

        if not request.url.path.endswith("/health"):
            log.info(
                "request",
                status=response.status_code,
                duration_ms=duration_ms,
            )

        response.headers["X-Request-ID"] = request_id
        return response
