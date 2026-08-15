import os
import shutil
from pathlib import Path
from huggingface_hub import HfApi

def deploy():
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable is missing")
        exit(1)

    deploy_dir = Path(".deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    
    deploy_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy backend directory contents to .deploy/
    ignored_patterns = {".pytest_cache", ".ruff_cache", "__pycache__", "venv", ".env", ".git"}
    backend_dir = Path("backend")
    for item in backend_dir.iterdir():
        if item.name in ignored_patterns:
            continue
        dest = deploy_dir / item.name
        if item.is_dir():
            shutil.copytree(
                item, 
                dest, 
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache", "venv")
            )
        else:
            shutil.copy2(item, dest)
            
    # Copy Dockerfile.hf -> .deploy/Dockerfile
    dockerfile_hf = backend_dir / "Dockerfile.hf"
    if dockerfile_hf.exists():
        shutil.copy2(dockerfile_hf, deploy_dir / "Dockerfile")

    print("Uploading folder to Hugging Face Spaces...")
    api = HfApi()
    api.upload_folder(
        folder_path=str(deploy_dir),
        repo_id="Nihronick/blackrose-backend",
        repo_type="space",
        token=token,
    )
    print("Successfully deployed backend to Hugging Face Space!")

if __name__ == "__main__":
    deploy()
