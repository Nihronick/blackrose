"""
BlackRose Mini App API v3.0 — PostgreSQL edition
"""
import os
import re
import time
import hmac
import hashlib
import logging
import json
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from icons import get_icon
from database import (
    init_db, close_pool, get_pool,
    get_categories, get_category, upsert_category, delete_category,
    get_guides_by_category, get_guide, upsert_guide, delete_guide,
)

# ── Logging ───────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("blackrose")

# ── Config ────────────────────────────────────────────
BOT_TOKEN        = os.getenv("BOT_TOKEN", "")
INIT_DATA_MAX_AGE = int(os.getenv("INIT_DATA_MAX_AGE", 86400))
LOG_LEVEL_STR    = os.getenv("LOG_LEVEL", "INFO")

ALLOWED_USERS_RAW = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = set()
for part in ALLOWED_USERS_RAW.replace(";", ",").split(","):
    part = part.strip()
    if part.lstrip("-").isdigit():
        ALLOWED_USERS.add(int(part))

ADMIN_USERS_RAW = os.getenv("ADMIN_USERS", "")
ADMIN_USERS: set[int] = set()
for part in ADMIN_USERS_RAW.replace(";", ",").split(","):
    part = part.strip()
    if part.lstrip("-").isdigit():
        ADMIN_USERS.add(int(part))

# If ADMIN_USERS not set — first user in ALLOWED_USERS is admin
if not ADMIN_USERS and ALLOWED_USERS:
    ADMIN_USERS = ALLOWED_USERS.copy()


# ── Guide text formatter ──────────────────────────────
def format_guide_text(text: str) -> str:
    def replace_icon(match):
        icon_name = match.group(1)
        icon_url  = get_icon(icon_name)
        return f'<img src="{icon_url}" alt="{icon_name}" width="20" height="20" style="vertical-align:middle;margin:0 4px;">'
    result = re.sub(r"\{\{(\w+)\}\}", replace_icon, text)
    result = result.replace("\n", "<br>")
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"\*(.+?)\*",   r"<em>\1</em>",           result)
    return result


# ── Telegram auth ─────────────────────────────────────
def verify_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed   = parse_qs(init_data, strict_parsing=True)
        hash_val = parsed.pop("hash", [None])[0]
        if not hash_val:
            return None
        check_string = "\n".join(
            f"{k}={v[0]}" for k, v in sorted(parsed.items())
        )
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected   = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            return None
        auth_date = int(parsed.get("auth_date", [0])[0])
        if INIT_DATA_MAX_AGE > 0 and (time.time() - auth_date) > INIT_DATA_MAX_AGE:
            return None
        user_str = parsed.get("user", [None])[0]
        return json.loads(user_str) if user_str else None
    except Exception:
        return None


async def require_telegram_user(request: Request) -> dict:
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if init_data:
        user = verify_telegram_init_data(init_data)
        if user and (not ALLOWED_USERS or user["id"] in ALLOWED_USERS):
            return user
        if user and user["id"] not in ALLOWED_USERS:
            logger.warning(f"User {user.get('id')} not in whitelist")
            raise HTTPException(status_code=403, detail="Откройте приложение через Telegram бота @blackrosesl1_bot")

    ua      = request.headers.get("user-agent", "")
    referer = request.headers.get("referer", "")
    origin  = request.headers.get("origin", "")
    is_tg   = (
        "telegram" in ua.lower()
        or "tgweb" in ua.lower()
        or "railway.app" in referer
        or "railway.app" in origin
    )
    if is_tg:
        logger.info(f"No initData but Telegram context — allowing (UA: {ua[:80]})")
        return {"id": 0, "first_name": "TelegramUser"}

    logger.warning(f"Доступ отклонён (UA: {ua[:80]})")
    raise HTTPException(status_code=403, detail="Откройте приложение через Telegram бота @blackrosesl1_bot")


async def require_admin(request: Request) -> dict:
    user = await require_telegram_user(request)
    uid  = user.get("id", 0)
    if uid != 0 and uid not in ADMIN_USERS:
        logger.warning(f"Admin access denied for user {uid}")
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user


# ── App lifecycle ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("=" * 50)
    logger.info("BlackRose Mini App API v3.0")
    logger.info(f"  Auth:      on")
    logger.info(f"  Whitelist: {len(ALLOWED_USERS)} users")
    logger.info(f"  Admins:    {len(ADMIN_USERS)} users")
    logger.info("=" * 50)
    yield
    await close_pool()


