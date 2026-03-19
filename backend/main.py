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
import bleach
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from icons import get_icon
from database import (
    init_db, close_pool, get_pool,
    get_categories, get_category, upsert_category, delete_category,
    get_guides_by_category, get_all_guides, get_guide, upsert_guide, delete_guide,
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


# ── Bleach — разрешённые HTML-теги и атрибуты ────────
_ALLOWED_TAGS = [
    "strong", "em", "s", "u", "code", "h2", "h3",
    "blockquote", "li", "a", "img", "br", "hr",
    "span", "svg", "path", "line",
]
_ALLOWED_ATTRS = {
    "a":    ["href", "target", "rel", "class",
             "data-guide-key", "data-guide-title", "data-guide-icon"],
    "img":  ["src", "alt", "width", "height", "class", "style",
             "loading", "onerror"],
    "svg":  ["viewBox", "width", "height", "fill", "stroke",
             "stroke-width", "stroke-linecap", "class", "style"],
    "path": ["d", "fill", "stroke", "stroke-width", "stroke-linecap"],
    "line": ["x1", "y1", "x2", "x2", "stroke", "stroke-width"],
    "*":    ["class", "style"],
}

# ── Guide text formatter ──────────────────────────────
def normalize_icon_syntax(text: str) -> str:
    """
    Конвертирует :key: → {{key}} и исправляет регистр ключа.
    Примеры:
      :pilloffire:  → {{PillarOfFire}}  (регистр исправляется по ALL_ICONS)
      :Fam_HI:      → {{fam_hi}}        (нормализуется до реального ключа)
      {{pillaroffire}} → {{PillarOfFire}} (тоже исправляется)
    """
    from icons import ALL_ICONS, _ICONS_LOWER

    def resolve_key(raw: str) -> str:
        """Найти правильный ключ (с правильным регистром) или вернуть как есть."""
        if raw in ALL_ICONS:
            return raw
        return _ICONS_LOWER.get(raw.lower(), raw)

    # :key: → {{key}} с исправлением регистра
    def replace_colon(match):
        key = resolve_key(match.group(1))
        return f"{{{{{key}}}}}"

    result = re.sub(r":(\w+):", replace_colon, text)

    # {{key}} — исправить регистр если ключ известен
    def fix_curly(match):
        key = resolve_key(match.group(1))
        return f"{{{{{key}}}}}"

    result = re.sub(r"\{\{(\w+)\}\}", fix_curly, result)
    return result


async def resolve_guide_link(key: str) -> dict | None:
    """Получить заголовок и иконку гайда для кибер-ссылки."""
    try:
        g = await get_guide(key)
        if g:
            return {"title": g["title"], "icon": g["icon_url"] or ""}
    except Exception:
        pass
    return None


def format_guide_text(text: str, guide_links: dict | None = None) -> str:
    """
    Форматирует текст гайда в HTML.

    Поддерживаемый синтаксис:
      {{icon_key}}          — иконка
      [[guide_key]]         — кибер-ссылка на другой гайд (заголовок авто)
      [[guide_key|Текст]]   — кибер-ссылка с произвольным текстом
      **текст**             — жирный
      *текст*               — курсив
      ~~текст~~             — зачёркнутый
      ||текст||             — спойлер
      <u>текст</u>          — подчёркнутый
      `текст`               — моноширинный код
      ## Заголовок          — h2
      ### Заголовок         — h3
      > цитата              — blockquote
      - элемент             — маркированный список
      1. элемент            — нумерованный список
      [текст](url)          — внешняя ссылка
    """
    # guide_links: { key -> { title, icon } } — предзагруженные данные
    if guide_links is None:
        guide_links = {}

    # 1. Иконки {{key}}
    def replace_icon(match):
        icon_name = match.group(1)
        icon_url  = get_icon(icon_name)
        return f'<img src="{icon_url}" alt="{icon_name}" class="inline-icon" width="20" height="20" style="vertical-align:middle;margin:0 4px;">'
    result = re.sub(r"\{\{(\w+)\}\}", replace_icon, text)

    # 2. Кибер-ссылки [[key]] и [[key|Текст]]
    def replace_guide_link(match):
        key_part  = match.group(1)
        label_part = match.group(2)  # None если без |Текст

        if "|" in key_part:
            key, label = key_part.split("|", 1)
        else:
            key   = key_part
            label = label_part  # None

        key = key.strip()
        info = guide_links.get(key, {})
        title = info.get("title", key)
        icon  = info.get("icon", "")

        display = label.strip() if label else title

        icon_html = ""
        if icon:
            icon_html = f'<img src="{icon}" width="16" height="16" style="vertical-align:middle;margin-right:4px;border-radius:3px;">'

        return (
            f'<a class="guide-cyberlink" '
            f'data-guide-key="{key}" '
            f'data-guide-title="{title}" '
            f'data-guide-icon="{icon}" '
            f'href="#">'
            f'{icon_html}{display}'
            f'<svg class="guide-cyberlink-arrow" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="margin-left:4px;vertical-align:middle"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'
            f'</a>'
        )

    # Поддерживаем [[key]] и [[key|Текст]]
    result = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_guide_link, result)

    # 3. Блочные элементы (обрабатываем построчно)
    lines = result.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Заголовки
        if line.startswith("### "):
            out.append(f'<h3 class="guide-h3">{line[4:]}</h3>')
        elif line.startswith("## "):
            out.append(f'<h2 class="guide-h2">{line[3:]}</h2>')
        # Цитата
        elif line.startswith("> "):
            out.append(f'<blockquote class="guide-quote">{line[2:]}</blockquote>')
        # Маркированный список
        elif line.startswith("- "):
            out.append(f'<li class="guide-li guide-ul">{line[2:]}</li>')
        # Нумерованный список
        elif re.match(r"^\d+\. ", line):
            content = re.sub(r"^\d+\. ", "", line)
            out.append(f'<li class="guide-li guide-ol">{content}</li>')
        # Разделитель
        elif line.strip() == "---":
            out.append('<hr class="guide-hr">')
        # Обычная строка
        else:
            out.append(line)

        i += 1

    result = "\n".join(out)

    # 4. Инлайн-форматирование
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result, flags=re.DOTALL)
    result = re.sub(r"\*(.+?)\*",     r"<em>\1</em>",          result, flags=re.DOTALL)
    result = re.sub(r"~~(.+?)~~",     r"<s>\1</s>",            result, flags=re.DOTALL)
    result = re.sub(r"\|\|(.+?)\|\|", r'<span class="guide-spoiler">\1</span>', result, flags=re.DOTALL)
    result = re.sub(r"`(.+?)`",       r'<code class="guide-code">\1</code>', result, flags=re.DOTALL)
    result = re.sub(r"\[(.+?)\]\((https?://[^\)]+)\)", r'<a href="\2" target="_blank" rel="noreferrer" class="guide-extlink">\1</a>', result)

    # 5. Переносы строк (только для обычных строк, не блочных элементов)
    result = result.replace("\n", "<br>")

    # 6. Санитизация — убрать любые теги, не входящие в whitelist
    result = bleach.clean(
        result,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        strip=True,
    )

    return result


