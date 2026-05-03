import logging
import os
import uuid
import base64
import gc
from io import BytesIO
from huggingface_hub import HfApi
from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError
from core.config import settings

# Exports for compatibility with GC worker
hf_api = HfApi(token=settings.HF_TOKEN)
HF_DATASET_REPO = settings.HF_DATASET_REPO
HF_PATH = "uploads"

async def delete_files(paths: list[str]) -> int:
    """Batch delete files from HF dataset."""
    if not settings.HF_TOKEN or not HF_DATASET_REPO: return 0
    count = 0
    for path in paths:
        try:
            hf_api.delete_file(
                path_in_repo=path,
                repo_id=HF_DATASET_REPO,
                repo_type="dataset"
            )
            count += 1
        except Exception:
            continue
    return count

class HFStorageService:
    def __init__(self):
        self.api = HfApi(token=settings.HF_TOKEN)
        self.repo_id = settings.HF_DATASET_REPO
        self.path_prefix = "uploads"
        self.quality = int(os.getenv("MEDIA_IMAGE_QUALITY", "82"))
        self.max_width = int(os.getenv("MEDIA_MAX_IMAGE_WIDTH", "1920"))

    def _get_public_url(self, path: str) -> str:
        if not self.repo_id: return ""
        return f"https://huggingface.co/datasets/{self.repo_id}/resolve/main/{path}"

    def _optimize_image(self, filename: str, content: bytes) -> tuple[str, bytes, bool]:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            return filename, content, False

        try:
            with Image.open(BytesIO(content)) as img:
                original_size = len(content)
                target = img

                if self.max_width > 0 and img.width > self.max_width:
                    ratio = self.max_width / img.width
                    new_height = max(1, int(img.height * ratio))
                    target = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)

                if target.mode not in ("RGB", "RGBA"):
                    target = target.convert("RGBA" if "A" in target.getbands() else "RGB")

                out = BytesIO()
                target.save(out, format="WEBP", quality=max(1, min(100, self.quality)), method=6, optimize=True)
                optimized = out.getvalue()

                if len(optimized) >= original_size:
                    return filename, content, False

                stem = os.path.splitext(filename)[0]
                return f"{stem}.webp", optimized, True
        except UnidentifiedImageError:
            return filename, content, False

    async def upload(self, file: UploadFile, folder: str = "guides") -> str:
        if not settings.HF_TOKEN or not self.repo_id:
            raise RuntimeError("Media storage not configured")

        source_name = file.filename or ""
        content = await file.read()
        opt_name, content, optimized = self._optimize_image(source_name, content)

        ext = os.path.splitext(opt_name)[1] or os.path.splitext(source_name)[1]
        filename = f"{uuid.uuid4()}{ext}"
        full_path = f"{self.path_prefix}/{folder}/{filename}".replace("//", "/")

        try:
            self.api.upload_file(
                path_or_fileobj=content,
                path_in_repo=full_path,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Admin: Upload {filename}"
            )
            return self._get_public_url(full_path)
        except Exception as e:
            logger.error(f"HF upload failed: {e}")
            raise RuntimeError(f"Storage error: {str(e).split('?')[0]}")
        finally:
            await file.close()
            del content
            gc.collect()

    async def delete(self, url: str) -> bool:
        if not settings.HF_TOKEN or not self.repo_id: return False
        
        path = None
        marker = "/resolve/main/"
        if marker in url:
            path = url.split(marker)[1]
        
        if not path: return False

        try:
            self.api.delete_file(
                path_in_repo=path,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Admin: Delete {path}"
            )
            return True
        except Exception as e:
            logger.error(f"HF delete failed: {e}")
            return False

    async def upload_local_file(self, file_path: str, filename: str, folder: str = "guides") -> str:
        """Uploads a local file from disk with optional optimization."""
        if not settings.HF_TOKEN or not self.repo_id: return ""
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        opt_name, content, optimized = self._optimize_image(filename, content)
        ext = os.path.splitext(opt_name)[1]
        target_filename = f"{uuid.uuid4()}{ext}"
        full_path = f"{self.path_prefix}/{folder}/{target_filename}".replace("//", "/")

        try:
            self.api.upload_file(
                path_or_fileobj=content,
                path_in_repo=full_path,
                repo_id=self.repo_id,
                repo_type="dataset",
                commit_message=f"Admin: Import {target_filename}"
            )
            return self._get_public_url(full_path)
        except Exception as e:
            logger.error(f"HF upload_local failed: {e}")
            raise

    async def ping(self) -> dict:
        if not settings.HF_TOKEN or not self.repo_id:
            return {"status": "unconfigured"}
        try:
            # We just check if we can get repo info
            self.api.repo_info(repo_id=self.repo_id, repo_type="dataset")
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

storage_service = HFStorageService()
