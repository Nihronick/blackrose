from slowapi import Limiter
from slowapi.util import get_remote_address

# Default fallback rate limiter (200 requests / minute)
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
