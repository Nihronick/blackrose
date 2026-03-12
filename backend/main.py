"""
BlackRose Mini App API v2.1
"""
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Логирование ──────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("blackrose")

if os.getenv("RAILWAY_ENVIRONMENT"):
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

sys.path.append(str(Path(__file__).parent))

from guides import CONTENT, MAIN_CATEGORIES, SUBMENUS

try:
    from icons import ALL_ICONS, get_icon
    ICONS_AVAILABLE = True
    logger.info(f"Icons loaded: {len(ALL_ICONS)}")
except ImportError:
    ICONS_AVAILABLE = False
    ALL_ICONS = {}
    logger.warning("icons.py not found — icons disabled")


# ── Конфигурация доступа ─────────────────────────────
BOT_TOKEN         = os.getenv("BOT_TOKEN", "")
INIT_DATA_MAX_AGE = int(os.getenv("INIT_DATA_MAX_AGE", "86400"))

# ALLOWED_USERS — формат: "123456789,987654321"
# Тот же список что в боте, задаётся через Railway Shared Variables
_raw = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = {
    int(uid.strip())
    for uid in _raw.split(",")
    if uid.strip().isdigit()
}

if not BOT_TOKEN:
    logger.warning("BOT_TOKEN не задан — проверка initData ОТКЛЮЧЕНА")
if ALLOWED_USERS:
    logger.info(f"Whitelist: {len(ALLOWED_USERS)} пользователей")
else:
    logger.warning("ALLOWED_USERS не задан — доступ открыт всем Telegram-пользователям")


# ── Проверка Telegram initData ───────────────────────
def verify_telegram_init_data(init_data: str) -> dict | None:
    """
    Проверяет:
    1. HMAC-подпись (данные точно от Telegram)
    2. Свежесть auth_date
    3. user_id входит в ALLOWED_USERS
    """
    if not BOT_TOKEN:
        return {"id": 0, "first_name": "Guest"}
    if not init_data:
        return None

    try:
        parsed = parse_qs(init_data, keep_blank_values=True)

        # 1. HMAC
        received_hash = parsed.get("hash", [None])[0]
        if not received_hash:
            return None

        check_pairs = [
            f"{k}={v[0]}"
            for k, v in sorted(parsed.items())
            if k != "hash"
        ]
        data_check_string = "\n".join(check_pairs)

        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            logger.warning("initData: HMAC mismatch")
            return None

        # 2. Свежесть
        if INIT_DATA_MAX_AGE > 0:
            auth_date = parsed.get("auth_date", [None])[0]
            if auth_date:
                age = time.time() - int(auth_date)
                if age > INIT_DATA_MAX_AGE:
                    logger.warning(f"initData: просрочен ({age:.0f}s)")
                    return None

        # 3. User
        user_raw = parsed.get("user", [None])[0]
        if not user_raw:
            return None
        user = json.loads(unquote(user_raw))
        user_id = user.get("id")

        # 4. Whitelist
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            logger.warning(
                f"Доступ запрещён: user_id={user_id} "
                f"({user.get('first_name', '?')}) не в ALLOWED_USERS"
            )
            return None

        logger.debug(f"initData OK: user_id={user_id} ({user.get('first_name', '?')})")
        return user

    except Exception as e:
        logger.error(f"initData error: {e}")
        return None


async def require_telegram_user(request: Request) -> dict:
    """
    Dependency для всех защищённых эндпоинтов.
    403 если: невалидная подпись / user не в whitelist / не Telegram-контекст.
    """
    if not BOT_TOKEN:
        return {"id": 0, "first_name": "Dev"}

    init_data = (
        request.headers.get("X-Telegram-Init-Data", "")
        or request.query_params.get("initData", "")
    )

    if init_data:
        user = verify_telegram_init_data(init_data)
        if user:
            return user
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён. Обратитесь к администратору гильдии.",
        )

    # Нет initData — проверяем контекст
    ua      = request.headers.get("user-agent", "")
    referer = request.headers.get("referer", "")
    origin  = request.headers.get("origin", "")

    is_tg = (
        "telegram" in ua.lower()
        or "tgweb" in ua.lower()
        or "railway.app" in referer
        or "railway.app" in origin
    )

    if is_tg:
        logger.info(f"No initData but Telegram context — allowing (UA: {ua[:80]})")
        return {"id": 0, "first_name": "TelegramUser"}

    logger.warning(f"Доступ отклонён (UA: {ua[:80]})")
    raise HTTPException(
        status_code=403,
        detail="Откройте приложение через Telegram бота @blackrosesl1_bot",
    )


# ── App ──────────────────────────────────────────────
app = FastAPI(title="BlackRose Mini App API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*", "X-Telegram-Init-Data"],
)

guide_stats: dict[str, int] = {}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    ms = (time.time() - start) * 1000
    if request.url.path != "/":
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({ms:.1f}ms)")
    return response


# ── Helpers ──────────────────────────────────────────
def resolve_icon(icon_raw: str | None) -> str | None:
    if not icon_raw or not ICONS_AVAILABLE:
        return None
    if icon_raw.startswith("http"):
        return icon_raw
    return get_icon(icon_raw) if icon_raw in ALL_ICONS else None


