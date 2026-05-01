import asyncio

from cache import (
    get_categories_cache,
    get_guide_cache,
    invalidate_guide_cache,
    set_categories_cache,
    set_guide_cache,
)
from database import (
    add_comment,
    delete_comment,
    get_all_tags,
    get_categories_with_counts,
    get_category,
    get_comments,
    get_global_recent_comments,
    get_guide,
    get_guide_tags,
    get_guides_by_category,
    get_guides_by_tag,
    get_recent_guides,
    get_top_guides,
    get_user_subscriptions,
    increment_views,
    search_guides,
    subscribe,
    unsubscribe,
)
from dependencies import ADMIN_USERS, _jwt_encode, require_public_user
from fastapi import APIRouter, Depends, HTTPException, Request
from limiter import limiter
from models import CommentIn, PreviewIn
from pydantic import BaseModel
from utils import format_guide_text, resolve_guide_links_bulk

router = APIRouter()
_cache_lock = asyncio.Lock()


async def _invalidate_guide_cache_key(key: str):
    await invalidate_guide_cache(key)


@router.get("/health")
async def health():
    from database import is_db_ready
    from cache import get_redis
    
    db_ok = is_db_ready()
    
    redis_ok = False
    try:
        redis = get_redis()
        if redis:
            await redis.ping()
            redis_ok = True
    except Exception:
        pass
        
    status = "ok" if db_ok and redis_ok else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
        "cache": "connected" if redis_ok else "disconnected",
        "version": "3.3.0"
    }


@router.get("/auth")
async def auth(user=Depends(require_public_user)):
    uid = user.get("id", 0)
    return {
        "authorized": True,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": uid in ADMIN_USERS,
        "is_guest": user.get("is_guest", False),
    }


@router.get("/categories")
async def categories(user=Depends(require_public_user)):
    cached = await get_categories_cache()
    if cached:
        return cached

    async with _cache_lock:
        cached = await get_categories_cache()
        if cached:
            return cached

        cats = await get_categories_with_counts()
        result = {
            "categories": [
                {
                    "key": c["key"],
                    "title": c["title"],
                    "icon": c["icon"],
                    "count": c["count"],
                }
                for c in cats
            ]
        }
        await set_categories_cache(result)
        return result


@router.get("/category/{key}")
async def category(key: str, user=Depends(require_public_user)):
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


@router.get("/guide/{key}")
@router.get("/guides/{key}")  # Fallback for old plural requests
async def guide(key: str, user=Depends(require_public_user)):
    from icons import ALL_ICONS

    cached = await get_guide_cache(key)
    if cached:
        # ALL_ICONS is NOT stored in cache (saves ~34KB per guide in Redis).
        # Always inject from in-memory constant.
        return {**cached, "icons": ALL_ICONS}

    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")

    raw_text = g["text"] or ""
    import re

    link_keys = list(
        set(k.strip() for k in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?]]", raw_text))
    )
    guide_links = await resolve_guide_links_bulk(link_keys)

    # Build cacheable result WITHOUT icons (they are added from memory on read)
    result = {
        **g,
        "text": raw_text,
        "guide_links": guide_links,
        "photo": g["photo"] or [],
        "video": g["video"] or [],
        "document": g["document"] or [],
    }
    # Standardize icon field name
    if "icon_url" in result and "icon" not in result:
        result["icon"] = result.pop("icon_url")
    await set_guide_cache(key, result)
    # Inject icons into response (but NOT into cache)
    return {**result, "icons": ALL_ICONS}


