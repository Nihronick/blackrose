from fastapi import APIRouter, Depends, HTTPException, Request

from core.auth import (
    require_public_user,
    require_telegram_user,
    jwt_decode,
    jwt_encode,
    jwt_refresh_encode,
    verify_telegram_login_widget,
    verify_password,
)
from core.config import settings
from core.logging import get_logger
from core.db import get_health as get_db_health
from services.guides.service import guide_service, category_service
from services.cache.redis_cache import cache_service
from services.common.members import member_service
from services.common.utils import format_guide_text
from models.db_models import LocalAdmin
from models.schemas import CommentIn
from core.db import get_sessionmaker

router = APIRouter(tags=["public"])
logger = get_logger("blackrose.api.public")

@router.get("/health")
async def health():
    from services.storage.hf_storage import storage_service
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
    is_admin = await _is_admin(user)
    return {
        "authorized": True,
        "user_id": user.get("id", 0),
        "first_name": user.get("first_name", ""),
        "is_admin": is_admin,
        "is_guest": False,
    }

@router.get("/categories")
async def categories(user=Depends(require_public_user)):
    cached = await cache_service.get_categories()
    if cached:
        return cached

    cats = await category_service.get_all()
    result = {"categories": cats}
    await cache_service.set_categories(result)
    return result

@router.get("/guide/{key}")
async def guide(key: str, user=Depends(require_public_user)):
    g = await guide_service.get_by_key(key)
    if not g:
        raise HTTPException(status_code=404, detail="Guide not found")
    return g

@router.get("/category/{key}")
async def category_guides(key: str, user=Depends(require_public_user)):
    items = await guide_service.get_by_category(key)
    return {"items": items}

@router.get("/search")
async def search(q: str = "", user=Depends(require_public_user)):
    if not q or len(q.strip()) < 2:
        return {"results": []}
    results = await guide_service.search(q.strip())
    return {"results": results}

@router.get("/top")
async def top_guides(user=Depends(require_public_user)):
    results = await guide_service.get_top_guides(limit=10)
    return {"results": results}

@router.get("/tag/{tag}")
async def guides_by_tag(tag: str, user=Depends(require_public_user)):
    return {"results": await guide_service.get_by_tag(tag)}

@router.get("/tags")
async def tags(user=Depends(require_public_user)):
    return {"tags": await guide_service.get_tags()}

@router.get("/recent/guides")
async def recent_guides(user=Depends(require_public_user)):
    results = await guide_service.get_recent_guides(limit=10)
    return {"results": results}

@router.get("/recent/comments")
async def recent_comments(user=Depends(require_public_user)):
    comments = await guide_service.get_recent_comments(limit=10)
    return {"comments": comments}

@router.post("/auth/web-login")
async def web_login(request: Request):
    body = await request.json()
    user = verify_telegram_login_widget(body)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid auth")

    access_token = jwt_encode(user, expires_in=900, token_type="access")
    refresh_token = jwt_refresh_encode({"id": user["id"]})
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
        "user_id": user["id"],
        "is_admin": user["id"] in settings.admin_user_ids,
        **user,
    }

@router.post("/auth/tma-login")
async def tma_login(request: Request):
    user = await require_telegram_user(request)
    is_admin = await _is_admin(user)
    access_token = jwt_encode(
        {"id": user.get("id", 0), "first_name": user.get("first_name", ""), "is_admin": is_admin},
        expires_in=900,
        token_type="access",
    )
    refresh_token = jwt_refresh_encode({"id": int(user.get("id", 0) or 0)})
    return {
        "token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
        "user_id": int(user.get("id", 0) or 0),
        "first_name": user.get("first_name", ""),
        "is_admin": is_admin,
    }

@router.get("/auth/web-check")
async def web_check(request: Request):
    user = await _try_get_user(request)
    if not user:
        return {"authorized": False, "is_admin": False}
    return {"authorized": True, "is_admin": await _is_admin(user)}


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

    access_payload = {"id": user_id}
    if payload.get("is_local_admin"):
        access_payload["is_local_admin"] = True
        access_payload["is_admin"] = True
    new_access = jwt_encode(access_payload, expires_in=900, token_type="access")
    return {"token": new_access, "expires_in": 900}

@router.post("/auth/admin-login")
async def admin_login(request: Request):
    body = await request.json()
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))
    if not username or not password:
        raise HTTPException(status_code=400, detail="username/password required")

    async with get_sessionmaker()() as session:
        from sqlalchemy import select

        res = await session.execute(select(LocalAdmin).where(LocalAdmin.username == username))
        row = res.scalar_one_or_none()
        if not row or not verify_password(password, row.password_hash):
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
async def add_comment(guide_key: str, body: CommentIn, user=Depends(require_public_user)):
    row = await guide_service.add_comment(guide_key, user, body.text)
    return row

@router.delete("/guide/{guide_key}/comments/{comment_id}")
async def delete_comment(guide_key: str, comment_id: int, user=Depends(require_public_user)):
    deleted = await guide_service.delete_comment(guide_key, comment_id, user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
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
    from fastapi.responses import Response
    cats = await category_service.get_all()
    guides = await guide_service.get_all()
    frontend_url = settings.FRONTEND_URL.rstrip("/")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.append(f'  <url><loc>{frontend_url}/</loc><priority>1.0</priority></url>')
    for c in cats:
        xml.append(f'  <url><loc>{frontend_url}/category/{c["key"]}</loc><priority>0.8</priority></url>')
    for g in guides:
        xml.append(f'  <url><loc>{frontend_url}/guide/{g["key"]}</loc><priority>0.6</priority></url>')
    xml.append('</urlset>')
    return Response(content="\n".join(xml), media_type="application/xml")


async def _try_get_user(request: Request) -> dict | None:
    try:
        return await require_telegram_user(request)
    except HTTPException:
        return None


async def _is_admin(user: dict) -> bool:
    if user.get("is_local_admin"):
        return True
    uid = int(user.get("id", 0) or 0)
    if uid in settings.admin_user_ids:
        return True
    if uid <= 0:
        return False
    return await member_service.is_admin(uid)
