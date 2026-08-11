from fastapi import APIRouter, Depends, HTTPException, Header, status
from core.config import settings
from services.guides.service import guide_service
from services.cache.redis_cache import cache_service
from services.media.service import media_cache_service
from pydantic import BaseModel

router = APIRouter(prefix="/webhook", tags=["webhook"])

class IngestGuidePayload(BaseModel):
    guide_key: str
    category_key: str
    category_title: str | None = None
    title: str
    icon_url: str | None = None
    text: str = ""
    photo: list[str] = []
    video: list[str] = []
    document: list[str] = []
    sort_order: int = 0

async def verify_ingest_token(x_ingest_token: str = Header(..., alias="X-Ingest-Token")):
    if x_ingest_token != settings.INGEST_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ingest token"
        )
    return x_ingest_token


@router.post("/ingest", dependencies=[Depends(verify_ingest_token)])
async def webhook_ingest_guide(payload: IngestGuidePayload):
    # 1. Автоматическое перманентное кэширование всех медиафайлов (Discord CDN -> /api/media/{hash})
    clean_text = await media_cache_service.process_text_media(payload.text)
    clean_photos = await media_cache_service.process_media_urls(payload.photo, media_type="photo")
    clean_videos = await media_cache_service.process_media_urls(payload.video, media_type="video")

    # 2. Call core database upsert through guide_service
    is_new = await guide_service.upsert(
        key=payload.guide_key,
        data={
            "category_key": payload.category_key,
            "category_title": payload.category_title,
            "title": payload.title,
            "icon_url": payload.icon_url,
            "text": clean_text,
            "photo": clean_photos,
            "video": clean_videos,
            "document": payload.document,
            "sort_order": payload.sort_order
        },
        changed_by="webhook_ai_ingest"
    )
    # Clear both global categories cache and specific guide details cache
    await cache_service.invalidate_all()
    await cache_service.invalidate_guide(payload.guide_key)
    return {"ok": True, "created": is_new}
