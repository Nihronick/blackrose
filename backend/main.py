"""
BlackRose Mini App API v3.1
Changes vs v3.0:
  - /api/category/{key} now returns preview + has_photo/video/document per guide
  - /api/admin/guide/{key} DELETE passes changed_by to audit log
  - /api/admin/guide/{key}/history — audit log endpoint
  - /api/admin/reorder/guides and /api/admin/reorder/categories — drag-and-drop
  - /api/admin/export — full JSON export
  - /api/admin/import — full JSON import
  - /api/search uses new FTS-based search_guides
  - upsert_guide passes user id as changed_by
"""

import asyncio as _asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import time
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

import aiohttp
import nh3
from cache import (
    close_redis,
    get_categories_cache,
    get_guide_cache,
    invalidate_all,
    invalidate_guide_cache,
    set_categories_cache,
    set_guide_cache,
)
from database import (
    add_comment,
    close_pool,
    delete_category,
    delete_comment,
    delete_guide,
    export_all,
    get_all_guides,
    get_all_tags,
    get_categories,
    get_category,
    get_comments,
    get_guide,
    get_guide_history,
    get_guide_tags,
    get_guides_by_category,
    get_guides_by_tag,
    get_pool,
    get_subscribers,
    get_top_guides,
    get_user_subscriptions,
    import_guides,
    increment_views,
    init_db,
    reorder_categories,
    reorder_guides,
    set_guide_tags,
    subscribe,
    unsubscribe,
    upsert_category,
    upsert_guide,
)
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from icons import get_icon
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("blackrose")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
INIT_DATA_MAX_AGE = int(os.getenv("INIT_DATA_MAX_AGE", 86400))
BOT_NOTIFY_URL = os.getenv("BOT_NOTIFY_URL", "")  # URL самого бота для webhook-нотификаций


async def _notify_new_guide(guide_key: str, guide_title: str, category_key: str) -> None:
    """Fire-and-forget: tell the bot to push notifications to category subscribers."""
    if not BOT_NOTIFY_URL or not BOT_TOKEN:
        return
    try:
        payload = {
            "guide_key": guide_key,
            "guide_title": guide_title,
            "category_key": category_key,
            "bot_token": BOT_TOKEN,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BOT_NOTIFY_URL}/api/internal/notify",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as r:
                if r.status != 200:
                    logger.warning(f"notify webhook status={r.status}")
    except Exception as e:
        logger.warning(f"_notify_new_guide failed: {e}")


def _parse_ids(raw: str) -> set[int]:
    s: set[int] = set()
    for p in raw.replace(";", ",").split(","):
        p = p.strip()
        if p.lstrip("-").isdigit():
            s.add(int(p))
    return s


ALLOWED_USERS = _parse_ids(os.getenv("ALLOWED_USERS", ""))
ADMIN_USERS = _parse_ids(os.getenv("ADMIN_USERS", ""))

# ── Bleach whitelist ──────────────────────────────────
# nh3 uses sets, not lists; wildcard "*" is not supported — use tag_attribute_values
# IMPORTANT: nh3 controls <a rel="..."> via the separate link_rel= parameter.
# Adding "rel" to attributes["a"] causes a Rust-level panic in ammonia.
_ALLOWED_TAGS: set[str] = {
    "strong",
    "em",
    "s",
    "u",
    "code",
    "h2",
    "h3",
    "blockquote",
    "li",
    "a",
    "img",
    "br",
    "hr",
    "span",
    "svg",
    "path",
    "line",
}
_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href", "target", "class", "data-guide-key", "data-guide-title", "data-guide-icon"},
    "img": {"src", "alt", "width", "height", "class", "style", "loading"},
    "svg": {
        "viewBox",
        "width",
        "height",
        "fill",
        "stroke",
        "stroke-width",
        "stroke-linecap",
        "class",
        "style",
    },
    "path": {"d", "fill", "stroke", "stroke-width", "stroke-linecap"},
    "line": {"x1", "y1", "x2", "stroke", "stroke-width"},
    "strong": {"class", "style"},
    "em": {"class", "style"},
    "s": {"class", "style"},
    "u": {"class", "style"},
    "code": {"class", "style"},
    "h2": {"class", "style"},
    "h3": {"class", "style"},
    "blockquote": {"class", "style"},
    "li": {"class", "style"},
    "br": {"class"},
    "hr": {"class"},
    "span": {"class", "style"},
}


