import base64
import os
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy import select

from core.auth import require_admin
from core.db import get_sessionmaker
from core.logging import get_logger
from models.db_models import MediaCache
from pydantic import BaseModel
from fastapi import Depends

router = APIRouter(tags=["media"])
logger = get_logger("blackrose.api.media")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class DirectMediaCacheIn(BaseModel):
    canonical_url: str
    data_base64: str
    mime_type: str = "image/png"
    media_type: str = "photo"


@router.post("/admin/media/direct-cache")
async def direct_media_cache(body: DirectMediaCacheIn, user=Depends(require_admin)):
    """Прямое сохранение медиафайла в базу данных PostgreSQL для постоянного кэширования."""
    import hashlib
    from core.url_validator import validate_media_url, SSRFError

    # SSRF Protection: validate canonical URL
    try:
        validate_media_url(body.canonical_url)
    except SSRFError as e:
        raise HTTPException(status_code=400, detail=f"URL rejected (SSRF protection): {e}")

    canonical = body.canonical_url.split("?")[0]
    file_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    ext = "png"
    if "jpeg" in body.mime_type or "jpg" in body.mime_type:
        ext = "jpg"
    elif "webp" in body.mime_type:
        ext = "webp"
    elif "gif" in body.mime_type:
        ext = "gif"
    elif "mp4" in body.mime_type:
        ext = "mp4"
    elif "webm" in body.mime_type:
        ext = "webm"

    filename = f"{file_hash}.{ext}"
    rel_dir = "emojis" if body.media_type == "emoji" else ("videos" if body.media_type == "video" else "photos")
    rel_path = f"media/{rel_dir}/{filename}"
    file_size = int(len(body.data_base64) * 3 / 4)

    # Сохраняем физический файл на диск сразу
    abs_path = os.path.join(BASE_DIR, rel_path)
    try:
        raw_bytes = base64.b64decode(body.data_base64)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        logger.warning(f"Failed to write local media file: {e}")

    async with get_sessionmaker()() as session:
        res = await session.execute(
            select(MediaCache).where((MediaCache.file_hash == file_hash) | (MediaCache.canonical_url == canonical))
        )
        cached = res.scalar_one_or_none()
        if cached:
            cached.data_base64 = body.data_base64
            cached.mime_type = body.mime_type
            cached.file_size = file_size
            cached.local_path = rel_path
            await session.commit()
            return {"ok": True, "file_hash": file_hash, "url": f"/api/media/{file_hash}"}

        record = MediaCache(
            canonical_url=canonical,
            file_hash=file_hash,
            filename=filename,
            mime_type=body.mime_type,
            media_type=body.media_type,
            local_path=rel_path,
            file_size=file_size,
            data_base64=body.data_base64,
        )
        session.add(record)
        await session.commit()

    return {"ok": True, "file_hash": file_hash, "url": f"/api/media/{file_hash}"}


@router.get("/media/{file_hash}")
async def serve_media(file_hash: str):
    """Высокопроизводительная отдача медиафайлов с вечным браузерным кэшированием."""
    async with get_sessionmaker()() as session:
        res = await session.execute(
            select(MediaCache).where(MediaCache.file_hash == file_hash)
        )
        record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Медиафайл не найден")

    # 1. Пробуем отдать физический файл с диска
    abs_path = os.path.join(BASE_DIR, record.local_path)
    if os.path.exists(abs_path):
        return FileResponse(
            path=abs_path,
            media_type=record.mime_type,
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "ETag": f'"{file_hash}"',
            },
        )

    # 2. Если файл временно сбросился при рестарте контейнера — восстанавливаем из Base64 из базы!
    if record.data_base64:
        try:
            raw_bytes = base64.b64decode(record.data_base64)
            # Восстанавливаем файл на диск
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "wb") as f:
                f.write(raw_bytes)
            
            return Response(
                content=raw_bytes,
                media_type=record.mime_type,
                headers={
                    "Cache-Control": "public, max-age=31536000, immutable",
                    "ETag": f'"{file_hash}"',
                },
            )
        except Exception as e:
            logger.error(f"Failed to restore media from Base64 for {file_hash}: {e}")

    raise HTTPException(status_code=404, detail="Файл медиа недоступен")