app = FastAPI(title="BlackRose API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0  = time.time()
    res = await call_next(request)
    ms  = (time.time() - t0) * 1000
    logger.info(f"{request.method} {request.url.path} → {res.status_code} ({ms:.1f}ms)")
    return res


# ── Public endpoints ──────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}


@app.get("/api/auth")
async def auth(user=Depends(require_telegram_user)):
    return {"ok": True, "user_id": user.get("id"), "name": user.get("first_name")}

_categories_cache = None
_categories_cache_time = 0
CACHE_TTL = 60  # секунд

@app.get("/api/categories")
async def categories(user=Depends(require_telegram_user)):
    global _categories_cache, _categories_cache_time
    
    now = time.time()
    if _categories_cache and (now - _categories_cache_time) < CACHE_TTL:
        return _categories_cache
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        cats = await conn.fetch("SELECT * FROM categories ORDER BY sort_order, key")
        guides = await conn.fetch(
            "SELECT key, category_key, title, icon_url FROM guides ORDER BY sort_order, key"
        )
    
    guides_by_cat = {}
    for g in guides:
        guides_by_cat.setdefault(g["category_key"], []).append({
            "key": g["key"], "title": g["title"], "icon": g["icon_url"]
        })
    
    result = [
        {"key": c["key"], "title": c["title"], "icon": c["icon_url"],
         "guides": guides_by_cat.get(c["key"], [])}
        for c in cats
    ]
    
    _categories_cache = result
    _categories_cache_time = now
    return result


@app.get("/api/guide/{key}")
async def guide(key: str, user=Depends(require_telegram_user)):
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    return {
        "key":      g["key"],
        "title":    g["title"],
        "icon":     g["icon_url"],
        "text":     format_guide_text(g["text"] or ""),
        "photo":    g["photo"] or [],
        "video":    g["video"] or [],
        "document": g["document"] or [],
    }


# ── Admin endpoints ───────────────────────────────────

class CategoryIn(BaseModel):
    title:      str
    icon_url:   Optional[str] = None
    sort_order: int = 0


class GuideIn(BaseModel):
    category_key: str
    title:        str
    icon_url:     Optional[str] = None
    text:         str = ""
    photo:        list[str] = []
    video:        list[str] = []
    document:     list[str] = []
    sort_order:   int = 0


@app.get("/api/admin/categories")
async def admin_categories(user=Depends(require_admin)):
    return await get_categories()


@app.put("/api/admin/category/{key}")
async def admin_upsert_category(key: str, body: CategoryIn, user=Depends(require_admin)):
    await upsert_category(key, body.title, body.icon_url, body.sort_order)
    return {"ok": True}


@app.delete("/api/admin/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    cat = await get_category(key)
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await delete_category(key)
    return {"ok": True}


@app.get("/api/admin/guides")
async def admin_guides(category_key: str = None, user=Depends(require_admin)):
    if category_key:
        return await get_guides_by_category(category_key)
    cats = await get_categories()
    all_guides = []
    for cat in cats:
        guides = await get_guides_by_category(cat["key"])
        all_guides.extend(guides)
    return all_guides


@app.get("/api/admin/guide/{key}")
async def admin_guide(key: str, user=Depends(require_admin)):
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    # Return raw text (not formatted) for editing
    return {**g, "photo": g["photo"] or [], "video": g["video"] or [], "document": g["document"] or []}


@app.put("/api/admin/guide/{key}")
async def admin_upsert_guide(key: str, body: GuideIn, user=Depends(require_admin)):
    await upsert_guide(
        key=key,
        category_key=body.category_key,
        title=body.title,
        icon_url=body.icon_url,
        text=body.text,
        photo=body.photo,
        video=body.video,
        document=body.document,
        sort_order=body.sort_order,
    )
    return {"ok": True}


@app.delete("/api/admin/guide/{key}")
async def admin_delete_guide(key: str, user=Depends(require_admin)):
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    await delete_guide(key)
    return {"ok": True}


@app.get("/api/admin/icons")
async def admin_icons(user=Depends(require_admin)):
    """Return list of available icon keys for the editor."""
    from icons import ICONS
    return [{"key": k, "url": v} for k, v in ICONS.items()]