import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.logging import configure_logging, RequestContextMiddleware, get_logger
from services.common.setup import seed_initial_admin
import inngest.fast_api
from core.inngest_client import inngest_client
from functions.discord_import import discord_import_guide
from services.cache.redis_cache import cache_service
from core.db import init_db, close_pool
from core.http import http_client
from core.middleware import setup_cors, add_security_headers, setup_honeybadger
from api import admin, public, webhook_ingest
from api.guilds import router as guilds_router
from api.discord_sync import router as discord_sync_router
from api.users_admin import router as users_admin_router
from api.media import router as media_router
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from core.rate_limit import limiter


logger = get_logger("blackrose.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger.info("Initializing BlackRose System", version=settings.VERSION, env=settings.ENVIRONMENT)

    if settings.JWT_SECRET == "dev_secret_key_change_me":
        logger.warning("SECURITY WARNING: JWT_SECRET is set to default development value!")

    # DB Init
    await init_db()

    # Seeding
    await seed_initial_admin()

    try:
        from services.discord_sync.service import discord_sync_service
        from services.discord_sync.worker import stealth_discord_worker
        saved_token = await discord_sync_service.get_setting("discord_user_token")
        if saved_token:
            logger.info("Auto-starting Discord Stealth Worker with saved token...")
            await stealth_discord_worker.start(saved_token)
    except Exception as err:
        logger.warning(f"Failed to auto-start Discord worker: {err}")

    # Auto-start Telegram Bot Runner for /start & inline WebApp
    try:
        from services.telegram_bot.bot_runner import telegram_bot_runner
        await telegram_bot_runner.start()
    except Exception as err:
        logger.warning(f"Failed to start Telegram Bot Runner: {err}")

    yield

    # Shutdown
    logger.info("Shutting down system...")
    try:
        from services.telegram_bot.bot_runner import telegram_bot_runner
        await telegram_bot_runner.stop()
    except Exception:
        pass
    await cache_service.close()
    await close_pool()
    await http_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Integrations & Middleware
setup_honeybadger(app)
setup_cors(app)
app.add_middleware(RequestContextMiddleware)
app.middleware("http")(add_security_headers)

from fastapi.responses import Response, PlainTextResponse
from core.metrics import metrics_registry
from core.db import get_health as get_db_health

# Kubernetes Liveness Probe
@app.get("/healthz", tags=["health"])
@app.get("/health", tags=["health"])
async def liveness_probe():
    return {"status": "ok", "version": settings.VERSION}

# Kubernetes Readiness Probe (Validates DB & Redis connections)
@app.get("/readyz", tags=["health"])
async def readiness_probe():
    db_health = await get_db_health()
    redis_health = await cache_service.ping()
    if db_health.get("status") != "healthy":
        return JSONResponse(status_code=503, content={"status": "not_ready", "db": db_health, "redis": redis_health})
    return {"status": "ready", "db": db_health, "redis": redis_health}

# Prometheus & Performance Metrics Endpoint
@app.get("/metrics", response_class=PlainTextResponse, tags=["metrics"])
@app.get("/api/metrics", tags=["metrics"])
async def get_metrics(request: Request):
    if "text/plain" in request.headers.get("accept", "") or request.url.path == "/metrics":
        return PlainTextResponse(metrics_registry.to_prometheus())
    return JSONResponse(metrics_registry.get_summary())


# Routers
app.include_router(public.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(webhook_ingest.router, prefix="/api")
app.include_router(guilds_router, prefix="/api")
app.include_router(discord_sync_router, prefix="/api")
app.include_router(users_admin_router, prefix="/api")
app.include_router(media_router, prefix="/api")

# Static files for frontend (Production)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# Inngest Background Tasks
try:
    inngest.fast_api.serve(
        app,
        inngest_client,
        [discord_import_guide],
        serve_path="/api/inngest"
    )
except Exception as e:
    logger.warning("Inngest integration disabled or failed to start (check INNGEST_SIGNING_KEY)", error=str(e))

# Health check is handled in api/public.py as /api/health

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # In production, notify via alerts if implemented
    logger.error("unhandled_exception", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error_debug": str(exc),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Setup uvloop for performance on Linux
if os.name != "nt":
    try:
        import uvloop
        uvloop.install()
        logger.info("uvloop installed")
    except ImportError:
        pass


if __name__ == "__main__":
    import uvicorn
    # Use string for app to support reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
