import asyncio
import os
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from core.auth import require_public_user, jwt_encode, require_admin, verify_telegram_login_widget, verify_telegram_init_data
from core.config import settings
from core.logging import get_logger
from core.db import get_sessionmaker, is_db_ready, get_health as get_db_health
from services.guides.service import guide_service, category_service
from services.cache.redis_cache import cache_service
from models.schemas import CommentIn, PreviewIn
from services.common.utils import normalize_icon_syntax

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
        "status": overall,
        "version": settings.VERSION,
        "services": {
            "database": db_health,
            "cache": redis_health,
            "storage": storage_health,
        }
    }

@router.get("/auth")
async def auth(user=Depends(require_public_user)):
    return {
        "authorized": True,
        "user_id": user.get("id", 0),
        "first_name": user.get("first_name", ""),
        "is_admin": user.get("is_admin", False),
        "is_guest": user.get("is_guest", False),
    }

@router.get("/categories")
async def categories(user=Depends(require_public_user)):
    cached = await cache_service.get_categories()
    if cached: return cached

    cats = await category_service.get_all()
    # Placeholder for counts logic if needed
    result = {"categories": cats}
    await cache_service.set_categories(result)
    return result

@router.get("/guide/{key}")
async def guide(key: str, user=Depends(require_public_user)):
    cached = await cache_service.get_client() # Need proper guide cache implementation
    # For now, bypass cache to ensure functionality
    g = await guide_service.get_by_key(key)
    if not g: raise HTTPException(status_code=404, detail="Guide not found")
    return g

@router.get("/search")
async def search(q: str = "", user=Depends(require_public_user)):
    if not q or len(q.strip()) < 2: return {"results": []}
    results = await guide_service.search(q.strip())
    return {"results": results}

@router.get("/top")
async def top_guides(user=Depends(require_public_user)):
    # Placeholder: implementation should be in guide_service
    return {"results": []}

@router.get("/recent/guides")
async def recent_guides(user=Depends(require_public_user)):
    return {"results": []}

@router.get("/recent/comments")
async def recent_comments(user=Depends(require_public_user)):
    return {"comments": []}

@router.post("/auth/web-login")
async def web_login(request: Request):
    body = await request.json()
    user = verify_telegram_login_widget(body)
    if not user: raise HTTPException(status_code=403, detail="Invalid auth")
    
    token = jwt_encode(user)
    return {"token": token, **user}

@router.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import Response
    cats = await category_service.get_all()
    guides = await guide_service.get_all()
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.append(f'  <url><loc>{frontend_url}/</loc><priority>1.0</priority></url>')
    for c in cats: xml.append(f'  <url><loc>{frontend_url}/category/{c["key"]}</loc><priority>0.8</priority></url>')
    for g in guides: xml.append(f'  <url><loc>{frontend_url}/guide/{g["key"]}</loc><priority>0.6</priority></url>')
    xml.append('</urlset>')
    return Response(content="\n".join(xml), media_type="application/xml")
