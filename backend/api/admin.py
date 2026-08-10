from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
import inngest

from core.auth import require_admin
from core.logging import get_logger
from models.schemas import CategoryIn, GuideIn, ImportMediaIn, LabImportIn, ReorderIn, TagsIn
from services.guides.service import guide_service, category_service
from services.cache.redis_cache import cache_service
from services.storage.hf_storage import storage_service
from services.translation.service import translation_service
from services.common.members import member_service
from services.common.media import media_service
from services.common.utils import normalize_icon_syntax
from services.common.icons import icon_catalog, icon_url
from services.discord_lab.lab_synthesizer import discord_lab_service
from core.inngest_client import inngest_client

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

@router.get("/guide/{key}")
async def admin_guide_get(key: str, user=Depends(require_admin)):
    g = await guide_service.get_by_key(key)
    if not g:
        raise HTTPException(status_code=404, detail="Guide not found")
    return g

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
    if not deleted:
        raise HTTPException(status_code=404, detail="Guide not found")
    await cache_service.invalidate_all()
    return {"ok": True}

@router.get("/guide/{key}/history")
async def admin_guide_history(key: str, user=Depends(require_admin)):
    return {"history": await guide_service.get_history(key)}

@router.delete("/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    deleted = await category_service.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
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

@router.post("/reorder/guides")
async def admin_reorder_guides(body: ReorderIn, user=Depends(require_admin)):
    await guide_service.reorder([i.model_dump() for i in body.order])
    await cache_service.invalidate_all()
    return {"ok": True}

@router.post("/reorder/categories")
async def admin_reorder_categories(body: ReorderIn, user=Depends(require_admin)):
    await category_service.reorder([i.model_dump() for i in body.order])
    await cache_service.invalidate_all()
    return {"ok": True}

@router.put("/guide/{key}/tags")
async def admin_set_guide_tags(key: str, body: TagsIn, user=Depends(require_admin)):
    ok = await guide_service.set_tags(key, body.tags)
    if not ok:
        raise HTTPException(status_code=404, detail="Guide not found")
    await cache_service.invalidate_guide(key)
    return {"ok": True}

@router.get("/analytics")
async def admin_analytics(days: int = 30, user=Depends(require_admin)):
    return {"chart": await guide_service.get_analytics(days)}

@router.get("/icons")
async def admin_icons(user=Depends(require_admin)):
    grouped = await admin_icons_grouped(user)
    flat = []
    for g in grouped:
        flat.extend(g.get("icons", []))
    return flat

@router.get("/icons/grouped")
async def admin_icons_grouped(user=Depends(require_admin)):
    keys = icon_catalog()
    return [
        {
            "id": "default",
            "label": "Default",
            "icons": [{"key": k, "url": icon_url(k)} for k in keys],
        }
    ]

@router.get("/media/list")
async def admin_media_list(user=Depends(require_admin)):
    if not storage_service.repo_id:
        return {"total": 0, "groups": []}
    groups_map: dict[str, list[dict]] = {}
    try:
        tree = storage_service.api.list_repo_tree(
            repo_id=storage_service.repo_id,
            repo_type="dataset",
            path_in_repo=storage_service.path_prefix,
            recursive=True,
        )
        for entry in tree:
            if getattr(entry, "type", "") != "file":
                continue
            path = entry.path
            folder = path.split("/")[1] if "/" in path else "root"
            name = path.rsplit("/", 1)[-1]
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            media_type = "video" if ext in {"mp4", "mov", "webm", "m4v"} else "image"
            groups_map.setdefault(folder, []).append(
                {"name": name, "url": storage_service._get_public_url(path), "type": media_type}
            )
    except Exception as e:
        logger.error(f"media list failed: {e}")
        return {"total": 0, "groups": []}
    groups = [
        {"id": k, "label": k, "items": sorted(v, key=lambda x: x["name"])}
        for k, v in sorted(groups_map.items())
    ]
    return {"total": sum(len(g["items"]) for g in groups), "groups": groups}

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File

@router.delete("/media")
async def admin_media_delete(url: str, user=Depends(require_admin)):
    ok = await storage_service.delete(url)
    if not ok:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"ok": True}

@router.post("/media/upload")
async def admin_media_upload(file: UploadFile = File(...), user=Depends(require_admin)):
    try:
        contents = await file.read()
        saved_path = await storage_service.save_file(
            file.filename or "upload.jpg", contents, folder="uploads"
        )
        return {"ok": True, "url": saved_path, "filename": file.filename}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка загрузки файла: {e}")

@router.get("/export")
async def admin_export(user=Depends(require_admin)):
    return {
        "categories": await category_service.get_all(),
        "guides": await guide_service.get_all(),
    }

