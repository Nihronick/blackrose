import hmac
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select

from core.auth import (
    require_public_user,
    require_user,
    jwt_decode,
    jwt_encode,
    jwt_refresh_encode,
    verify_password,
    hash_password,
    verify_telegram_login_widget,
)
from core.config import settings
from core.logging import get_logger
from core.rate_limit import limiter
from core.db import get_health as get_db_health, get_sessionmaker
from services.guides.service import guide_service, category_service
from services.cache.redis_cache import cache_service
from services.common.members import member_service
from services.common.utils import format_guide_text
from services.storage.hf_storage import storage_service
from models.db_models import LocalAdmin
from models.schemas import CommentIn, ReactionIn
from core.cache import cached

router = APIRouter(tags=["public"])
logger = get_logger("blackrose.api.public")

@router.get("/health")
async def health():
    db_health = await get_db_health()
    redis_health = await cache_service.ping()
    storage_health = await storage_service.ping()

    overall = "healthy"
    if db_health["status"] != "healthy" or storage_health["status"] == "unhealthy":
        overall = "degraded"

    return {
        "status": "ok" if overall == "healthy" else overall,
        "version": settings.VERSION,
        "services": {
            "database": db_health,
            "cache": redis_health,
            "storage": storage_health,
        }
    }

@router.get("/auth")
@router.get("/auth/web-check")
async def auth(request: Request):
    user = await _try_get_user(request)
    if not user:
        return {
            "authorized": False,
            "user_id": 0,
            "first_name": "",
            "is_admin": False,
            "is_guest": True,
        }
    uid = int(user.get("id", 0) or 0)
    username = str(user.get("username", "")).strip()
    first_name = str(user.get("first_name", "")).strip()
    if uid > 0:
        try:
            await member_service.ensure_member(uid, username, first_name)
        except Exception:
            pass

    is_admin = await _is_admin(user)
    token = jwt_encode({"id": uid, "username": username, "first_name": first_name, "is_admin": is_admin}, expires_in=86400 * 30)
    return {
        "authorized": True,
        "user_id": uid,
        "first_name": first_name,
        "username": username,
        "is_admin": is_admin,
        "is_guest": False,
        "token": token,
    }

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received Telegram webhook update: {data}")
        
        # 1. Handle Inline Queries (@BlackRoseBot <search>)
        inline_query = data.get("inline_query")
        if inline_query:
            iq_id = inline_query.get("id")
            query = inline_query.get("query", "").strip()
            if query:
                guides_found = await guide_service.search(query)
            else:
                guides_found = await guide_service.get_top_guides(limit=10)

            results = []
            base_url = (settings.FRONTEND_URL or "https://blackrosesl.me/").rstrip("/")
            for g in (guides_found or [])[:10]:
                g_key = g.get("key") or g.get("id")
                g_title = g.get("title", "Гайд Slayer Legend")
                g_text = (g.get("text") or "")[:200]
                guide_url = f"{base_url}/guide/{g_key}"

                results.append({
                    "type": "article",
                    "id": str(g_key),
                    "title": g_title,
                    "description": g_text[:100],
                    "input_message_content": {
                        "message_text": f"🌹 *{g_title}*\n\n{g_text}...\n\n🔗 Читать полностью: {guide_url}",
                        "parse_mode": "Markdown",
                    },
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "📖 Открыть гайд в App",
                                    "web_app": {"url": guide_url}
                                }
                            ]
                        ]
                    }
                })

            return {
                "method": "answerInlineQuery",
                "inline_query_id": iq_id,
                "results": results,
                "cache_time": 60,
            }

        # 2. Handle Chat Messages
        msg = data.get("message") or data.get("edited_message") or {}
        chat_id = msg.get("chat", {}).get("id")
        if chat_id:
            first_name = msg.get("from", {}).get("first_name", "Слеер")
            reply_text = (
                f"🌹 *Приветствуем, {first_name}!*\n\n"
                f"Добро пожаловать в *BlackRose* — главное сообщество и базу знаний по *Slayer Legend*!\n\n"
                f"Нажмите на **Inline-кнопку** ниже, чтобы открыть веб-приложение:"
            )
            app_url = (settings.FRONTEND_URL or "https://blackrosesl.me/").rstrip("/") + "/"
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "🚀 Открыть BlackRose App",
                            "web_app": {"url": app_url}
                        }
                    ]
                ]
            }
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": reply_text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            }
    except Exception as e:
        logger.warning(f"Telegram webhook handler notice: {e}")
    return {"ok": True}


