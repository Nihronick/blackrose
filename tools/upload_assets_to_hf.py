import os
import logging
from huggingface_hub import HfApi
from dotenv import load_dotenv

# Load env vars for HF_TOKEN
load_dotenv(os.path.join("backend", ".env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hf_sync")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_DATASET_REPO = "Nihronick/blackrose-media" # Target repo

def sync_assets():
    if not HF_TOKEN:
        logger.error("HF_TOKEN not found in .env! Cannot upload.")
        return

    api = HfApi(token=HF_TOKEN)
    
    # Source: local frontend/public/assets
    local_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "assets"))
    
    if not os.path.exists(local_assets):
        logger.error(f"Local assets directory not found: {local_assets}")
        return

    logger.info(f"Uploading assets from {local_assets} to {HF_DATASET_REPO}...")

    try:
        # Uploading folders to keep structure
        api.upload_folder(
            folder_path=local_assets,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            path_in_repo="assets",
            commit_message="Sync: Uploading local assets to HF"
        )
        logger.info("Assets successfully uploaded to HF!")
        logger.info(f"Your icons are now available at: https://huggingface.co/datasets/{HF_DATASET_REPO}/resolve/main/assets/images/icons/")
    except Exception as e:
        logger.error(f"Upload failed: {e}")

if __name__ == "__main__":
    sync_assets()
