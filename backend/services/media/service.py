import base64
import hashlib
import os
import re
import ssl
import urllib.parse
import urllib.request
from sqlalchemy import select
from core.db import get_sessionmaker
from core.logging import get_logger
from models.db_models import MediaCache

logger = get_logger("blackrose.services.media")

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

MEDIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "media"))

os.makedirs(os.path.join(MEDIA_ROOT, "emojis"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "photos"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "videos"), exist_ok=True)


class MediaCacheService:
    @staticmethod
    def get_canonical_url(raw_url: str) -> tuple[str, str]:
        """Удаляет токены жизни Discord (?ex=...) и возвращает канонический URL и SHA256-хэш."""
        parsed = urllib.parse.urlparse(raw_url)
        # Очищаем query токены для Discord CDN
        if "discord" in parsed.netloc:
            canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            canonical = raw_url.split("?")[0]
        
        file_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
        return canonical, file_hash

    async def get_or_download_media(self, raw_url: str, media_type: str = "photo") -> str:
        """Получить перманентную ссылку на медиа. Скачивает 1 раз и вечно кэширует в БД и на диске."""
        if not raw_url or not raw_url.startswith("http"):
            return raw_url

        if "/api/media/" in raw_url:
            return raw_url

        canonical_url, file_hash = self.get_canonical_url(raw_url)
        permanent_path = f"/api/media/{file_hash}"

        # 1. Проверка в БД
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(MediaCache).where(MediaCache.file_hash == file_hash)
            )
            cached = res.scalar_one_or_none()
            if cached:
                return permanent_path

        # 2. Скачивание с Discord CDN
        try:
            logger.info(f"Downloading media from Discord CDN: {canonical_url}")
            req = urllib.request.Request(raw_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, context=_ssl_ctx, timeout=25) as resp:
                content_type = resp.headers.get("Content-Type", "application/octet-stream")
                data = resp.read()
        except Exception as e:
            logger.warning(f"Failed to download media {raw_url}: {e}")
            return raw_url

        if not data:
            return raw_url

        # Определяем расширение файла
        ext = "webp"
        if "image/png" in content_type:
            ext = "png"
        elif "image/jpeg" in content_type:
            ext = "jpg"
        elif "image/gif" in content_type:
            ext = "gif"
        elif "video/mp4" in content_type or raw_url.endswith(".mp4"):
            ext = "mp4"
            media_type = "video"
        elif "video/webm" in content_type or raw_url.endswith(".webm"):
            ext = "webm"
            media_type = "video"

        filename = f"{file_hash}.{ext}"
        rel_dir = "emojis" if "emojis" in raw_url or media_type == "emoji" else ("videos" if media_type == "video" else "photos")
        target_dir = os.path.join(MEDIA_ROOT, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        local_filepath = os.path.join(target_dir, filename)
        rel_path = f"media/{rel_dir}/{filename}"

        # Запись файла на диск
        try:
            with open(local_filepath, "wb") as f:
                f.write(data)
        except Exception as e:
            logger.error(f"Failed to write media file {local_filepath}: {e}")

        # Мелкие изображения (<500 KB) дублируем в Base64 в базу для 100% отката
        b64_data = None
        if len(data) <= 500 * 1024 and not media_type == "video":
            b64_data = base64.b64encode(data).decode("utf-8")

        # Сохранение в БД кэша
        async with get_sessionmaker()() as session:
            try:
                record = MediaCache(
                    canonical_url=canonical_url,
                    file_hash=file_hash,
                    filename=filename,
                    mime_type=content_type,
                    media_type=media_type,
                    local_path=rel_path,
                    file_size=len(data),
                    data_base64=b64_data,
                )
                session.add(record)
                await session.commit()
            except Exception as e:
                logger.warning(f"MediaCache insert duplicate/error for {file_hash}: {e}")
                await session.rollback()

        return permanent_path

    async def process_media_urls(self, urls: list[str], media_type: str = "photo") -> list[str]:
        """Обработать массив ссылок и вернуть массив перманентных ссылок."""
        if not urls:
            return []
        res = []
        for u in urls:
            perm = await self.get_or_download_media(u, media_type=media_type)
            res.append(perm)
        return res

    async def process_text_media(self, text: str) -> str:
        """Найти все ссылки Discord в тексте (картинки, видео, эмодзи) и заменить на вечные ссылки."""
        if not text or "cdn.discordapp.com" not in text:
            return text

        # Ищем все URL Discord CDN
        discord_urls = set(re.findall(r'https://cdn\.discordapp\.com/[^\s"\'\)\>]+', text))
        for url in discord_urls:
            m_type = "emoji" if "/emojis/" in url else ("video" if re.search(r'\.(mp4|webm|mov)($|\?)', url, re.I) else "photo")
            perm_url = await self.get_or_download_media(url, media_type=m_type)
            text = text.replace(url, perm_url)

        return text


media_cache_service = MediaCacheService()
