import asyncio
from typing import Any
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from core.auth import require_admin
from core.logging import get_logger
from models.schemas import CategoryIn, GuideIn, ReorderIn, TagsIn, ImportMediaIn, LabImportIn
from services.guides.service import guide_service, category_service
from services.cache.redis_cache import cache_service
from services.storage.hf_storage import storage_service
from services.notifications.telegram_service import telegram_service
from services.translation.service import translation_service
from services.common.members import member_service
from services.common.media import media_service
from services.common.utils import normalize_icon_syntax
from services.discord_lab.lab_synthesizer import discord_lab_service

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger("blackrose.api.admin")

@router.get("/stats")
async def admin_stats(user=Depends(require_admin)):
    return await guide_service.get_stats()

@router.get("/categories")
async def admin_categories(user=Depends(require_admin)):
    return await category_service.get_all()

@router.put("/category/{key}")
async def admin_upsert_category(key: str, body: CategoryIn, user=Depends(require_admin)):
    # Ensure icon_url is a string for the service layer
    await category_service.upsert(key, body.title, body.icon_url or "", body.sort_order)
    await cache_service.invalidate_all()
    return {"ok": True}

@router.get("/guides")
async def admin_guides_list(category_key: str | None = None, user=Depends(require_admin)):
    return await guide_service.get_all(category_key)

@router.put("/guide/{key}")
async def admin_upsert_guide(key: str, body: GuideIn, user=Depends(require_admin)):
    is_new = await guide_service.upsert(
        key=key,
        data={
            "category_key": body.category_key,
            "title": body.title,
            "icon_url": body.icon_url,
            "text": normalize_icon_syntax(body.text),
            "photo": body.photo,
            "video": body.video,
            "document": body.document,
            "sort_order": body.sort_order
        },
        changed_by=user.get("id")
    )
    await cache_service.invalidate_all()
    await cache_service.invalidate_guide(key)
    
    if is_new:
        # Background task for notification
        # In a real app we'd use Celery/Inngest, here we can use background tasks or fire-and-forget
        asyncio.create_task(telegram_service.notify_new_guide(key, body.title, body.category_key, [])) # Need subscribers logic
        
    return {"ok": True, "created": is_new}

@router.post("/upload")
async def admin_upload(file: UploadFile = File(...), folder: str = "guides", user=Depends(require_admin)):
    url = await storage_service.upload(file, folder=folder)
    return {"url": url, "filename": file.filename}

@router.post("/translate")
async def admin_translate(request: Request, user=Depends(require_admin)):
    body = await request.json()
    translated = await translation_service.translate_text(body.get("text", ""))
    return {"translated": translated}

@router.post("/media/import")
async def admin_import_media(body: ImportMediaIn, user=Depends(require_admin)):
    url = await media_service.import_from_url(body.url, folder="imported")
    return {"url": url}

@router.delete("/guide/{key}")
async def admin_delete_guide(key: str, user=Depends(require_admin)):
    deleted = await guide_service.delete(key, changed_by=user.get("id"))
    if not deleted: raise HTTPException(status_code=404, detail="Guide not found")
    await cache_service.invalidate_all()
    return {"ok": True}

@router.delete("/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    deleted = await category_service.delete(key)
    if not deleted: raise HTTPException(status_code=404, detail="Category not found")
    await cache_service.invalidate_all()
    return {"ok": True}

@router.get("/members")
async def admin_members(user=Depends(require_admin)):
    return await member_service.list_members()

@router.post("/member")
async def admin_add_member(request: Request, user=Depends(require_admin)):
    body = await request.json()
    await member_service.upsert(
        user_id=body["user_id"],
        username=body.get("username", ""),
        first_name=body.get("first_name", ""),
        role=body.get("role", "member"),
        added_by=user.get("id")
    )
    return {"ok": True}

@router.delete("/member/{user_id}")
async def admin_delete_member(user_id: int, user=Depends(require_admin)):
    await member_service.delete(user_id)
    return {"ok": True}

@router.post("/cache/clear")
async def admin_clear_cache(user=Depends(require_admin)):
    await cache_service.invalidate_all()
    return {"ok": True}

@router.post("/lab/synthesize")
async def admin_lab_synthesize(body: LabImportIn, user=Depends(require_admin)):
    if body.use_ai:
        return await discord_lab_service.synthesize_ai(body.messages)
    return discord_lab_service.synthesize(body.messages)

@router.post("/lab/import")
async def admin_lab_import(body: LabImportIn, user=Depends(require_admin)):
    """
    Triggers a background import task via Inngest.
    """
    from core.inngest_client import inngest_client
    
    # We send the data to Inngest to handle it as a durable background job
    await inngest_client.send(
        "discord/guide.import",
        data={
            "messages": body.messages, # It's already a list of dicts
            "category_key": body.category_key or "imported",
            "title": body.title or "New Imported Guide",
            "guide_key": body.guide_key
        }
    )
    
    return {"ok": True, "message": "Import task queued in background"}
