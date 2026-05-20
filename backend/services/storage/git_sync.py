import base64
from core.config import settings
from core.http import http_client
from core.logging import get_logger

logger = get_logger("blackrose.services.git_sync")

class GitSyncService:
    """
    Service for syncing guide content to a GitHub repository (Wiki-style).
    """
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def sync_guide(self, key: str, title: str, content: str, category: str = "general"):
        if not settings.GITHUB_TOKEN or not settings.GITHUB_REPO:
            return

        file_path = f"guides/{category}/{key}.md"
        url = f"{self.base_url}/repos/{settings.GITHUB_REPO}/contents/{file_path}"

        # Format the markdown content
        full_md = f"# {title}\n\n{content}"
        encoded_content = base64.b64encode(full_md.encode()).decode()

        session = await http_client.get_session()

        # 1. Check if file exists to get SHA
        sha = None
        async with session.get(url, headers=self.headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                sha = data.get("sha")

        # 2. Push update
        payload = {
            "message": f"Wiki Sync: {title} ({key})",
            "content": encoded_content,
            "branch": settings.GITHUB_BRANCH
        }
        if sha:
            payload["sha"] = sha

        async with session.put(url, json=payload, headers=self.headers) as resp:
            if resp.status in (200, 201):
                logger.info(f"Successfully synced guide to Git: {key}")
            else:
                err_text = await resp.text()
                logger.error(f"Failed to sync guide to Git: {resp.status} - {err_text}")

git_sync_service = GitSyncService()
