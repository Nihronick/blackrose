import asyncio
import logging
import os
import tempfile
import uuid
from io import BytesIO
from typing import Any

from cache import invalidate_all, invalidate_guide_cache
from database import (
    delete_category,
    delete_guide,
    export_all,
    get_all_guides,
    get_categories,
    get_category,
    get_guide,
    get_guide_history,
    get_guides_by_category,
    import_guides,
    reorder_categories,
    reorder_guides,
    set_guide_tags,
    upsert_category,
    upsert_guide,
)
from dependencies import require_admin, get_db
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from models import CategoryIn, GuideIn, ImportMediaIn, ReorderIn, TagsIn
from pydantic import BaseModel
from storage import delete_file, delete_files, upload_file
from utils import _notify_new_guide, normalize_icon_syntax
import re

router = APIRouter()
logger = logging.getLogger("blackrose.admin")


async def _invalidate_cache():
    await invalidate_all()


async def _invalidate_guide_cache_key(key: str):
    await invalidate_guide_cache(key)


@router.post("/upload")
async def admin_upload(
    file: UploadFile = File(...),
    folder: str = "guides",
    user=Depends(require_admin),
):
    """Загрузка файла в облачное хранилище (R2/S3)."""
    try:
        url = await upload_file(file, folder=folder)
        return {"url": url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {e}")



@router.post("/media/import")
async def admin_import_media(body: ImportMediaIn, user=Depends(require_admin)):
    import aiohttp
    from fastapi import UploadFile
    from urllib.parse import urlparse
    
    tmp_path = None
    temp_compressed_path = None
    try:
        # Determine filename from URL
        parsed = urlparse(body.url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = f"file_{uuid.uuid4().hex[:8]}"
            
        async with aiohttp.ClientSession() as session:
            async with session.get(body.url, timeout=60) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to fetch {body.url}: {resp.status}")
                
                content_type = resp.headers.get("content-type", "application/octet-stream")
                
                # Если файл большой (видео), качаем через диск для экономии RAM при компрессии
                is_video = "video" in content_type or any(body.url.lower().endswith(ext) for ext in [".mp4", ".mov", ".webm"])
                
                if is_video:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp:
                        tmp_path = tmp.name
                        async for chunk in resp.content.iter_chunked(1024 * 1024):
                            tmp.write(chunk)
                    
                    temp_compressed_path = tmp_path + "_comp.mp4"
                    final_path = tmp_path
                    
                    if os.path.getsize(tmp_path) > 48 * 1024 * 1024:
                        logger.info(f"File {filename} is large ({os.path.getsize(tmp_path) / 1024 / 1024:.2f}MB).")
                        
                        is_render = os.environ.get('RENDER') == 'true'
                        if is_render and os.path.getsize(tmp_path) > 100 * 1024 * 1024:
                            logger.warning("File too huge for Render RAM, skipping compression.")
                        else:
                            try:
                                logger.info(f"Attempting to compress {filename}...")
                                import asyncio
                                process = await asyncio.create_subprocess_exec(
                                    'ffmpeg', '-i', tmp_path, '-vcodec', 'libx264', '-crf', '28', '-preset', 'veryfast', temp_compressed_path,
                                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                                )
                                try:
                                    await asyncio.wait_for(process.communicate(), timeout=300)
                                    if os.path.exists(temp_compressed_path) and os.path.getsize(temp_compressed_path) > 0:
                                        final_path = temp_compressed_path
                                        logger.info(f"Compression successful: {os.path.getsize(temp_compressed_path) / 1024 / 1024:.2f}MB")
                                except asyncio.TimeoutError:
                                    logger.error("FFmpeg compression timed out.")
                                    process.kill()
                            except Exception as e:
                                logger.error(f"Compression failed: {e}")

                    # Загружаем
                    with open(final_path, "rb") as f:
                        upload_file_obj = UploadFile(
                            file=f,
                            filename=filename,
                            headers={"content-type": content_type}
                        )
                        url = await upload_file(upload_file_obj, folder=body.folder)
                else:
                    # Изображения обычно небольшие, качаем в память
                    content = await resp.read()
                    upload_file_obj = UploadFile(
                        file=BytesIO(content),
                        filename=filename,
                        headers={"content-type": content_type}
                    )
                    url = await upload_file(upload_file_obj, folder=body.folder)
            
        return {"url": url, "filename": filename}
    except Exception as e:
        logger.error("Failed to import media: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка импорта медиа: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)
        if temp_compressed_path and os.path.exists(temp_compressed_path): os.remove(temp_compressed_path)


@router.get("/media/proxy")
async def admin_media_proxy(url: str, user=Depends(require_admin)):
    """
    Прокси для медиафайлов из Discord. Позволяет обходить CORS и 
    временные ограничения ссылок Discord для предпросмотра.
    Полностью асинхронная реализация с поддержкой метаданных.
    """
    import aiohttp
    from fastapi.responses import StreamingResponse
    
    if not url.startswith("https://cdn.discordapp.com") and not url.startswith("https://media.discordapp.net"):
        raise HTTPException(status_code=400, detail="Разрешены только ссылки Discord")

    headers = {
        "Cache-Control": "public, max-age=3600",
        "Access-Control-Allow-Origin": "*",
        "Accept-Ranges": "bytes"
    }
    
    # Маскируемся под обычный браузер, чтобы Discord CDN не блокировал aiohttp
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://discord.com/"
    }

    # Получаем метаданные асинхронно
    async with aiohttp.ClientSession() as session:
        try:
            async with session.head(url, headers=req_headers, timeout=5) as head_resp:
                if head_resp.status != 200:
                    logger.warning(f"Discord returned {head_resp.status} for HEAD {url}")
                    # Если ссылка протухла или заблокирована, нет смысла продолжать
                    raise HTTPException(status_code=head_resp.status, detail="Media not found or expired")
                    
                if "Content-Length" in head_resp.headers:
                    headers["Content-Length"] = head_resp.headers["Content-Length"]
                if "Content-Type" in head_resp.headers:
                    content_type = head_resp.headers["Content-Type"]
                else:
                    import mimetypes
                    clean_url = url.split("?")[0]
                    content_type, _ = mimetypes.guess_type(clean_url)
                    if not content_type:
                        content_type = "video/mp4" if ".mp4" in clean_url.lower() else "application/octet-stream"
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Async HEAD failed for {url}: {e}")
            content_type = "application/octet-stream"

    async def stream_content():
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=req_headers, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to stream {url}, status: {resp.status}")
                        return
                    async for chunk in resp.content.iter_chunked(1024 * 64):
                        yield chunk
            except Exception as e:
                logger.error(f"Async proxy streaming error for {url}: {e}")

    return StreamingResponse(
        stream_content(), 
        media_type=content_type,
        headers=headers
    )


@router.get("/categories")
async def admin_categories(user=Depends(require_admin)):
    return await get_categories()


@router.get("/stats")
async def admin_stats(
    user=Depends(require_admin),
    session=Depends(get_db)
):
    from db_models import Guide, GuideComment, Category, Member
    from sqlalchemy import func, select

    try:
        # Optimized: Single query for all stats
        stmt = select(
            select(func.count(Category.key)).scalar_subquery(),
            select(func.count(Guide.key)).scalar_subquery(),
            select(func.count(Member.user_id)).scalar_subquery(),
            select(func.sum(Guide.views)).scalar_subquery(),
            select(func.count(GuideComment.id)).scalar_subquery(),
        )
        res = await session.execute(stmt)
        row = res.fetchone()

        return {
            "categories": int(row[0] or 0),
            "guides": int(row[1] or 0),
            "members": int(row[2] or 0),
            "views": int(row[3] or 0),
            "comments": int(row[4] or 0),
        }
    except Exception as e:
        logger.error("Error in admin_stats: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in admin_stats: {e}")


@router.get("/analytics")
async def admin_analytics(days: int = 30, user=Depends(require_admin)):
    from database import get_daily_analytics
    try:
        return {"chart": await get_daily_analytics(days)}
    except Exception as e:
        logger.error("Error in admin_analytics: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in admin_analytics: {e}")


@router.put("/category/{key}")
async def admin_upsert_category(
    key: str, body: CategoryIn, user=Depends(require_admin)
):
    await upsert_category(key, body.title, body.icon_url, body.sort_order)
    await _invalidate_cache()
    return {"ok": True}


@router.delete("/category/{key}")
async def admin_delete_category(key: str, user=Depends(require_admin)):
    if not await get_category(key):
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await delete_category(key)
    await _invalidate_cache()
    return {"ok": True}


@router.post("/reorder/categories")
async def admin_reorder_categories(body: ReorderIn, user=Depends(require_admin)):
    await reorder_categories(
        [{"key": i.key, "sort_order": i.sort_order} for i in body.order]
    )
    await _invalidate_cache()
    return {"ok": True}


@router.get("/guides")
async def admin_guides_list(
    category_key: str | None = None, user=Depends(require_admin)
):
    if category_key:
        return await get_guides_by_category(category_key)
    return await get_all_guides()


@router.get("/guide/{key}")
async def admin_guide_detail(key: str, user=Depends(require_admin)):
    g_raw = await get_guide(key)
    if not g_raw:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    g: dict[str, Any] = dict(g_raw)
    return {
        **g,
        "photo": g.get("photo", []),
        "video": g.get("video", []),
        "document": g.get("document", []),
    }


@router.put("/guide/{key}")
async def admin_upsert_guide(key: str, body: GuideIn, user=Depends(require_admin)):
    from models import _validate_key
    from services.notification_service import enqueue_guide_notification

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
        await enqueue_guide_notification(key, body.title, body.category_key)
        
    return {"ok": True, "created": is_new}


@router.delete("/guide/{key}")
async def admin_delete_guide_endpoint(key: str, user=Depends(require_admin)):
    # 1. Находим гайд перед удалением, чтобы получить список файлов
    snapshot = await delete_guide(key, changed_by=user.get("id"))
    if not snapshot:
        raise HTTPException(status_code=404, detail="Гайд не найден")
    
    # 2. Собираем все ссылки на медиа в этом гайде
    urls_to_delete = set()
    
    # Ссылки из массивов
    for field in ["photo", "video", "document"]:
        for url in snapshot.get(field, []):
            if "huggingface.co" in url:
                urls_to_delete.add(url)
    
    # Ссылки из иконки
    if snapshot.get("icon_url") and "huggingface.co" in snapshot["icon_url"]:
        urls_to_delete.add(snapshot["icon_url"])
        
    # Ссылки из текста (регуляркой)
    content_text = snapshot.get("text", "")
    hf_links = re.findall(r"https://huggingface\.co/datasets/[^/]+/[^/]+/resolve/main/uploads/[^\"'\s\)]+", content_text)
    urls_to_delete.update(hf_links)
    
    # 3. Удаляем файлы из облака в фоне (чтобы не задерживать ответ)
    if urls_to_delete:
        logger.info(f"Deleting {len(urls_to_delete)} media files for guide {key}")
        asyncio.create_task(delete_files(list(urls_to_delete)))
        
    await _invalidate_cache()
    return {"ok": True, "deleted_media": len(urls_to_delete)}


@router.post("/reorder/guides")
async def admin_reorder_guides_endpoint(body: ReorderIn, user=Depends(require_admin)):
    await reorder_guides(
        [{"key": i.key, "sort_order": i.sort_order} for i in body.order]
    )
    await _invalidate_cache()
    return {"ok": True}


@router.get("/guide/{key}/history")
async def admin_guide_history_endpoint(key: str, user=Depends(require_admin)):
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


@router.get("/export")
async def admin_export(user=Depends(require_admin)):
    data = await export_all()
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": "attachment; filename=blackrose-export.json"},
    )


@router.post("/import")
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


@router.post("/translate")
async def admin_translate(request: Request, user=Depends(require_admin)):
    from services.translation_service import TranslationService
    
    try:
        body = await request.json()
        text = body.get("text", "")
        if not text:
            return {"translated": ""}
            

        # --- ШАГ 3: Безотказный вариант (Google Translate без ключей) ---
        if GoogleTranslator:
            logger.info("Using Google Translate as last resort fallback")
            translated = GoogleTranslator(source='auto', target='ru').translate(text)
            # Google Translate особенно любит переводить теги, поэтому исправляем обязательно
            translated = translated.replace("![видео]", "![video]").replace("![изображение]", "![image]")
            return {"translated": translated}
        else:
            raise Exception("No translation provider available (libraries missing)")
                
    except Exception as e:
        logger.error(f"All translation methods failed: {e}")
        raise HTTPException(status_code=500, detail=f"Критическая ошибка перевода: {str(e)}")


@router.get("/icons")
async def admin_icons(user=Depends(require_admin)):
    from icons import ALL_ICONS

    return [{"key": k, "url": v} for k, v in ALL_ICONS.items()]


@router.get("/icons/grouped")
async def admin_icons_grouped(user=Depends(require_admin)):
    from typing import Any

    from icons import (
        ADVENTURES,
        CLASS_ETC,
        GUILD,
        INFO_CATEGORIES,
        PROMOTION,
        SKILLS,
        SPIRIT,
    )

    groups: list[dict[str, Any]] = [
        {"id": "class_etc", "label": "⚔️ Классы, мечи, статы", "icons": CLASS_ETC},
        {"id": "promotion", "label": "🏆 Промоуты", "icons": PROMOTION},
        {"id": "skills", "label": "✨ Навыки", "icons": SKILLS},
        {"id": "spirit", "label": "👻 Духи и фамильяры", "icons": SPIRIT},
        {"id": "adventures", "label": "🗺️ Приключения", "icons": ADVENTURES},
        {
            "id": "info_categories",
            "label": "📋 Категории информации",
            "icons": INFO_CATEGORIES,
        },
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


@router.put("/guide/{key}/tags")
async def admin_set_tags(key: str, body: TagsIn, user=Depends(require_admin)):
    if not await get_guide(key):
        raise HTTPException(status_code=404, detail="Гайд не найден")
    await set_guide_tags(key, body.tags)
    await _invalidate_guide_cache_key(key)
    return {"ok": True}


# ── Members management ────────────────────────────────────────


@router.get("/members")
async def members_list(user=Depends(require_admin)):
    from database import list_members

    return {"members": await list_members()}


@router.post("/members/{user_id}")
async def member_add(
    user_id: int,
    request: Request,
    user=Depends(require_admin),
):
    from database import upsert_member

    body = await request.json()
    is_new = await upsert_member(
        user_id=user_id,
        username=body.get("username"),
        first_name=body.get("first_name"),
        role=body.get("role", "member"),
        added_by=user.get("id"),
    )
    logger.info(
        f"member {'added' if is_new else 'updated'}: uid={user_id} by={user.get('id')}"
    )
    return {"ok": True, "created": is_new}


@router.delete("/members/{user_id}")
async def member_remove(user_id: int, user=Depends(require_admin)):
    from database import deactivate_member

    removed = await deactivate_member(user_id)
    if not removed:
        raise HTTPException(
            status_code=404, detail="Участник не найден или уже неактивен"
        )
    logger.info(f"member deactivated: uid={user_id} by={user.get('id')}")
    return {"ok": True}


# ── Media management ────────────────────────────────────────


@router.post("/media/upload")
async def admin_upload_media(
    file: UploadFile = File(...),
    guide_key: str = "",
    user=Depends(require_admin),
):
    """Загрузка медиа файла для гайда с получением URL."""
    try:
        folder = f"guides/{guide_key}" if guide_key else "guides"
        url = await upload_file(file, folder=folder)
        return {
            "url": url,
            "filename": file.filename,
            "size": file.size,
        }
    except Exception as e:
        logger.error(f"Media upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки медиа: {e}")


@router.get("/media/list")
async def admin_media_list(user=Depends(require_admin)):
    """Получить список всех медиа файлов напрямую из Hugging Face Dataset."""
    from storage import HF_DATASET_REPO, HF_TOKEN, _public_media_url
    from huggingface_hub import HfApi
    
    if not HF_DATASET_REPO:
        return {"groups": [], "total": 0}

    try:
        api = HfApi(token=HF_TOKEN)
        # Получаем все файлы из папки uploads
        all_files = api.list_repo_files(repo_id=HF_DATASET_REPO, repo_type="dataset")
        
        # Фильтруем только те, что в папке uploads/
        media_files = [f for f in all_files if f.startswith("uploads/")]
        
        # Группируем по папкам (напр. uploads/guides/..., uploads/imported/...)
        groups_dict = {}
        for f in media_files:
            parts = f.split("/")
            if len(parts) < 3: continue # Пропускаем файлы в корне uploads
            
            folder_name = parts[1]
            if folder_name not in groups_dict:
                groups_dict[folder_name] = []
                
            groups_dict[folder_name].append({
                "name": parts[-1],
                "url": _public_media_url(f),
                "type": "video" if any(ext in f.lower() for ext in [".mp4", ".webm", ".mov"]) else "image",
                "path": f
            })

        grouped = [
            {"id": name, "label": f"📁 {name.capitalize()}", "items": items}
            for name, items in groups_dict.items()
        ]
        
        return {"groups": grouped, "total": len(media_files)}
    except Exception as e:
        logger.error(f"Failed to list HF media: {e}")
        return {"groups": [], "total": 0, "error": str(e)}


@router.get("/media/preview")
async def admin_media_preview(
    path: str,
    user=Depends(require_admin),
):
    """Получить данные и ссылку на медиа файл из облака."""
    from storage import _public_media_url
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(path)
    
    return {
        "filename": path.split("/")[-1],
        "mime_type": mime_type or "application/octet-stream",
        "url": _public_media_url(path),
    }
@router.delete("/media")
async def admin_delete_media(url: str, user=Depends(require_admin)):
    """Удалить файл из Hugging Face Dataset по URL."""
    if not url:
        raise HTTPException(status_code=400, detail="URL не указан")
    
    success = await delete_file(url)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось удалить файл")
        
    return {"ok": True}


@router.post("/cache/clear")
async def admin_clear_cache(user=Depends(require_admin)):
    """Полная очистка Redis кэша (категории + гайды)."""
    try:
        await invalidate_all()
        return {"ok": True, "message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка очистки кэша: {e}")
