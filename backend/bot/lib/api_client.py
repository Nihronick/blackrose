import urllib.parse
import aiohttp
from loguru import logger
from bot.config import API_URL, API_TOKEN

class BotApiClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url.rstrip("/") if base_url else None

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict | None:
        if not self.base_url:
            logger.warning("API_URL is not configured.")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {"X-Bot-Token": API_TOKEN}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=5), **kwargs) as r:
                    if r.status in (200, 201):
                        return await r.json()
                    elif r.status == 404:
                        return {"_error": 404}
                    else:
                        logger.warning(f"API {method} {endpoint} failed: {r.status}")
                        return {"_error": r.status}
        except Exception as e:
            logger.warning(f"APIClient error at {endpoint}: {e}")
            return None

    async def search(self, query: str) -> list[dict]:
        data = await self._request("GET", f"/api/search?q={urllib.parse.quote(query)}")
        if data and "_error" not in data:
            return data.get("results", [])
        return []

    async def get_members(self) -> list[dict]:
        data = await self._request("GET", "/api/admin/members")
        if data and "_error" not in data:
            return data.get("members", [])
        return []

    async def add_member(self, target_id: int, role: str) -> dict:
        return await self._request("POST", f"/api/admin/members/{target_id}", json={"role": role, "first_name": ""})

    async def delete_member(self, target_id: int) -> dict:
        return await self._request("DELETE", f"/api/admin/members/{target_id}")

    async def notify_subscribers(self, guide_key: str, guide_title: str, category_key: str) -> dict | None:
        payload = {
            "guide_key": guide_key,
            "guide_title": guide_title,
            "category_key": category_key,
            "bot_token": API_TOKEN,
        }
        # Increased timeout for notification process
        return await self._request("POST", "/api/internal/notify", json=payload, timeout=aiohttp.ClientTimeout(total=60))

api_client = BotApiClient()