def format_guide_text(text: str) -> str:
    if not text:
        return ""
    html = text
    if ICONS_AVAILABLE:
        def replace_icon(m):
            url = get_icon(m.group(1).strip())
            if url:
                return f'<img src="{url}" alt="{m.group(1)}" class="inline-icon" onerror="this.style.display=\'none\'">'
            return ""
        html = re.sub(r"\{\{(\w+(?:\s+\w+)*)\}\}", replace_icon, html)
    else:
        html = re.sub(r"\{\{(\w+(?:\s+\w+)*)\}\}", "", html)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = html.replace("\n", "<br>")
    html = re.sub(r"(<br>\s*){3,}", "<br><br>", html)
    return html


def extract_media(media) -> list[str]:
    if not media:
        return []
    if isinstance(media, list):
        return [i for i in media if i and isinstance(i, str) and i not in ("None", "")]
    if isinstance(media, str) and media not in ("None", ""):
        return [media]
    return []


# ── Routes ───────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": "2.1.0",
        "auth": bool(BOT_TOKEN),
        "whitelist": len(ALLOWED_USERS),
    }


@app.get("/api/auth")
async def check_auth(user: dict = Depends(require_telegram_user)):
    return {"authorized": True, "user_id": user.get("id"), "first_name": user.get("first_name", "")}


@app.get("/api/categories")
def get_categories(user: dict = Depends(require_telegram_user)):
    result = []
    for key, data in MAIN_CATEGORIES.items():
        title    = data["title"] if isinstance(data, dict) else data
        icon_raw = data.get("icon") if isinstance(data, dict) else None
        result.append({
            "key":   key,
            "title": title,
            "icon":  resolve_icon(icon_raw),
            "count": len(SUBMENUS.get(key, [])),
        })
    return {"categories": result}


@app.get("/api/category/{category_key}")
async def get_category(category_key: str, user: dict = Depends(require_telegram_user)):
    if category_key not in SUBMENUS:
        raise HTTPException(404, detail="Category not found")

    items = []
    for item in SUBMENUS[category_key]:
        key, title = item[0], item[1]
        icon_raw   = item[2] if len(item) >= 3 else None
        guide      = CONTENT.get(key, {})
        preview    = re.sub(r"\{\{.*?\}\}", "", guide.get("text", "")[:150]).strip()
        preview    = re.sub(r"\*\*(.+?)\*\*", r"\1", preview)
        items.append({
            "key":          key,
            "title":        title,
            "icon":         resolve_icon(icon_raw),
            "preview":      (preview + "...") if preview else "",
            "has_photo":    bool(guide.get("photo")),
            "has_video":    bool(guide.get("video")),
            "has_document": bool(guide.get("document")),
        })

    cat   = MAIN_CATEGORIES.get(category_key, {})
    title = cat["title"] if isinstance(cat, dict) else cat
    return {"category": {"key": category_key, "title": title}, "items": items}


@app.get("/api/guide/{guide_key}")
async def get_guide(guide_key: str, user: dict = Depends(require_telegram_user)):
    guide = CONTENT.get(guide_key)
    if not guide:
        raise HTTPException(404, detail="Guide not found")
    guide_stats[guide_key] = guide_stats.get(guide_key, 0) + 1
    return {
        "key":      guide_key,
        "title":    guide.get("title", guide_key),
        "icon":     resolve_icon(guide.get("icon")),
        "text":     format_guide_text(guide.get("text", "")),
        "photo":    extract_media(guide.get("photo")),
        "video":    extract_media(guide.get("video")),
        "document": extract_media(guide.get("document")),
        "views":    guide_stats[guide_key],
    }


@app.get("/api/search")
async def search_guides(q: str = Query(min_length=2), user: dict = Depends(require_telegram_user)):
    query   = q.lower().strip()
    results = []
    for key, guide in CONTENT.items():
        title = guide.get("title", key)
        if query in key.lower() or query in title.lower() or query in guide.get("text", "").lower():
            preview = re.sub(r"\{\{.*?\}\}", "", guide.get("text", "")[:150]).strip()
            results.append({"key": key, "title": title, "icon": resolve_icon(guide.get("icon")), "preview": preview + "..."})
    return {"results": results[:10]}


@app.get("/api/stats")
async def get_stats():
    return {"total_guides": len(CONTENT), "total_categories": len(MAIN_CATEGORIES), "total_views": sum(guide_stats.values())}


# ── Startup ──────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("=" * 50)
    logger.info("BlackRose Mini App API v2.1.0")
    logger.info(f"  Guides:     {len(CONTENT)}")
    logger.info(f"  Icons:      {len(ALL_ICONS) if ICONS_AVAILABLE else 'disabled'}")
    logger.info(f"  Auth:       {'on' if BOT_TOKEN else 'OFF'}")
    logger.info(f"  Whitelist:  {len(ALLOWED_USERS)} users" if ALLOWED_USERS else "  Whitelist:  OFF")
    logger.info("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=not os.getenv("RAILWAY_ENVIRONMENT"),
        log_level="info",
    )