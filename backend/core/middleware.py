from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import get_logger

logger = get_logger("blackrose.core.middleware")

def setup_cors(app: FastAPI):
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://nihronick.github.io",
    ]

    if settings.FRONTEND_URL:
        for origin_entry in settings.FRONTEND_URL.split(","):
            entry = origin_entry.strip()
            if not entry:
                continue
            parsed = urlparse(entry)
            if parsed.scheme and parsed.netloc:
                base_origin = f"{parsed.scheme}://{parsed.netloc}"
                if base_origin not in cors_origins:
                    cors_origins.append(base_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=r"https://(blackrosesl\.me|nihronick\.github\.io)|https://.*\.app\.github\.dev",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

import time
import uuid
import asyncio
from core.metrics import metrics_registry

# Backpressure: limit concurrent request processing
_concurrency_semaphore = asyncio.Semaphore(100)

async def backpressure_middleware(request: Request, call_next):
    """Graceful backpressure: queue requests during bursts, reject only on persistent overload."""
    try:
        await asyncio.wait_for(_concurrency_semaphore.acquire(), timeout=5.0)
    except asyncio.TimeoutError:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"detail": "Сервер временно перегружен. Повторите через несколько секунд."},
            headers={"Retry-After": "3"},
        )
    try:
        return await call_next(request)
    finally:
        _concurrency_semaphore.release()

async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    
    # Distributed Tracing Request ID
    req_id = request.headers.get("X-Request-ID") or f"br_{uuid.uuid4().hex[:16]}"
    request.state.request_id = req_id

    response = await call_next(request)
    
    # Latency tracking
    duration_ms = (time.time() - start_time) * 1000.0
    metrics_registry.record_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )

    # Security & WAF Headers
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https: blob:; "
        "media-src 'self' data: https: blob:; "
        "connect-src 'self' https: wss:; "
        "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org https://blackrosesl.me;"
    )
    return response


def setup_honeybadger(app: FastAPI):
    if not settings.HONEYBADGER_API_KEY:
        return
    try:
        from honeybadger import honeybadger
        from honeybadger.contrib.asgi import ASGIHoneybadger
        import honeybadger.contrib.asgi as asgi_hb
        
        # Monkey-patch to fix KeyError caused by duplicate headers
        def patched_get_headers(scope):
            headers = {}
            for raw_key, raw_value in scope.get("headers", []):
                key = raw_key.decode("latin-1").lower()
                value = raw_value.decode("latin-1")
                if key in headers:
                    headers[key] = headers[key] + ", " + value
                else:
                    headers[key] = value
            return headers
        asgi_hb._get_headers = patched_get_headers

        honeybadger.configure(api_key=settings.HONEYBADGER_API_KEY, environment=settings.ENVIRONMENT)
        app.add_middleware(ASGIHoneybadger)
        logger.info("Honeybadger enabled.")
    except ImportError:
        logger.warning("Honeybadger not installed.")
