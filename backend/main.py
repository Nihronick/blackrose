import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import configure_logging, RequestContextMiddleware, get_logger
from core.db import init_db, is_db_ready
from core.middleware import setup_cors, add_security_headers, setup_honeybadger
from api import admin, public, bot
from services.notifications.bot_service import bot_service
from core.http import http_client
from services.common.setup import seed_initial_admin


logger = get_logger("blackrose.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger.info("Initializing BlackRose System", version=settings.VERSION, env=settings.ENVIRONMENT)
    
    # DB Init
    await init_db()
    
    # Bot Init
    bot_service.init_bot()
    if bot_service.bot:
        webhook_base = settings.WEBHOOK_URL or (f"https://{os.getenv('SPACE_HOST')}" if os.getenv("SPACE_HOST") else "")
        if webhook_base:
            full_url = f"{webhook_base.rstrip('/')}{settings.WEBHOOK_PATH}"
            logger.info(f"Setting webhook: {full_url}")
            try:
                await bot_service.bot.set_webhook(
                    url=full_url, 
                    secret_token=settings.WEBHOOK_SECRET or None, 
                    drop_pending_updates=True,
                    request_timeout=30.0 # Explicit timeout
                )
                logger.info("Bot webhook set successfully.")
            except Exception as e:
                logger.error("Failed to set bot webhook, continuing without bot.", error=str(e))
    
    # Seeding
    await seed_initial_admin()
    
    yield
    
    # Shutdown
    logger.info("Shutting down system...")
    await bot_service.close()
    from services.cache.redis_cache import cache_service
    await cache_service.close()
    from core.db import close_pool
    await close_pool()
    await http_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Integrations & Middleware
setup_honeybadger(app)
setup_cors(app)
app.add_middleware(RequestContextMiddleware)
app.middleware("http")(add_security_headers)

# Routers
app.include_router(public.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(bot.router)

# Inngest Background Tasks
import inngest.fast_api
from core.inngest_client import inngest_client
from functions.discord_import import discord_import_guide
from functions.test_job import test_job

inngest.fast_api.serve(
    app,
    inngest_client,
    [discord_import_guide, test_job],
    serve_path="/api/inngest"
)

# Health check is handled in api/public.py as /api/health

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # In production, notify via alerts if implemented
    logger.error("unhandled_exception", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "request_id": getattr(request.state, "request_id", "unknown")}
    )

# Setup uvloop for performance on Linux
if os.name != "nt":
    try:
        import uvloop
        uvloop.install()
        logger.info("uvloop installed")
    except ImportError:
        pass