# ── Telegram auth ─────────────────────────────────────
def verify_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed   = parse_qs(init_data, keep_blank_values=True)
        hash_val = parsed.get("hash", [None])[0]
        if not hash_val:
            return None
        check_string = "\n".join(
            f"{k}={v[0]}" for k, v in sorted(parsed.items()) if k != "hash"
        )
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected   = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            logger.warning("HMAC mismatch")
            return None
        auth_date = int(parsed.get("auth_date", ["0"])[0])
        if INIT_DATA_MAX_AGE > 0 and (time.time() - auth_date) > INIT_DATA_MAX_AGE:
            logger.warning("initData expired")
            return None
        user_str = parsed.get("user", [None])[0]
        return json.loads(user_str) if user_str else None
    except Exception as e:
        logger.error(f"verify_telegram_init_data error: {e}")
        return None


async def require_telegram_user(request: Request) -> dict:
    init_data = request.headers.get("X-Telegram-Init-Data", "")

    if not init_data:
        logger.warning(f"Запрос без initData: {request.url.path}")
        raise HTTPException(status_code=403, detail="Откройте приложение через Telegram бота")

    user = verify_telegram_init_data(init_data)
    if not user:
        logger.warning(f"Неверные initData для {request.url.path}")
        raise HTTPException(status_code=403, detail="Неверные данные авторизации Telegram")

    if ALLOWED_USERS and user["id"] not in ALLOWED_USERS:
        logger.warning(f"User {user.get('id')} не в whitelist")
        raise HTTPException(status_code=403, detail="Откройте приложение через Telegram бота @blackrosesl1_bot")

    return user


