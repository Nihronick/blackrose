import aiohttp
from typing import Optional
from core.logging import get_logger

logger = get_logger("blackrose.core.http")

class HttpClient:
    _session: Optional[aiohttp.ClientSession] = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None or cls._session.closed:
            logger.info("Creating new global aiohttp session")
            # Timeout for safety
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            cls._session = aiohttp.ClientSession(timeout=timeout)
        return cls._session

    @classmethod
    async def close(cls):
        if cls._session and not cls._session.closed:
            logger.info("Closing global aiohttp session")
            await cls._session.close()
            cls._session = None

http_client = HttpClient()
