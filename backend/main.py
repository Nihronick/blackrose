import os
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from core.auth import require_user, require_admin

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

from core.middleware import backpressure_middleware
app.middleware("http")(backpressure_middleware)

from fastapi.responses import Response, PlainTextResponse
from core.metrics import metrics_registry
from core.db import get_health as get_db_health
from core.feature_flags import feature_flag_service

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

# SLI / SLO / Error Budget Dashboard
@app.get("/api/slo", tags=["metrics"])
async def get_slo():
    return metrics_registry.get_slo_report()

# Feature Flags
@app.get("/api/features", tags=["features"])
async def get_features():
    return await feature_flag_service.get_all()

@app.put("/api/admin/features", tags=["features"])
async def update_features(request: Request, user=Depends(require_admin)):
    body = await request.json()
    return await feature_flag_service.set_all(body)

# ── GDPR (EU) + 152-ФЗ (РФ): User Data Endpoints ──────────────────

@app.get("/api/user/me/export", tags=["gdpr"])
async def export_user_data(user=Depends(require_user)):
    """
    GDPR Art. 20 — Data Portability / 152-ФЗ ст. 14 — Право на получение данных.
    Returns all personal data stored about the user in JSON format.
    """
    user_id = int(user.get("id", 0))
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    from core.db import get_sessionmaker
    from sqlalchemy import select, text
    from models.db_models import UserFavorite, GuideReaction, GuildMember
    
    async with get_sessionmaker()() as session:
        # Favorites
        fav_res = await session.execute(
            select(UserFavorite.guide_key, UserFavorite.created_at)
            .where(UserFavorite.user_id == user_id)
        )
        favorites = [{"guide_key": r[0], "added_at": str(r[1])} for r in fav_res.all()]
        
        # Reactions
        react_res = await session.execute(
            select(GuideReaction.guide_key, GuideReaction.reaction, GuideReaction.created_at)
            .where(GuideReaction.user_id == user_id)
        )
        reactions = [{"guide_key": r[0], "reaction": r[1], "created_at": str(r[2])} for r in react_res.all()]
        
        # Guild membership
        guild_res = await session.execute(
            select(GuildMember.guild_id, GuildMember.rank, GuildMember.joined_at)
            .where(GuildMember.user_id == user_id)
        )
        guilds = [{"guild_id": r[0], "rank": r[1], "joined_at": str(r[2])} for r in guild_res.all()]
    
    return {
        "user_id": user_id,
        "profile": {
            "first_name": user.get("first_name"),
            "username": user.get("username"),
        },
        "favorites": favorites,
        "reactions": reactions,
        "guild_memberships": guilds,
        "exported_at": str(datetime.now(timezone.utc)),
        "legal_basis": "GDPR Art. 20 / 152-ФЗ ст. 14",
    }


@app.delete("/api/user/me", tags=["gdpr"])
async def delete_user_data(user=Depends(require_user)):
    """
    GDPR Art. 17 — Right to Erasure / 152-ФЗ ст. 21 — Право на удаление.
    Deletes all personal data associated with the user.
    """
    user_id = int(user.get("id", 0))
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    from core.db import get_sessionmaker
    from sqlalchemy import delete
    from models.db_models import UserFavorite, GuideReaction, GuildMember, GuideComment, GuildJoinRequest
    
    async with get_sessionmaker()() as session:
        await session.execute(delete(UserFavorite).where(UserFavorite.user_id == user_id))
        await session.execute(delete(GuideReaction).where(GuideReaction.user_id == user_id))
        await session.execute(delete(GuildMember).where(GuildMember.user_id == user_id))
        await session.execute(delete(GuideComment).where(GuideComment.user_id == user_id))
        await session.execute(delete(GuildJoinRequest).where(GuildJoinRequest.user_id == user_id))
        await session.commit()
    
    # Revoke all JWT tokens for this user
    await cache_service.set(f"jwt:revoke_all:{user_id}", True, expire=604800)
    
    logger.info(f"User data deleted (GDPR/152-FZ): user_id={user_id}")
    return {
        "deleted": True,
        "user_id": user_id,
        "message": "Все персональные данные удалены. Сессии отозваны.",
        "legal_basis": "GDPR Art. 17 / 152-ФЗ ст. 21",
    }


# Privacy Policy (served as JSON for SPA consumption)
@app.get("/api/legal/privacy", tags=["legal"])
async def privacy_policy():
    return {
        "title": "Политика конфиденциальности / Privacy Policy",
        "effective_date": "2026-08-22",
        "data_controller": "BlackRose Project",
        "legal_basis": ["GDPR (EU 2016/679)", "152-ФЗ (РФ)"],
        "data_collected": [
            {"type": "Telegram ID", "purpose": "Идентификация пользователя", "retention": "До удаления аккаунта"},
            {"type": "Имя и username", "purpose": "Отображение в профиле", "retention": "До удаления аккаунта"},
            {"type": "Избранные гайды", "purpose": "Персонализация", "retention": "До удаления аккаунта"},
            {"type": "Реакции и комментарии", "purpose": "Взаимодействие с контентом", "retention": "До удаления аккаунта"},
        ],
        "user_rights": [
            "Право на доступ к данным (GET /api/user/me/export)",
            "Право на удаление данных (DELETE /api/user/me)",
            "Право на отзыв согласия",
            "Право на перенос данных (JSON экспорт)",
        ],
        "third_parties": [
            {"name": "Telegram", "purpose": "Авторизация", "country": "ОАЭ"},
            {"name": "Hugging Face", "purpose": "Хостинг бэкенда", "country": "США/ЕС"},
            {"name": "Cloudflare", "purpose": "CDN и защита", "country": "США"},
        ],
        "contact": "Telegram: @nihronick",
    }


# Routers
app.include_router(public.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(webhook_ingest.router, prefix="/api")
app.include_router(guilds_router, prefix="/api")
app.include_router(discord_sync_router, prefix="/api")
app.include_router(users_admin_router, prefix="/api")
app.include_router(media_router, prefix="/api")

# API Versioning: mount all routes also under /api/v1/ for future compatibility
app.include_router(public.router, prefix="/api/v1")


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
