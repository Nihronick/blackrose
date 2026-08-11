import base64
import os
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy import select

from core.db import get_sessionmaker
from core.logging import get_logger
from models.db_models import MediaCache

router = APIRouter(tags=["media"])
logger = get_logger("blackrose.api.media")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


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
