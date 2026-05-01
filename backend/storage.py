import logging
import os
import uuid
import base64
import tempfile
import subprocess
from io import BytesIO

from huggingface_hub import HfApi
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

def _compress_video_bytes(filename: str, content: bytes) -> tuple[str, bytes, bool]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".mp4", ".mov", ".webm", ".avi", ".mkv"}:
        return filename, content, False

    if len(content) <= 48 * 1024 * 1024:
        return filename, content, False

    logger.info(f"Video {filename} is > 48MB. Starting automatic compression via ffmpeg...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf_in:
        tf_in.write(content)
        temp_in = tf_in.name
    
    temp_out = tempfile.mktemp(suffix=".mp4")
    
    try:
        cmd = [
            "ffmpeg", "-y", "-i", temp_in, 
            "-vf", "scale='min(1280,iw)':-2",
            "-vcodec", "libx264", "-crf", "28", "-preset", "veryfast", 
            "-b:a", "128k", temp_out
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        with open(temp_out, "rb") as tf_out:
            compressed = tf_out.read()
            
        if len(compressed) < len(content):
            logger.info(f"Compression success: {len(content)//1024//1024}MB -> {len(compressed)//1024//1024}MB")
            stem = os.path.splitext(filename)[0]
            return f"{stem}.mp4", compressed, True
    except Exception as e:
        logger.error(f"Video compression failed: {e}")
    finally:
        if os.path.exists(temp_in):
            os.remove(temp_in)
        if os.path.exists(temp_out):
            os.remove(temp_out)
            
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
    if not optimized:
        optimized_name, content, optimized = _compress_video_bytes(optimized_name or source_name, content)

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
    except Exception as e:
        logger.error(f"Failed to upload file to Hugging Face: {e}")
        raise
    finally:
        await file.close()
        import gc
        del content
        gc.collect()
