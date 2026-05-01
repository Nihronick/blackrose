"""
BlackRose Mini App API v3.3
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from cache import close_redis
from database import close_pool, init_db
from dependencies import (
    ADMIN_USERS,
    BOT_TOKEN,
    INITIAL_ADMIN,
    hash_password,
)
from limiter import limiter
from logging_config import RequestContextMiddleware, configure_logging, get_logger
from models import NotifyIn
from routers import admin_router, public_router
from slowapi import _rate_limit_exceeded_handler
from utils import _telegram_send_new_guide_notifications

configure_logging()
logger = get_logger("blackrose")

# === Configuration / Setup Helpers ===

def setup_honeybadger(app: FastAPI) -> None:
    """Configures Honeybadger error reporting if API key is present."""
    hb_api_key = os.getenv("HONEYBADGER_API_KEY", "").strip()
    if not hb_api_key:
        return

    try:
        from honeybadger import honeybadger
        from honeybadger.contrib.asgi import ASGIHoneybadger

        honeybadger.configure(
            api_key=hb_api_key,
            environment="production",
            force_sync=False,
        )
        app.add_middleware(ASGIHoneybadger)
        logger.info("Honeybadger integration enabled.")
    except ImportError:
        logger.warning("Honeybadger is not installed. Error reporting disabled.")


def setup_cors(app: FastAPI) -> None:
    """Configures CORS middleware with default and environment-specific origins."""
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://nihronick.github.io",
    ]
    
    if frontend_url:
        from urllib.parse import urlparse
        for origin_entry in frontend_url.split(","):
            entry = origin_entry.strip()
            if not entry:
                continue
            
            # Parse and extract base origin (proto://host[:port])
            # CORS requires base origin, not full path
            parsed = urlparse(entry)
            if parsed.scheme and parsed.netloc:
                base_origin = f"{parsed.scheme}://{parsed.netloc}"
                if base_origin not in cors_origins:
                    cors_origins.append(base_origin)
                    logger.info(f"Added CORS origin: {base_origin}")

    logger.info(f"Configured CORS origins: {cors_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=r"https://(blackrosesl\.me|nihronick\.github\.io)|https://.*\.app\.github\.dev",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Telegram-Init-Data",
            "X-Bot-Token",
            "Accept",
            "Origin",
        ],
        expose_headers=["X-Request-ID"],
    )


async def seed_initial_admin() -> None:
    """Seeds initial admin users from environment variables if specified.
    
    Supports:
    - INITIAL_ADMIN=username:password (single admin, legacy)
    - INITIAL_ADMINS=admin1:pass1;admin2:pass2;admin3:pass3 (multiple admins)
    """
    from database import upsert_local_admin

    admins_to_seed = []
    
    # Support new multi-admin format
    initial_admins = os.getenv("INITIAL_ADMINS", "").strip()
    if initial_admins:
        for admin_str in initial_admins.split(";"):
            admin_str = admin_str.strip()
            if ":" in admin_str:
                admins_to_seed.append(admin_str)
    
    # Fallback to legacy INITIAL_ADMIN for backwards compatibility
    if not admins_to_seed and INITIAL_ADMIN and ":" in INITIAL_ADMIN:
        admins_to_seed.append(INITIAL_ADMIN)
    
    if not admins_to_seed:
        return
    
    logger.info("Seeding %d local admin(s)...", len(admins_to_seed))
    try:
        for admin_str in admins_to_seed:
            username, password = admin_str.split(":", 1)
            username = username.strip()
            password = password.strip()
            await upsert_local_admin(username, hash_password(password))
            logger.info("Local admin '%s' seeded successfully.", username)
    except Exception as e:
        logger.error("Failed to seed admins: %s", e, exc_info=True)


# === Lifespan & Application Definition ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("=" * 50)
    logger.info(f"BlackRose Mini App API v{app.version}")
    logger.info(f"  Admins configured: {len(ADMIN_USERS)}")
    
    await seed_initial_admin()
    
    logger.info("=" * 50)
    yield
    await close_pool()
    await close_redis()


app = FastAPI(title="BlackRose API", version="3.3.0", lifespan=lifespan)

# Setup integrations
setup_honeybadger(app)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middlewares (added in reverse order of execution)
setup_cors(app)
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(public_router, prefix="/api", tags=["public"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])


@app.post("/api/internal/notify")
async def notify_subscribers(body: NotifyIn):
    """Внутренний вызов: рассылка уведомлений при создании гайда."""
    if body.bot_token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    sent, total = await _telegram_send_new_guide_notifications(
        body.guide_key, body.guide_title, body.category_key
    )
    
    return {"success": True, "sent": sent, "total": total}
