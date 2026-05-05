import os
import uuid
import tempfile
import hmac
import hashlib
import base64
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