# ── Text formatting ───────────────────────────────────
def normalize_icon_syntax(text: str) -> str:
    from icons import _ICONS_LOWER, ALL_ICONS

    def resolve_key(raw: str) -> str:
        if raw in ALL_ICONS:
            return raw
        return _ICONS_LOWER.get(raw.lower(), raw)

    result = re.sub(r":(\w+):", lambda m: f"{{{{{resolve_key(m.group(1))}}}}}", text)
    result = re.sub(r"\{\{(\w+)\}\}", lambda m: f"{{{{{resolve_key(m.group(1))}}}}}", result)
    return result


async def resolve_guide_links_bulk(keys: list[str]) -> dict[str, dict]:
    """Batch-fetch guide meta for [[key]] links — one query instead of N."""
    if not keys:
        return {}
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT key, title, icon_url FROM guides WHERE key = ANY($1::text[])",
                keys,
            )
        return {r["key"]: {"title": r["title"], "icon": r["icon_url"] or ""} for r in rows}
    except Exception as e:
        logger.warning(f"resolve_guide_links_bulk: {e}")
        return {}


def format_guide_text(text: str, guide_links: dict | None = None) -> str:
    if guide_links is None:
        guide_links = {}

    def replace_icon(match):
        icon_name = match.group(1)
        icon_url = get_icon(icon_name)
        return (
            f'<img src="{icon_url}" alt="{icon_name}" class="inline-icon" '
            f'width="20" height="20" style="vertical-align:middle;margin:0 4px;">'
        )

    result = re.sub(r"\{\{(\w+)\}\}", replace_icon, text)

    def replace_guide_link(match):
        key_part = match.group(1)
        label_part = match.group(2)
        if "|" in key_part:
            key, label = key_part.split("|", 1)
        else:
            key = key_part
            label = label_part
        key = key.strip()
        info = guide_links.get(key, {})
        title = info.get("title", key)
        icon = info.get("icon", "")
        display = label.strip() if label else title
        icon_html = (
            f'<img src="{icon}" width="16" height="16" '
            f'style="vertical-align:middle;margin-right:4px;border-radius:3px;">'
            if icon
            else ""
        )
        return (
            f'<a class="guide-cyberlink" data-guide-key="{key}" '
            f'data-guide-title="{title}" data-guide-icon="{icon}" href="#">'
            f"{icon_html}{display}"
            f'<svg class="guide-cyberlink-arrow" viewBox="0 0 16 16" width="12" height="12" '
            f'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'style="margin-left:4px;vertical-align:middle">'
            f'<path d="M3 8h10M9 4l4 4-4 4"/></svg></a>'
        )

    result = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_guide_link, result)

    lines = result.split("\n")
    out = []
    for line in lines:
        if line.startswith("### "):
            out.append(f'<h3 class="guide-h3">{line[4:]}</h3>')
        elif line.startswith("## "):
            out.append(f'<h2 class="guide-h2">{line[3:]}</h2>')
        elif line.startswith("> "):
            out.append(f'<blockquote class="guide-quote">{line[2:]}</blockquote>')
        elif line.startswith("- "):
            out.append(f'<li class="guide-li guide-ul">{line[2:]}</li>')
        elif re.match(r"^\d+\. ", line):
            content = re.sub(r"^\d+\. ", "", line)
            out.append(f'<li class="guide-li guide-ol">{content}</li>')
        elif line.strip() == "---":
            out.append('<hr class="guide-hr">')
        else:
            out.append(line)
    result = "\n".join(out)

    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result, flags=re.DOTALL)
    result = re.sub(r"\*(.+?)\*", r"<em>\1</em>", result, flags=re.DOTALL)
    result = re.sub(r"~~(.+?)~~", r"<s>\1</s>", result, flags=re.DOTALL)
    result = re.sub(
        r"\|\|(.+?)\|\|", r'<span class="guide-spoiler">\1</span>', result, flags=re.DOTALL
    )
    result = re.sub(r"`(.+?)`", r'<code class="guide-code">\1</code>', result, flags=re.DOTALL)
    result = re.sub(
        r"\[(.+?)\]\((https?://[^\)]+)\)",
        r'<a href="\2" target="_blank" rel="noreferrer" class="guide-extlink">\1</a>',
        result,
    )
    result = result.replace("\n", "<br>")
    result = nh3.clean(
        result,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        link_rel="noreferrer",  # nh3 sets rel on <a> via this param, not attributes
    )
    return result