async def require_admin(request: Request) -> dict:
    user = await require_telegram_user(request)
    uid  = user.get("id", 0)
    if uid not in ADMIN_USERS:
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

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_FRONTEND_URL = os.getenv("FRONTEND_URL", "")
_CORS_ORIGINS = [o.strip() for o in _FRONTEND_URL.split(",") if o.strip()]
# Всегда разрешаем Telegram Web и локальную разработку
_CORS_ORIGINS += [
    "https://web.telegram.org",
    "https://webk.telegram.org",
    "https://webz.telegram.org",
    "http://localhost:5173",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Telegram-Init-Data"],
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
    uid = user.get("id", 0)
    return {
        "authorized": True,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": uid in ADMIN_USERS,
    }

_categories_cache = None
_categories_cache_time = 0
CACHE_TTL = 60  # секунд

def invalidate_categories_cache():
    global _categories_cache, _categories_cache_time
    _categories_cache = None
    _categories_cache_time = 0

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

    count_by_cat = {}
    for g in guides:
        count_by_cat[g["category_key"]] = count_by_cat.get(g["category_key"], 0) + 1

    result = {
        "categories": [
            {
                "key":   c["key"],
                "title": c["title"],
                "icon":  c["icon_url"],
                "count": count_by_cat.get(c["key"], 0),
            }
            for c in cats
        ]
    }

    _categories_cache = result
    _categories_cache_time = now
    return result

@app.get("/api/category/{key}")
async def category(key: str, user=Depends(require_telegram_user)):
    guides = await get_guides_by_category(key)
    if guides is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    cat = await get_category(key)
    return {
        "category": {"key": key, "title": cat["title"] if cat else key},
        "items": [
            {
                "key":   g["key"],
                "title": g["title"],
                "icon":  g["icon_url"],
            }
            for g in guides
        ]
    }

@app.get("/api/guide/{key}")
async def guide(key: str, user=Depends(require_telegram_user)):
    import asyncio
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")

    raw_text = g["text"] or ""

    # Предзагрузка данных для кибер-ссылок [[guide_key]] и [[guide_key|Текст]]
    link_keys = list(set(k.strip() for k in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", raw_text)))

    async def load_link(k):
        info = await resolve_guide_link(k)
        return k, info or {}

    results = await asyncio.gather(*[load_link(k) for k in link_keys])
    guide_links = dict(results)

    return {
        "key":      g["key"],
        "title":    g["title"],
        "icon":     g["icon_url"],
        "text":     format_guide_text(raw_text, guide_links=guide_links),
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

    @field_validator("photo", "video", "document", mode="before")
    @classmethod
    def validate_urls(cls, v):
        if not isinstance(v, list):
            return v
        for url in v:
            if url and not url.startswith(("https://", "http://")):
                raise ValueError(f"Только http/https URL допустимы: {url!r}")
        return v

    @field_validator("icon_url", mode="before")
    @classmethod
    def validate_icon_url(cls, v):
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("icon_url должен быть http/https URL")
        return v


@app.get("/api/admin/categories")
async def admin_categories(user=Depends(require_admin)):
    return await get_categories()


@app.put("/api/admin/category/{key}")
async def admin_upsert_category(key: str, body: CategoryIn, user=Depends(require_admin)):
    await upsert_category(key, body.title, body.icon_url, body.sort_order)
    invalidate_categories_cache()
    return {"ok": True}


@app.delete("/api/admin/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    cat = await get_category(key)
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await delete_category(key)
    invalidate_categories_cache()
    return {"ok": True}


@app.get("/api/admin/guides")
async def admin_guides(category_key: str = None, user=Depends(require_admin)):
    if category_key:
        return await get_guides_by_category(category_key)
    return await get_all_guides()


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
        text=normalize_icon_syntax(body.text),
        photo=body.photo,
        video=body.video,
        document=body.document,
        sort_order=body.sort_order,
    )
    invalidate_categories_cache()
    return {"ok": True}


@app.delete("/api/admin/guide/{key}")
async def admin_delete_guide(key: str, user=Depends(require_admin)):
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    await delete_guide(key)
    invalidate_categories_cache()
    return {"ok": True}


@app.get("/api/admin/icons")
async def admin_icons(user=Depends(require_admin)):
    """Flat list of all icons for the icon picker."""
    from icons import ALL_ICONS
    return [{"key": k, "url": v} for k, v in ALL_ICONS.items()]


@app.get("/api/admin/icons/grouped")
async def admin_icons_grouped(user=Depends(require_admin)):
    """Icons grouped by category for the icon library."""
    from icons import CLASS_ETC, PROMOTION, SKILLS, SPIRIT, INFO_CATEGORIES, ADVENTURES, GUILD
    groups = [
        {"id": "class_etc",       "label": "⚔️ Классы, мечи, статы",  "icons": CLASS_ETC},
        {"id": "promotion",       "label": "🏆 Промоуты",              "icons": PROMOTION},
        {"id": "skills",          "label": "✨ Навыки",                "icons": SKILLS},
        {"id": "spirit",          "label": "👻 Духи и фамильяры",      "icons": SPIRIT},
        {"id": "adventures",      "label": "🗺️ Приключения",           "icons": ADVENTURES},
        {"id": "info_categories", "label": "📋 Категории информации",  "icons": INFO_CATEGORIES},
        {"id": "guild",           "label": "🛡️ Гильдия",              "icons": GUILD},
    ]
    return [
        {
            "id":    g["id"],
            "label": g["label"],
            "icons": [{"key": k, "url": v} for k, v in g["icons"].items()],
        }
        for g in groups
    ]


# ── Search endpoint ───────────────────────────────────
@app.get("/api/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str = "", user=Depends(require_telegram_user)):
    if not q or len(q.strip()) < 2:
        return {"results": []}
    from database import search_guides
    guides = await search_guides(q.strip())
    return {
        "results": [
            {
                "key":   g["key"],
                "title": g["title"],
                "icon":  g["icon_url"],
                "category_key": g["category_key"],
            }
            for g in guides
        ]
    }