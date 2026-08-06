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
from core.middleware import setup_cors, add_security_headers, setup_honeybadger
from api import admin, public, webhook_ingest
from api.guilds import router as guilds_router
from core.http import http_client


logger = get_logger("blackrose.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger.info("Initializing BlackRose System", version=settings.VERSION, env=settings.ENVIRONMENT)

    # DB Init
    await init_db()

    # Seeding
    await seed_initial_admin()

    yield

    # Shutdown
    logger.info("Shutting down system...")
    await cache_service.close()
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
app.include_router(webhook_ingest.router, prefix="/api")
app.include_router(guilds_router, prefix="/api")

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


if __name__ == "__main__":
    import uvicorn
    # Use string for app to support reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