@router.post("/auth/web-login")
@router.post("/auth/telegram-inline-login")
async def telegram_web_login(request: Request):
    """
    Authenticates a user via Telegram Login Widget or Telegram Inline Login URL parameters.
    Verifies HMAC-SHA256 signature using bot_token.
    """
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")

    verified_user = verify_telegram_login_widget(body)
    if not verified_user:
        raise HTTPException(status_code=403, detail="Недействительная подпись Telegram")

    uid = int(verified_user.get("id", 0) or 0)
    if uid <= 0:
        raise HTTPException(status_code=403, detail="Неверный идентификатор пользователя")

    username = str(verified_user.get("username", "")).strip()
    first_name = str(verified_user.get("first_name", "")).strip()
    photo_url = str(verified_user.get("photo_url", "")).strip()

    try:
        await member_service.ensure_member(uid, username, first_name)
    except Exception as e:
        logger.debug(f"ensure_member notice in web_login: {e}")

    is_admin = await _is_admin(verified_user)
    token_payload = {
        "id": uid,
        "username": username,
        "first_name": first_name,
        "photo_url": photo_url,
        "is_admin": is_admin,
    }

    access_token = jwt_encode(token_payload, expires_in=86400 * 30, token_type="access")
    refresh_token = jwt_refresh_encode({"id": uid, "username": username, "is_admin": is_admin})

    return {
        "ok": True,
        "token": access_token,
        "refresh_token": refresh_token,
        "user_id": uid,
        "first_name": first_name,
        "username": username,
        "photo_url": photo_url,
        "is_admin": is_admin,
    }

@router.post("/auth/emergency-login")
async def emergency_login(request: Request):
    if not settings.ADMIN_EMERGENCY_KEY:
        raise HTTPException(status_code=403, detail="Emergency login disabled")
    
    body = await request.json()
    key = str(body.get("emergency_key", "")).strip()
    target_key = settings.ADMIN_EMERGENCY_KEY
    if not hmac.compare_digest(key, target_key):
        raise HTTPException(status_code=403, detail="Неверный аварийный ключ доступа")

    payload = {
        "id": 7215567457,
        "first_name": "Project Lead (Emergency)",
        "role": "project_admin",
        "is_admin": True
    }
    token = jwt_encode(payload, expires_in=86400)
    return {"token": token, "ok": True, "user": payload}

@router.get("/categories")
@cached(expire=3600)
async def categories(request: Request, user=Depends(require_public_user)):
    cats = await category_service.get_all()
    return {"categories": cats}

@router.get("/guide/{key}")
@cached(expire=300)
async def guide(key: str, request: Request, user=Depends(require_public_user)):
    g = await guide_service.get_by_key(key)
    if not g:
        raise HTTPException(status_code=404, detail="Guide not found")
    return g

@router.get("/category/{key}")
@cached(expire=600)
async def category_guides(key: str, request: Request, user=Depends(require_public_user)):
    items = await guide_service.get_by_category(key)
    return {"items": items}

@router.get("/search")
async def search(q: str = "", user=Depends(require_public_user)):
    if not q or len(q.strip()) < 2:
        return {"results": []}
    results = await guide_service.search(q.strip())
    return {"results": results}

@router.get("/top")
@cached(expire=120)
async def top_guides(request: Request, user=Depends(require_public_user)):
    results = await guide_service.get_top_guides(limit=10)
    return {"results": results}

@router.get("/tag/{tag}")
@cached(expire=300)
async def guides_by_tag(tag: str, request: Request, user=Depends(require_public_user)):
    return {"results": await guide_service.get_by_tag(tag)}

@router.get("/tags")
@cached(expire=300)
async def tags(request: Request, user=Depends(require_public_user)):
    return {"tags": await guide_service.get_tags()}

@router.get("/recent/guides")
@cached(expire=120)
async def recent_guides(request: Request, user=Depends(require_public_user)):
    results = await guide_service.get_recent_guides(limit=10)
    return {"results": results}

@router.get("/recent/comments")
@cached(expire=60)
async def recent_comments(request: Request, user=Depends(require_public_user)):
    comments = await guide_service.get_recent_comments(limit=10)
    return {"comments": comments}

@router.get("/guide/{key}/reactions")
async def get_guide_reactions(key: str, request: Request, user=Depends(require_public_user)):
    user_id = str(user.get("id")) if user else request.client.host
    return await guide_service.get_reactions(key, user_id)