# ── Telegram auth ─────────────────────────────────────
def verify_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        hash_val = parsed.get("hash", [None])[0]
        if not hash_val:
            return None
        check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed.items()) if k != "hash")
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            return None
        auth_date = int(parsed.get("auth_date", ["0"])[0])
        if INIT_DATA_MAX_AGE > 0 and (time.time() - auth_date) > INIT_DATA_MAX_AGE:
            return None
        user_str = parsed.get("user", [None])[0]
        return json.loads(user_str) if user_str else None
    except Exception as e:
        logger.error(f"verify_telegram_init_data: {e}")
        return None


async def require_telegram_user(request: Request) -> dict:
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if not init_data:
        raise HTTPException(status_code=403, detail="Откройте приложение через Telegram бота")
    user = verify_telegram_init_data(init_data)
    if not user:
        raise HTTPException(status_code=403, detail="Неверные данные авторизации Telegram")
    if ALLOWED_USERS and user["id"] not in ALLOWED_USERS:
        raise HTTPException(
            status_code=403, detail="Откройте приложение через Telegram бота @blackrosesl1_bot"
        )
    return user


async def require_admin(request: Request) -> dict:
    user = await require_telegram_user(request)
    if user.get("id", 0) not in ADMIN_USERS:
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user


# ── App ───────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("=" * 50)
    logger.info("BlackRose Mini App API v3.1")
    logger.info(f"  Whitelist: {len(ALLOWED_USERS)} users | Admins: {len(ADMIN_USERS)}")
    logger.info("=" * 50)
    yield
    await close_pool()
    await close_redis()


