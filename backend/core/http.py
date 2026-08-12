import httpx
from typing import Optional
from core.logging import get_logger

logger = get_logger("blackrose.core.http")

class HttpClient:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return cls._client

    @classmethod
    async def get(cls, url: str, **kwargs):
        client = cls._get_client()
        return await client.get(url, **kwargs)

    @classmethod
    async def post(cls, url: str, **kwargs):
        client = cls._get_client()
        return await client.post(url, **kwargs)

    @classmethod
    async def close(cls):
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None

http_client = HttpClient()