@router.get("/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str = "", user=Depends(require_public_user)):
    if not q or len(q.strip()) < 2:
        return {"results": []}
    guides = await search_guides(q.strip())
    return {
        "results": [
            {
                "key": g["key"],
                "title": g["title"],
                "icon": g["icon_url"],
                "category_key": g["category_key"],
            }
            for g in guides
        ],
    }


@router.post("/guide/__preview__")
async def preview_guide(body: PreviewIn, user=Depends(require_public_user)):
    import asyncio

    html = await asyncio.to_thread(format_guide_text, body.text, guide_links={})
    return {"html": html}


@router.get("/icons")
async def public_icons():
    """Публичный эндпоинт иконок — отдаётся с долгим кешем на стороне клиента."""
    from fastapi.responses import JSONResponse
    from icons import ALL_ICONS

    return JSONResponse(
        content={"icons": ALL_ICONS},
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/tags")
async def tags_list(user=Depends(require_public_user)):
    return {"tags": await get_all_tags()}


@router.get("/tag/{tag}")
async def guides_by_tag(tag: str, user=Depends(require_public_user)):
    return {"tag": tag, "results": await get_guides_by_tag(tag.lower())}


@router.post("/guide/{key}/view")
@router.post("/guides/{key}/view")
@limiter.limit("60/minute")
async def record_view(request: Request, key: str, user=Depends(require_public_user)):
    views = await increment_views(key)
    await _invalidate_guide_cache_key(key)
    return {"views": views}


@router.get("/top")
async def top_guides(user=Depends(require_public_user)):
    return {"results": await get_top_guides(limit=10)}


@router.get("/recent/guides")
async def recent_guides(user=Depends(require_public_user)):
    return {"results": await get_recent_guides(limit=10)}


@router.get("/recent/comments")
async def recent_comments(user=Depends(require_public_user)):
    return {"comments": await get_global_recent_comments(limit=5)}


@router.get("/guide/{key}/comments")
async def comments_list(key: str, user=Depends(require_public_user)):
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


@router.post("/guide/{key}/comments")
@limiter.limit("10/minute")
async def comment_add(
    request: Request, key: str, body: CommentIn, user=Depends(require_public_user)
):
    uid = user.get("id", 0)
    if uid == 0:
        # Гость — разрешаем комментировать с именем "Гость"
        pass
    g = await get_guide(key)
    if not g:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    result = await add_comment(
        guide_key=key,
        user_id=uid,
        username=user.get("username", ""),
        first_name=user.get("first_name", "Гость"),
        text=body.text,
    )
    return {"ok": True, **result}


@router.delete("/guide/{key}/comments/{comment_id}")
async def comment_delete(key: str, comment_id: int, user=Depends(require_public_user)):
    uid = user.get("id", 0)
    is_admin = uid in ADMIN_USERS
    deleted = await delete_comment(comment_id, user_id=uid, is_admin=is_admin)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Комментарий не найден или нет прав"
        )
    return {"ok": True}


@router.get("/subscriptions")
async def my_subscriptions(user=Depends(require_public_user)):
    uid = user.get("id", 0)
    if uid == 0:
        return {"subscriptions": []}
    subs = await get_user_subscriptions(uid)
    return {"subscriptions": subs}


@router.post("/subscriptions/{category_key}")
async def subscribe_category(category_key: str, user=Depends(require_public_user)):
    uid = user.get("id", 0)
    if uid == 0:
        raise HTTPException(
            status_code=403, detail="Войдите через Telegram для подписки"
        )
    cat = await get_category(category_key)
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await subscribe(uid, category_key)
    return {"ok": True, "subscribed": True}


@router.delete("/subscriptions/{category_key}")
async def unsubscribe_category(category_key: str, user=Depends(require_public_user)):
    uid = user.get("id", 0)
    if uid == 0:
        raise HTTPException(
            status_code=403, detail="Войдите через Telegram для отписки"
        )
    await unsubscribe(uid, category_key)
    return {"ok": True, "subscribed": False}


# ── Веб-авторизация (Telegram Login Widget) ──────────────────


@router.post("/auth/web-login")
@limiter.limit("5/minute")
async def web_login(request: Request):
    """
    Принимает данные от Telegram Login Widget, верифицирует,
    возвращает JWT для последующих запросов с веб-сайта/PWA.
    Авторизация нужна только для администрирования и действий с user_id.
    """
    from dependencies import (
        get_admin_users,
        verify_telegram_login_widget,
    )

    body = await request.json()
    user = verify_telegram_login_widget(body)
    if not user:
        raise HTTPException(
            status_code=403, detail="Неверные данные авторизации Telegram"
        )
    uid = user["id"]
    # Проверяем и env ADMIN_USERS, и БД members с ролью admin
    admins = await get_admin_users()
    is_admin = uid in admins
    import time

    payload = {
        **user,
        "is_admin": is_admin,
        "source": "web",
        "exp": int(time.time()) + 86400 * 30,  # 30 дней
    }
    token = _jwt_encode(payload)
    return {
        "token": token,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": is_admin,
    }


@router.post("/auth/tma-login")
@limiter.limit("10/minute")
async def tma_login(request: Request):
    """
    Обменивает Telegram initData на JWT.
    Позволяет TMA пользователям получить полноценную сессию.
    """
    from dependencies import (
        get_admin_users,
        verify_telegram_init_data,
    )

    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        raise HTTPException(status_code=400, detail="Отсутствуют данные Telegram")

    user = verify_telegram_init_data(init_data)
    if not user:
        raise HTTPException(status_code=403, detail="Неверные данные Telegram")

    uid = user["id"]
    admins = await get_admin_users()
    is_admin = uid in admins
    import time

    payload = {
        **user,
        "is_admin": is_admin,
        "source": "tma",
        "exp": int(time.time()) + 86400 * 30,
    }
    token = _jwt_encode(payload)
    return {
        "token": token,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": is_admin,
    }


@router.get("/auth/web-check")
async def web_check(user=Depends(require_public_user)):
    """Проверка валидности JWT / initData. Всегда возвращает 200."""
    from dependencies import get_admin_users

    uid = user.get("id", 0) if user else 0
    admins = await get_admin_users()
    return {
        "authorized": True,
        "user_id": uid,
        "first_name": user.get("first_name", "") if user else "",
        "is_admin": uid in admins or user.get("is_local_admin", False),
        "is_guest": user.get("is_guest", False) if user else True,
        "source": user.get("source", "web") if user else "web",
    }


@router.post("/auth/refresh")
async def refresh_token(user=Depends(require_public_user)):
    """
    Обновляет JWT сессию. Доступно только для авторизованных пользователей.
    """
    if user.get("is_guest"):
        raise HTTPException(status_code=401, detail="Невозможно обновить гостевую сессию")

    uid = user["id"]
    from dependencies import get_admin_users

    admins = await get_admin_users()
    is_admin = uid in admins
    import time

    payload = {
        **user,
        "is_admin": is_admin,
        "exp": int(time.time()) + 86400 * 30,  # Продлеваем еще на 30 дней
    }
    token = _jwt_encode(payload)
    return {
        "token": token,
        "user_id": uid,
        "first_name": user.get("first_name", ""),
        "is_admin": is_admin,
    }


class AdminLoginIn(BaseModel):
    username: str
    password: str


@router.post("/auth/admin-login")
@limiter.limit("5/minute")
async def admin_local_login(request: Request, data: AdminLoginIn):
    """Авторизация админа по логину и паролю (без Telegram)."""
    from database import get_local_admin
    from dependencies import verify_password

    admin_data = await get_local_admin(data.username)
    if not admin_data or not verify_password(
        data.password, admin_data["password_hash"]
    ):
        raise HTTPException(status_code=403, detail="Неверный логин или пароль")

    import time

    payload = {
        "id": -1,
        "username": admin_data["username"],
        "first_name": "Локальный Администратор",
        "is_admin": True,
        "is_local_admin": True,
        "exp": int(time.time()) + 86400 * 30,
    }
    token = _jwt_encode(payload)
    return {
        "token": token,
        "user_id": -1,
        "first_name": payload["first_name"],
        "is_admin": True,
    }