@router.post("/import")
async def admin_import(request: Request, user=Depends(require_admin)):
    body = await request.json()
    categories = body.get("categories", []) or []
    guides = body.get("guides", []) or []
    imported_categories = 0
    imported_guides = 0
    for c in categories:
        await category_service.upsert(
            key=c.get("key", ""),
            title=c.get("title", ""),
            icon_url=c.get("icon_url", ""),
            sort_order=int(c.get("sort_order", 0) or 0),
        )
        imported_categories += 1
    for g in guides:
        key = g.get("key", "")
        if not key:
            continue
        await guide_service.upsert(
            key=key,
            data={
                "category_key": g.get("category_key", ""),
                "title": g.get("title", ""),
                "icon_url": g.get("icon_url"),
                "text": normalize_icon_syntax(g.get("text", "")),
                "photo": g.get("photo", []) or [],
                "video": g.get("video", []) or [],
                "document": g.get("document", []) or [],
                "sort_order": int(g.get("sort_order", 0) or 0),
            },
            changed_by=user.get("id"),
        )
        imported_guides += 1
    await cache_service.invalidate_all()
    return {"categories": imported_categories, "guides": imported_guides}

@router.post("/lab/synthesize")
async def admin_lab_synthesize(body: LabImportIn, user=Depends(require_admin)):
    if body.use_ai:
        return await discord_lab_service.synthesize_ai(body.messages)
    return discord_lab_service.synthesize(body.messages)

@router.post("/lab/import")
async def admin_lab_import(body: LabImportIn, user=Depends(require_admin)):
    """
    Triggers a background import task via Inngest.
    Falls back to inline execution if Inngest is not configured.
    """
    import os
    has_inngest = bool(os.getenv("INNGEST_SIGNING_KEY"))

    category_key = body.category_key or "imported"
    title = body.title or "New Imported Guide"
    guide_key = body.guide_key

    if has_inngest:
        event = inngest.Event(
            name="discord/guide.import",
            data={
                "messages": body.messages,
                "category_key": category_key,
                "title": title,
                "guide_key": guide_key,
            },
        )
        await inngest_client.send(event)
        return {"ok": True, "message": "Import task queued in background"}

    # Fallback: inline execution when Inngest is unavailable
    try:
        if body.use_ai:
            synthesis = await discord_lab_service.synthesize_ai(body.messages)
        else:
            synthesis = discord_lab_service.synthesize(body.messages)

        content = synthesis["content"]
        
        # Resolve inline Discord URLs in markdown
        content = await media_service.resolve_inline_media(content, folder="imported")
        
        raw_media = synthesis.get("media", [])

        processed_media = []
        for m in raw_media[:10]:
            try:
                url = m if isinstance(m, str) else m.get("url", "")
                new_url = await media_service.import_from_url(url, folder="imported")
                processed_media.append(new_url)
            except Exception as e:
                logger.error(f"Media import failed: {e}")

        if not guide_key:
            import uuid
            guide_key = f"imported-{str(uuid.uuid4())[:8]}"

        await guide_service.upsert(
            key=guide_key,
            data={
                "category_key": category_key,
                "title": title,
                "text": normalize_icon_syntax(content),
                "photo": [u for u in processed_media if u.endswith(('.webp', '.png', '.jpg'))],
                "video": [u for u in processed_media if u.endswith(('.mp4', '.mov'))],
                "sort_order": 0,
            },
        )
        await cache_service.invalidate_all()
        return {"ok": True, "message": "Import completed inline (Inngest unavailable)", "guide_key": guide_key}
    except Exception as e:
        logger.error(f"Inline import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/backup/export")
async def admin_export_backup(user=Depends(require_admin)):
    from core.db import get_sessionmaker
    from sqlalchemy import select
    from models.db_models import Category, Guide, DiscordSyncChannel, Guild

    async with get_sessionmaker()() as session:
        cats_res = await session.execute(select(Category))
        categories = [c.__dict__ for c in cats_res.scalars().all()]
        for c in categories:
            c.pop("_sa_instance_state", None)

        guides_res = await session.execute(select(Guide))
        guides = [g.__dict__ for g in guides_res.scalars().all()]
        for g in guides:
            g.pop("_sa_instance_state", None)

        channels_res = await session.execute(select(DiscordSyncChannel))
        channels = [ch.__dict__ for ch in channels_res.scalars().all()]
        for ch in channels:
            ch.pop("_sa_instance_state", None)

        guilds_res = await session.execute(select(Guild))
        guilds = [gl.__dict__ for gl in guilds_res.scalars().all()]
        for gl in guilds:
            gl.pop("_sa_instance_state", None)

        return {
            "version": "2.0",
            "categories": categories,
            "guides": guides,
            "discord_sync_channels": channels,
            "guilds": guilds,
        }