@router.post("/guide/{key}/react")
@limiter.limit("30/minute")
async def post_guide_reaction(request: Request, key: str, body: ReactionIn, user=Depends(require_public_user)):
    user_id = str(user.get("id")) if user and user.get("id") else request.client.host
    if body.reaction not in ("fire", "like", "idea", "dragon"):
        raise HTTPException(status_code=400, detail="Неверный тип реакции")
    return await guide_service.toggle_reaction(key, body.reaction, user_id)

@router.get("/user/favorites")
async def get_my_favorites(user=Depends(require_user)):
    favs = await guide_service.get_user_favorites(user["id"])
    return {"favorites": favs}

@router.post("/user/favorites/{key}")
async def add_my_favorite(key: str, user=Depends(require_user)):
    ok = await guide_service.add_user_favorite(user["id"], key)
    return {"ok": ok}

@router.delete("/user/favorites/{key}")
async def remove_my_favorite(key: str, user=Depends(require_user)):
    ok = await guide_service.remove_user_favorite(user["id"], key)
    return {"ok": ok}







@router.post("/auth/refresh")
async def refresh_token(request: Request):
    body = await request.json()
    token = body.get("refresh_token", "")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    payload = jwt_decode(token)
    if not payload or payload.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload.get("id", 0) or 0)
    if user_id <= 0:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # JWT Rotation: Check if this refresh token is blacklisted
    
    token_jti = payload.get("iat", "")  # Use issued-at as unique token ID
    blacklist_key = f"jwt:blacklist:{user_id}:{token_jti}"
    is_blacklisted = await cache_service.get(blacklist_key)
    if is_blacklisted:
        # Token reuse detected — potential theft. Revoke entire family.
        logger.warning(f"Refresh token reuse detected for user {user_id}. Revoking all tokens.")
        await cache_service.set(f"jwt:revoke_all:{user_id}", True, expire=604800)
        raise HTTPException(status_code=401, detail="Token reuse detected. All sessions revoked.")

    # Check if all tokens for this user have been revoked
    all_revoked = await cache_service.get(f"jwt:revoke_all:{user_id}")
    if all_revoked:
        raise HTTPException(status_code=401, detail="All sessions have been revoked. Please re-authenticate.")

    # Blacklist the used refresh token (TTL = remaining lifetime)
    exp = payload.get("exp", 0)
    remaining_ttl = max(int(exp - time.time()), 60)
    await cache_service.set(blacklist_key, True, expire=remaining_ttl)

    # Issue new access token
    access_payload = {"id": user_id}
    if payload.get("is_local_admin"):
        access_payload["is_local_admin"] = True
        access_payload["is_admin"] = True
    new_access = jwt_encode(access_payload, expires_in=900, token_type="access")

    # Issue NEW refresh token (rotation)
    refresh_payload = {"id": user_id}
    if payload.get("is_local_admin"):
        refresh_payload["is_local_admin"] = True
        refresh_payload["is_admin"] = True
    new_refresh = jwt_refresh_encode(refresh_payload, expires_in=60 * 60 * 24 * 7)

    return {
        "token": new_access,
        "refresh_token": new_refresh,
        "expires_in": 900,
    }

