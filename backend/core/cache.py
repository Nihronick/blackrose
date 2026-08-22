import hashlib
import json
from functools import wraps
from typing import Callable
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from services.cache.redis_cache import cache_service
from loguru import logger

def cached(expire: int = 300):
    """
    Decorator for caching FastAPI endpoint responses.
    Cache key is generated from the request path and query parameters.
    
    Adds HTTP cache headers:
    - Cache-Control: public, max-age={expire}, stale-while-revalidate=60
    - ETag: content hash for 304 Not Modified support
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
                
                # Generate ETag from cached data
                etag = _generate_etag(cached_data)
                
                # Check If-None-Match header for 304 Not Modified
                if_none_match = request.headers.get("if-none-match", "")
                if if_none_match and if_none_match.strip('"') == etag:
                    return Response(
                        status_code=304,
                        headers={
                            "ETag": f'"{etag}"',
                            "Cache-Control": f"public, max-age={expire}, stale-while-revalidate=60",
                        },
                    )
                
                return JSONResponse(
                    content=cached_data,
                    headers={
                        "ETag": f'"{etag}"',
                        "Cache-Control": f"public, max-age={expire}, stale-while-revalidate=60",
                        "X-Cache": "HIT",
                    },
                )

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                if isinstance(result, Response):
                    return result
                json_compatible = jsonable_encoder(result)
                await cache_service.set(cache_key, json_compatible, expire=expire)
                logger.debug(f"Cache stored for {cache_key}")
                
                etag = _generate_etag(json_compatible)
                return JSONResponse(
                    content=json_compatible,
                    headers={
                        "ETag": f'"{etag}"',
                        "Cache-Control": f"public, max-age={expire}, stale-while-revalidate=60",
                        "X-Cache": "MISS",
                    },
                )

            return result
        return wrapper
    return decorator


def _generate_etag(data) -> str:
    """Generate a short ETag hash from response data."""
    raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]
