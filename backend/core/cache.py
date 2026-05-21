from functools import wraps
from typing import Callable
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from services.cache.redis_cache import cache_service
from loguru import logger

def cached(expire: int = 300):
    """
    Decorator for caching FastAPI endpoint responses.
    Cache key is generated from the request path and query parameters.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to find request in kwargs or args
            request: Request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                return await func(*args, **kwargs)

            # Generate cache key
            # Simple version: path + sorted query params
            query_params = sorted(request.query_params.items())
            query_str = "&".join([f"{k}={v}" for k, v in query_params])
            cache_key = f"cache:{request.url.path}:{query_str}"

            # Check cache
            cached_data = await cache_service.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                json_compatible = jsonable_encoder(result)
                await cache_service.set(cache_key, json_compatible, expire=expire)
                logger.debug(f"Cache stored for {cache_key}")

            return result
        return wrapper
    return decorator
