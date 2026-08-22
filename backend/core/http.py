import aiohttp
import httpx
from typing import Optional
from core.logging import get_logger

logger = get_logger("blackrose.core.http")

class HttpClient:
    _client: Optional[httpx.AsyncClient] = None
    _aio_session: Optional[aiohttp.ClientSession] = None

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return cls._client

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """Returns a shared aiohttp ClientSession for streaming and aiohttp-based callers."""
        if cls._aio_session is None or cls._aio_session.closed:
            connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=60)
            cls._aio_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return cls._aio_session

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
        if cls._aio_session and not cls._aio_session.closed:
            await cls._aio_session.close()
            cls._aio_session = None

http_client = HttpClient()
