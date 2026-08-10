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
    backend_dir = Path("backend")
    for item in backend_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, deploy_dir / item.name)
        else:
            shutil.copy2(item, deploy_dir / item.name)
            
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
