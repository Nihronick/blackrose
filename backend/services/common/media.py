import os
import uuid
import tempfile
import hmac
import hashlib
import base64
import re
import asyncio
from urllib.parse import urlparse
from core.config import settings
from core.logging import get_logger
from core.http import http_client
from services.storage.hf_storage import storage_service

logger = get_logger("blackrose.services.media")

class MediaService:
    @staticmethod
    async def import_from_url(url: str, folder: str = "imported") -> str:
        """Downloads a file from URL and uploads it to our storage."""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or f"file_{uuid.uuid4().hex[:8]}"

        session = await http_client.get_session()
        async with session.get(url, timeout=60) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch {url}: {resp.status}")

            # Use a temp file to avoid large memory usage
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    tmp.write(chunk)
                tmp_path = tmp.name

            try:
                # upload_local_file expects a path string
                url = await storage_service.upload_local_file(tmp_path, filename, folder)
                return url
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    @staticmethod
    async def resolve_inline_media(content: str, folder: str = "imported") -> str:
        """
        Finds Discord attachment URLs in text, downloads them to our storage, 
        and replaces the original URLs in the text with our persistent URLs.
        """
        if not content:
            return content

        # Find all discord attachment URLs (both cdn and media domains)
        # Supports URLs that might be inside markdown like ![image](url) or plain text
        pattern = r'(https?://(?:cdn|media)\.discordapp\.(?:com|net)/attachments/[^\s\)"\'>]+)'
        urls = list(set(re.findall(pattern, content)))
        
        if not urls:
            return content
            
        logger.info(f"Found {len(urls)} inline media URLs to resolve")
        
        async def _resolve_single(url: str) -> tuple[str, str]:
            try:
                clean_url = url.rstrip('.,;!') 
                new_url = await MediaService.import_from_url(clean_url, folder)
                return url, new_url
            except Exception as e:
                logger.error(f"Failed to resolve inline media {url}: {e}")
                return url, url 

        # Limit concurrency to 5 to avoid overloading network/storage
        semaphore = asyncio.Semaphore(5)
        async def _bounded_resolve(url: str):
            async with semaphore:
                return await _resolve_single(url)

        tasks = [_bounded_resolve(u) for u in urls]
        results = await asyncio.gather(*tasks)
        
        new_content = content
        for old_url, new_url in results:
            if old_url != new_url:
                new_content = new_content.replace(old_url, new_url)
                
        return new_content

    @staticmethod
    def get_optimized_url(url: str, width: int = 0, height: int = 0, extension: str = "webp") -> str:
        """Generates a signed imgproxy URL for the given image."""
        if not settings.IMGPROXY_URL or not settings.IMGPROXY_KEY or not settings.IMGPROXY_SALT:
            return url

        if not url.startswith(("http://", "https://")):
            return url

        # Define transformations
        # rs:fill:W:H:0 (0 means no enlargement if smaller)
        resize = f"rs:fill:{width}:{height}:0" if width or height else "rs:auto"
        path = f"/{resize}/plain/{url}@{extension}"

        # Sign the path
        key = bytes.fromhex(settings.IMGPROXY_KEY)
        salt = bytes.fromhex(settings.IMGPROXY_SALT)

        msg = salt + path.encode()
        signature = hmac.new(key, msg, hashlib.sha256).digest()
        encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{settings.IMGPROXY_URL.rstrip('/')}/{encoded_sig}{path}"

media_service = MediaService()