@router.post("/auth/admin-login")
async def admin_login(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    if not username or not password:
        raise HTTPException(status_code=400, detail="username/password required")

    async with get_sessionmaker()() as session:
        

        res = await session.execute(select(LocalAdmin).where(LocalAdmin.username == username))
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        elif not verify_password(password, row.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt_encode(
        {"id": row.id, "first_name": username, "is_admin": True, "is_local_admin": True},
        expires_in=900,
        token_type="access",
    )
    refresh_token = jwt_refresh_encode({"id": row.id, "is_local_admin": True, "is_admin": True})
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
        "user_id": row.id,
        "first_name": username,
        "is_admin": True,
    }

@router.get("/subscriptions")
async def subscriptions(user=Depends(require_public_user)):
    uid = int(user.get("id", 0) or 0)
    if uid <= 0:
        return {"subscriptions": []}
    return {"subscriptions": await category_service.get_subscriptions(uid)}

@router.post("/subscriptions/{category_key}")
async def subscribe(category_key: str, user=Depends(require_public_user)):
    uid = int(user.get("id", 0) or 0)
    if uid <= 0:
        raise HTTPException(status_code=403, detail="Unauthorized")
    await category_service.subscribe(uid, category_key)
    return {"ok": True}

@router.delete("/subscriptions/{category_key}")
async def unsubscribe(category_key: str, user=Depends(require_public_user)):
    uid = int(user.get("id", 0) or 0)
    if uid <= 0:
        raise HTTPException(status_code=403, detail="Unauthorized")
    await category_service.unsubscribe(uid, category_key)
    return {"ok": True}


@router.get("/guide/{guide_key}/comments")
async def comments(guide_key: str, user=Depends(require_public_user)):
    return {"comments": await guide_service.get_comments(guide_key)}

@router.post("/guide/{guide_key}/comments")
@limiter.limit("10/minute")
async def add_comment(request: Request, guide_key: str, body: CommentIn, user=Depends(require_public_user)):
    row = await guide_service.add_comment(guide_key, user, body.text)
    return row

@router.delete("/guide/{guide_key}/comments/{comment_id}")
async def delete_comment(guide_key: str, comment_id: int, user=Depends(require_user)):
    deleted = await guide_service.delete_comment(guide_key, comment_id, user)
    if not deleted:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления комментария")
    return {"ok": True}

@router.post("/guide/{guide_key}/view")
async def record_view(guide_key: str, user=Depends(require_public_user)):
    await guide_service.record_view(guide_key)
    return {"ok": True}

@router.post("/guide/__preview__")
async def preview_guide(request: Request, user=Depends(require_public_user)):
    body = await request.json()
    text = str(body.get("text", ""))
    guides = await guide_service.get_all()
    guide_links = {
        g["key"]: {"title": g.get("title", g["key"]), "icon": g.get("icon_url", "")}
        for g in guides
    }
    return {"html": format_guide_text(text, guide_links)}

@router.get("/sitemap.xml")
async def sitemap():
    
    cats = await category_service.get_all()
    primary_url = "https://blackrosesl.me"
    if settings.FRONTEND_URL:
        for entry in settings.FRONTEND_URL.split(","):
            clean = entry.strip().rstrip("/")
            if "blackrosesl.me" in clean or "nihronick.github.io" in clean:
                primary_url = clean
                break
            if clean.startswith("http"):
                primary_url = clean

    frontend_url = primary_url

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.append(f'  <url><loc>{frontend_url}/</loc><priority>1.0</priority></url>')
    for c in cats:
        xml.append(f'  <url><loc>{frontend_url}/category/{c["key"]}</loc><priority>0.8</priority></url>')
    guides = await guide_service.get_all()
    for g in guides:
        xml.append(f'  <url><loc>{frontend_url}/guide/{g["key"]}</loc><priority>0.6</priority></url>')
    xml.append('</urlset>')
    return Response(content="\n".join(xml), media_type="application/xml")


@router.get("/og/guide/{guide_key}")
async def og_guide_preview(guide_key: str):
    """Dynamic OpenGraph and Twitter Card metadata for social bots."""
    
    guide = await guide_service.get_by_key(guide_key)
    if not guide:
        raise HTTPException(status_code=404, detail="Гайд не найден")

    title = guide.get("title", "Гайд Slayer Legend")
    raw_text = guide.get("text") or guide.get("content") or ""
    clean_desc = (raw_text[:200] if len(raw_text) > 200 else raw_text).replace('"', '&quot;').replace('\n', ' ')
    icon_url = guide.get("icon_url") or "https://blackrosesl.me/app-icon.png"
    canonical_url = f"https://blackrosesl.me/guide/{guide_key}"

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>{title} | BlackRose Slayer Legend</title>
  <meta name="description" content="{clean_desc}">
  <meta property="og:site_name" content="BlackRose Slayer Legend Wiki">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{clean_desc}">
  <meta property="og:image" content="{icon_url}">
  <meta property="og:url" content="{canonical_url}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{clean_desc}">
  <meta name="twitter:image" content="{icon_url}">
  <meta http-equiv="refresh" content="0; url={canonical_url}">
</head>
<body>
  <p>Перенаправление на <a href="{canonical_url}">{title}</a>...</p>
</body>
</html>"""
    return HTMLResponse(content=html, media_type="text/html")


async def _try_get_user(request: Request) -> dict | None:
    try:
        return await require_user(request)
    except HTTPException:
        return None


async def _is_admin(user: dict) -> bool:
    if user.get("is_local_admin") or user.get("is_admin"):
        return True
    if user.get("role") in ("project_admin", "admin"):
        return True

    uid = int(user.get("id", 0) or 0)
    if uid > 0:
        if uid in settings.admin_user_ids:
            return True
        return await member_service.is_admin(uid)

    return False
