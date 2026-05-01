import asyncio
import logging
import os
import uuid
import base64
from io import BytesIO

from huggingface_hub import HfApi
from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger("blackrose.storage")

# Hugging Face configuration
HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = os.getenv("HF_DATASET_REPO") # e.g. "Nihronick/blackrose-media"
HF_PATH = "uploads"
MEDIA_IMAGE_QUALITY = int(os.getenv("MEDIA_IMAGE_QUALITY", "82"))
MEDIA_MAX_IMAGE_WIDTH = int(os.getenv("MEDIA_MAX_IMAGE_WIDTH", "1920"))

# Initialize HF API
hf_api = HfApi(token=HF_TOKEN)

def _is_token_like(value: str | None) -> bool:
    """Checks if a string looks like a Hugging Face token."""
    if not value: return False
    return value.startswith("hf_") or len(value) > 32 and "-" not in value

if _is_token_like(HF_DATASET_REPO):
    logger.error("CRITICAL CONFIG ERROR: HF_DATASET_REPO contains a token instead of a repository ID!")

def _public_media_url(path: str) -> str:
    """
    Returns a public URL for a file in the HF Dataset.
    Using huggingface.co resolve URL which acts as a CDN.
    """
    if not HF_DATASET_REPO:
        return ""
    return f"https://huggingface.co/datasets/{HF_DATASET_REPO}/resolve/main/{path}"


def _optimize_image_bytes(filename: str, content: bytes) -> tuple[str, bytes, bool]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        return filename, content, False

    try:
        with Image.open(BytesIO(content)) as img:
            original_size = len(content)
            target = img

            if MEDIA_MAX_IMAGE_WIDTH > 0 and img.width > MEDIA_MAX_IMAGE_WIDTH:
                ratio = MEDIA_MAX_IMAGE_WIDTH / img.width
                new_height = max(1, int(img.height * ratio))
                target = img.resize((MEDIA_MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)

            if target.mode not in ("RGB", "RGBA"):
                target = target.convert("RGBA" if "A" in target.getbands() else "RGB")

            out = BytesIO()
            target.save(
                out,
                format="WEBP",
                quality=max(1, min(100, MEDIA_IMAGE_QUALITY)),
                method=6,
                optimize=True,
            )
            optimized = out.getvalue()

            # Keep original when WEBP is not smaller
            if len(optimized) >= original_size:
                return filename, content, False

            stem = os.path.splitext(filename)[0]
            return f"{stem}.webp", optimized, True
    except UnidentifiedImageError:
        return filename, content, False


async def upload_file(file: UploadFile, folder: str = "guides") -> str:
    """
    Uploads a file directly to the Hugging Face Dataset.
    Returns a public resolve URL.
    """
    if not HF_TOKEN or not HF_DATASET_REPO:
        logger.warning("HF_TOKEN or HF_DATASET_REPO not configured, file upload failed")
        raise RuntimeError("Media storage is not configured (check HF_TOKEN and HF_DATASET_REPO variables)")

    # Read file content
    source_name = file.filename or ""
    content = await file.read()
    
    # Optimization
    optimized_name, content, optimized = _optimize_image_bytes(source_name, content)

    # Generate unique filename
    ext = os.path.splitext(optimized_name)[1] if optimized_name else os.path.splitext(source_name)[1]
    filename = f"{uuid.uuid4()}{ext}"
    full_path = f"{HF_PATH}/{folder}/{filename}".replace("//", "/")

    if optimized:
        logger.info(f"File optimized before upload: {source_name} -> {filename}")

    try:
        # Upload to Hugging Face Dataset
        hf_api.upload_file(
            path_or_fileobj=content,
            path_in_repo=full_path,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            commit_message=f"Admin: Upload {filename}"
        )
        logger.info(f"File uploaded to Hugging Face: {full_path}")
        return _public_media_url(full_path)
    except RepositoryNotFoundError:
        error_msg = f"Repository '{HF_DATASET_REPO}' not found. Check HF_DATASET_REPO secret."
        if _is_token_like(HF_DATASET_REPO):
            error_msg = "HF_DATASET_REPO appears to be a token instead of a repository ID. Check Space secrets."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except HfHubHTTPError as e:
        # Sanitize error to avoid leaking token/URL
        status_code = getattr(e.response, "status_code", "Unknown")
        logger.error(f"HF Hub API error ({status_code}): {e}")
        raise RuntimeError(f"Hugging Face API error: {status_code}")
    except Exception as e:
        logger.error(f"Failed to upload file to Hugging Face: {e}")
        raise RuntimeError(f"Internal storage error: {str(e).split('?')[0]}") # Strip potential query params with tokens
    finally:
        await file.close()
        import gc
        del content
        gc.collect()

def _get_hf_path_from_url(url: str) -> str | None:
    """Извлекает путь файла в репозитории из публичного URL."""
    if not HF_DATASET_REPO or HF_DATASET_REPO not in url:
        return None
    
    # URL format: https://huggingface.co/datasets/Nihronick/blackrose-media/resolve/main/uploads/guides/xxx.webp
    marker = "/resolve/main/"
    if marker in url:
        return url.split(marker)[1]
    return None

async def delete_file(path_or_url: str) -> bool:
    """Удаляет файл из Hugging Face Dataset по пути или URL."""
    if not HF_TOKEN or not HF_DATASET_REPO:
        return False
        
    path = _get_hf_path_from_url(path_or_url) if "http" in path_or_url else path_or_url
    if not path:
        return False

    try:
        hf_api.delete_file(
            path_in_repo=path,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            commit_message=f"Admin: Delete {path}"
        )
        logger.info(f"File deleted from HF: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete file from HF {path}: {e}")
        return False

async def delete_files(paths_or_urls: list[str]) -> int:
    """Массовое удаление файлов."""
    count = 0
    for p in paths_or_urls:
        if await delete_file(p):
            count += 1
    return count