app = FastAPI(title="BlackRose API", version="3.1.0", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_FRONTEND_URL = os.getenv("FRONTEND_URL", "")
_CORS_ORIGINS = [o.strip() for o in _FRONTEND_URL.split(",") if o.strip()]
_CORS_ORIGINS += [
    "https://web.telegram.org",
    "https://webk.telegram.org",
    "https://webz.telegram.org",
    "http://localhost:5173",
    "http://localhost:3000",
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
    t0 = time.time()
    res = await call_next(request)
    ms = (time.time() - t0) * 1000
    logger.info(f"{request.method} {request.url.path} → {res.status_code} ({ms:.1f}ms)")
    return res


# ── Public endpoints ──────────────────────────────────


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.1.0"}


@app.get("/api/auth")
async def auth(user=Depends(require_telegram_user)):
    uid = user.get("id", 0)
    return {
        "authorized": True,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": uid in ADMIN_USERS,
    }


# ── Cache helpers (Redis-backed, see cache.py) ────────────────
_cache_lock = _asyncio.Lock()


async def _invalidate_cache():
    await invalidate_all()


async def _invalidate_guide_cache_key(key: str):
    await invalidate_guide_cache(key)


@app.get("/api/categories")
async def categories(user=Depends(require_telegram_user)):
    cached = await get_categories_cache()
    if cached:
        return cached

    async with _cache_lock:
        cached = await get_categories_cache()
        if cached:
            return cached

        pool = await get_pool()
        async with pool.acquire() as conn:
            cats = await conn.fetch("SELECT * FROM categories ORDER BY sort_order, key")
            guides = await conn.fetch("SELECT key, category_key FROM guides")

        count_by_cat: dict[str, int] = {}
        for g in guides:
            count_by_cat[g["category_key"]] = count_by_cat.get(g["category_key"], 0) + 1

        result = {
            "categories": [
                {
                    "key": c["key"],
                    "title": c["title"],
                    "icon": c["icon_url"],
                    "count": count_by_cat.get(c["key"], 0),
                }
                for c in cats
            ]
        }
        await set_categories_cache(result)
        return result


@app.get("/api/category/{key}")
async def category(key: str, user=Depends(require_telegram_user)):
    cat = await get_category(key)
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    guides = await get_guides_by_category(key)
    return {
        "category": {"key": key, "title": cat["title"]},
        "items": [
            {
                "key": g["key"],
                "title": g["title"],
                "icon": g["icon_url"],
                "preview": g["preview"],
                "has_photo": g["has_photo"],
                "has_video": g["has_video"],
                "has_document": g["has_document"],
                "views": g.get("views") or 0,
                "tags": g.get("tags") or [],
            }
            for g in guides
        ],
    }


@app.get("/api/guide/{key}")
async def guide(key: str, user=Depends(require_telegram_user)):
    cached = await get_guide_cache(key)
    if cached:
        return cached

    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")

    raw_text = g["text"] or ""
    link_keys = list(
        set(k.strip() for k in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", raw_text))
    )

    guide_links = await resolve_guide_links_bulk(link_keys)

    import asyncio

    formatted_text = await asyncio.to_thread(format_guide_text, raw_text, guide_links=guide_links)

    tags = await get_guide_tags(key)
    result = {
        "key": g["key"],
        "title": g["title"],
        "icon": g["icon_url"],
        "text": formatted_text,
        "photo": g["photo"] or [],
        "video": g["video"] or [],
        "document": g["document"] or [],
        "views": g.get("views") or 0,
        "tags": tags,
    }
    await set_guide_cache(key, result)
    return result


# ── Search ────────────────────────────────────────────


@app.get("/api/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str = "", user=Depends(require_telegram_user)):
    if not q or len(q.strip()) < 2:
        return {"results": []}
    from database import search_guides as db_search

    guides = await db_search(q.strip())
    return {
        "results": [
            {
                "key": g["key"],
                "title": g["title"],
                "icon": g["icon_url"],
                "category_key": g["category_key"],
            }
            for g in guides
        ]
    }


# ── Preview endpoint (admin live preview) ────────────────────


class PreviewIn(BaseModel):
    text: str = ""


@app.post("/api/guide/__preview__")
async def preview_guide(body: PreviewIn, user=Depends(require_telegram_user)):
    """Server-side render for admin live preview."""
    import asyncio

    html = await asyncio.to_thread(format_guide_text, body.text, guide_links={})
    return {"html": html}


# ── Admin: Pydantic models ────────────────────────────

_KEY_RE = re.compile(r"^[a-z0-9_-]{1,64}$")


def _validate_key(v: str) -> str:
    if not _KEY_RE.match(v):
        raise HTTPException(
            status_code=422,
            detail="Ключ должен содержать только строчные буквы, цифры, _ и - (до 64 символов)",
        )
    return v


class CategoryIn(BaseModel):
    title: str
    icon_url: str | None = None
    sort_order: int = 0

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()


class GuideIn(BaseModel):
    category_key: str
    title: str
    icon_url: str | None = None
    text: str = ""
    photo: list[str] = []
    video: list[str] = []
    document: list[str] = []
    sort_order: int = 0

    @field_validator("category_key")
    @classmethod
    def validate_category_key(cls, v):
        return _validate_key(v)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Название не может быть пустым")
        return v.strip()

    @field_validator("photo", "video", "document", mode="before")
    @classmethod
    def validate_urls(cls, v):
        if not isinstance(v, list):
            return v
        for url in v:
            if url and not url.startswith(("https://", "http://")):
                raise ValueError(f"Только http/https URL: {url!r}")
        return v

    @field_validator("icon_url", mode="before")
    @classmethod
    def validate_icon_url(cls, v):
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("icon_url должен быть http/https URL")
        return v


class ReorderItem(BaseModel):
    key: str
    sort_order: int


class ReorderIn(BaseModel):
    order: list[ReorderItem]


# ── Admin: Categories ─────────────────────────────────


@app.get("/api/admin/categories")
async def admin_categories(user=Depends(require_admin)):
    return await get_categories()


@app.put("/api/admin/category/{key}")
async def admin_upsert_category(key: str, body: CategoryIn, user=Depends(require_admin)):
    _validate_key(key)
    await upsert_category(key, body.title, body.icon_url, body.sort_order)
    await _invalidate_cache()
    return {"ok": True}


@app.delete("/api/admin/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    if not await get_category(key):
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await delete_category(key)
    await _invalidate_cache()
    return {"ok": True}


@app.post("/api/admin/reorder/categories")
async def admin_reorder_categories(body: ReorderIn, user=Depends(require_admin)):
    await reorder_categories([{"key": i.key, "sort_order": i.sort_order} for i in body.order])
    await _invalidate_cache()
    return {"ok": True}


# ── Admin: Guides ─────────────────────────────────────


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
    return {
        **g,
        "photo": g["photo"] or [],
        "video": g["video"] or [],
        "document": g["document"] or [],
    }


@app.put("/api/admin/guide/{key}")
async def admin_upsert_guide(key: str, body: GuideIn, user=Depends(require_admin)):
    _validate_key(key)
    is_new = not await get_guide(key)
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
        changed_by=user.get("id"),
    )
    await _invalidate_cache()
    await _invalidate_guide_cache_key(key)
    if is_new:
        import asyncio

        asyncio.create_task(_notify_new_guide(key, body.title, body.category_key))
    return {"ok": True, "created": is_new}


@app.delete("/api/admin/guide/{key}")
async def admin_delete_guide(key: str, user=Depends(require_admin)):
    if not await get_guide(key):
        raise HTTPException(status_code=404, detail="Гайд не найден")
    await delete_guide(key, changed_by=user.get("id"))
    await _invalidate_cache()
    return {"ok": True}


@app.post("/api/admin/reorder/guides")
async def admin_reorder_guides(body: ReorderIn, user=Depends(require_admin)):
    await reorder_guides([{"key": i.key, "sort_order": i.sort_order} for i in body.order])
    await _invalidate_cache()
    return {"ok": True}


@app.get("/api/admin/guide/{key}/history")
async def admin_guide_history(key: str, user=Depends(require_admin)):
    rows = await get_guide_history(key)
    return {
        "history": [
            {
                "id": r["id"],
                "action": r["action"],
                "changed_by": r["changed_by"],
                "changed_at": r["changed_at"].isoformat() if r["changed_at"] else None,
                "snapshot": r["snapshot"],
            }
            for r in rows
        ]
    }


# ── Admin: Export / Import ────────────────────────────


@app.get("/api/admin/export")
async def admin_export(user=Depends(require_admin)):
    data = await export_all()
    return JSONResponse(
        content=data, headers={"Content-Disposition": "attachment; filename=blackrose-export.json"}
    )


@app.post("/api/admin/import")
async def admin_import(request: Request, user=Depends(require_admin)):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Неверный JSON")
    if "categories" not in data or "guides" not in data:
        raise HTTPException(status_code=400, detail="Неверный формат файла")
    try:
        stats = await import_guides(data, changed_by=user.get("id"))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await _invalidate_cache()
    logger.info(f"Import by {user.get('id')}: {stats}")
    return {"ok": True, **stats}


# ── Admin: Icons ──────────────────────────────────────


@app.get("/api/admin/icons")
async def admin_icons(user=Depends(require_admin)):
    from icons import ALL_ICONS

    return [{"key": k, "url": v} for k, v in ALL_ICONS.items()]


@app.get("/api/admin/icons/grouped")
async def admin_icons_grouped(user=Depends(require_admin)):
    from icons import ADVENTURES, CLASS_ETC, GUILD, INFO_CATEGORIES, PROMOTION, SKILLS, SPIRIT

    groups = [
        {"id": "class_etc", "label": "⚔️ Классы, мечи, статы", "icons": CLASS_ETC},
        {"id": "promotion", "label": "🏆 Промоуты", "icons": PROMOTION},
        {"id": "skills", "label": "✨ Навыки", "icons": SKILLS},
        {"id": "spirit", "label": "👻 Духи и фамильяры", "icons": SPIRIT},
        {"id": "adventures", "label": "🗺️ Приключения", "icons": ADVENTURES},
        {"id": "info_categories", "label": "📋 Категории информации", "icons": INFO_CATEGORIES},
        {"id": "guild", "label": "🛡️ Гильдия", "icons": GUILD},
    ]
    return [
        {
            "id": g["id"],
            "label": g["label"],
            "icons": [{"key": k, "url": v} for k, v in g["icons"].items()],
        }
        for g in groups
    ]


# ════════════════════════════════════════════════════════════════
# TAGS
# ════════════════════════════════════════════════════════════════


@app.get("/api/tags")
async def tags_list(user=Depends(require_telegram_user)):
    return {"tags": await get_all_tags()}


@app.get("/api/tag/{tag}")
async def guides_by_tag(tag: str, user=Depends(require_telegram_user)):
    return {"tag": tag, "results": await get_guides_by_tag(tag.lower())}


# ════════════════════════════════════════════════════════════════
# VIEWS
# ════════════════════════════════════════════════════════════════


@app.post("/api/guide/{key}/view")
@limiter.limit("60/minute")
async def record_view(request: Request, key: str, user=Depends(require_telegram_user)):
    views = await increment_views(key)
    await _invalidate_guide_cache_key(key)
    return {"views": views}


@app.get("/api/top")
async def top_guides(user=Depends(require_telegram_user)):
    return {"results": await get_top_guides(limit=10)}


# ════════════════════════════════════════════════════════════════
# COMMENTS
# ════════════════════════════════════════════════════════════════


class CommentIn(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Комментарий не может быть пустым")
        if len(v) > 1000:
            raise ValueError("Комментарий слишком длинный (макс. 1000 символов)")
        return nh3.clean(v, tags=set())


@app.get("/api/guide/{key}/comments")
async def comments_list(key: str, user=Depends(require_telegram_user)):
    rows = await get_comments(key)
    return {
        "comments": [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "name": r["first_name"] or r["username"] or "Участник",
                "text": r["text"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "is_own": r["user_id"] == user.get("id"),
            }
            for r in rows
        ]
    }


@app.post("/api/guide/{key}/comments")
@limiter.limit("10/minute")
async def comment_add(
    request: Request, key: str, body: CommentIn, user=Depends(require_telegram_user)
):
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    result = await add_comment(
        guide_key=key,
        user_id=user.get("id"),
        username=user.get("username"),
        first_name=user.get("first_name"),
        text=body.text,
    )
    return {"ok": True, **result}


@app.delete("/api/guide/{key}/comments/{comment_id}")
async def comment_delete(key: str, comment_id: int, user=Depends(require_telegram_user)):
    uid = user.get("id", 0)
    is_admin = uid in ADMIN_USERS
    deleted = await delete_comment(comment_id, user_id=uid, is_admin=is_admin)
    if not deleted:
        raise HTTPException(status_code=404, detail="Комментарий не найден или нет прав")
    return {"ok": True}


# ════════════════════════════════════════════════════════════════
# SUBSCRIPTIONS
# ════════════════════════════════════════════════════════════════


@app.get("/api/subscriptions")
async def my_subscriptions(user=Depends(require_telegram_user)):
    subs = await get_user_subscriptions(user.get("id"))
    return {"subscriptions": subs}


@app.post("/api/subscriptions/{category_key}")
async def subscribe_category(category_key: str, user=Depends(require_telegram_user)):
    cat = await get_category(category_key)
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await subscribe(user.get("id"), category_key)
    return {"ok": True, "subscribed": True}


@app.delete("/api/subscriptions/{category_key}")
async def unsubscribe_category(category_key: str, user=Depends(require_telegram_user)):
    await unsubscribe(user.get("id"), category_key)
    return {"ok": True, "subscribed": False}


# ════════════════════════════════════════════════════════════════
# ADMIN: Tags management
# ════════════════════════════════════════════════════════════════


class TagsIn(BaseModel):
    tags: list[str]


@app.put("/api/admin/guide/{key}/tags")
async def admin_set_tags(key: str, body: TagsIn, user=Depends(require_admin)):
    if not await get_guide(key):
        raise HTTPException(status_code=404, detail="Гайд не найден")
    await set_guide_tags(key, body.tags)
    await _invalidate_guide_cache_key(key)
    return {"ok": True}


# ════════════════════════════════════════════════════════════════
# NOTIFICATIONS helper (called by bot after guide creation)
# ════════════════════════════════════════════════════════════════


class NotifyIn(BaseModel):
    guide_key: str
    guide_title: str
    category_key: str
    bot_token: str  # validated against BOT_TOKEN


@app.post("/api/internal/notify")
async def notify_subscribers(body: NotifyIn):
    """Internal endpoint — bot calls this after creating a guide."""
    if body.bot_token != BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    subs = await get_subscribers(body.category_key)
    return {"ok": True, "subscribers": len(subs), "user_ids": subs}
