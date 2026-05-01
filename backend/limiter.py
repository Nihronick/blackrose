from slowapi import Limiter
from slowapi.util import get_remote_address

def get_real_ip(request):
    """
    Извлекает реальный IP пользователя, учитывая прокси (X-Forwarded-For).
    Это критично при деплое на Hugging Face / Cloudflare.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Берем самый левый IP (оригинальный клиент)
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip, default_limits=["200/minute"])
