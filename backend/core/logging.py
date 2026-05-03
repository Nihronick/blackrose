import logging
import os
import uuid
import structlog
from logging.handlers import RotatingFileHandler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

def configure_logging() -> None:
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Ensure logs directory exists
    log_dir = settings.LOGS_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "app.log")

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Console output for HF / Docker
    console_renderer = structlog.dev.ConsoleRenderer(colors=True) if settings.ENVIRONMENT == "development" else structlog.processors.JSONRenderer()
    
    structlog.configure(
        processors=processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Standard logging handlers
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(structlog.stdlib.ProcessorFormatter(processor=console_renderer))

    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(structlog.stdlib.ProcessorFormatter(processor=structlog.processors.JSONRenderer()))

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level)
    
    # Silence noisy libraries
    for noisy in ("uvicorn.access", "asyncio", "aiohttp.access", "inngest"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

def get_logger(name: str = "blackrose"):
    return structlog.get_logger(name)

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Adds request_id and context information to each log."""
    async def dispatch(self, request: Request, call_next):
        import time
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # HF / Cloudflare IP resolution
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        real_ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host if request.client else "unknown"

        log = get_logger("blackrose.http").bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            ip=real_ip,
        )

        t0 = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - t0) * 1000, 1)

            if not request.url.path.endswith(("/health", "/metrics")):
                log.info("request_completed", status=response.status_code, duration_ms=duration_ms)
            
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration_ms = round((time.perf_counter() - t0) * 1000, 1)
            log.error("request_failed", error=str(e), duration_ms=duration_ms)
            raise
