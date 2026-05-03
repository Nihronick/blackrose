import hashlib
import hmac
import json
import logging
import secrets
import time
from urllib.parse import parse_qs
import base64
from fastapi import HTTPException, Request
from core.config import settings
from core.db import get_sessionmaker

logger = logging.getLogger("blackrose.core.auth")

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"pbkdf2:sha256:100000${salt}${hash_obj.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        parts = hashed.split("$")
        if len(parts) == 3:
            algo_iters, salt, hash_hex = parts
            hash_obj = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return hash_obj.hex() == hash_hex
    except Exception as e:
        logger.debug(f"verify_password error: {e}")
    return False

def verify_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        hash_val = parsed.get("hash", [None])[0]
        if not hash_val: return None
        check_string = "\n".join(
            f"{k}={v[0]}" for k, v in sorted(parsed.items()) if k != "hash"
        )
        secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, hash_val): return None
        
        auth_date = int(parsed.get("auth_date", ["0"])[0])
        if settings.INIT_DATA_MAX_AGE > 0 and (time.time() - auth_date) > settings.INIT_DATA_MAX_AGE:
            return None
        
        user_str = parsed.get("user", [None])[0]
        return json.loads(user_str) if user_str else None
    except Exception as e:
        logger.error(f"verify_telegram_init_data error: {e}")
        return None

import jwt

def jwt_encode(payload: dict) -> str:
    secret = (settings.JWT_SECRET or settings.BOT_TOKEN)
    return jwt.encode(payload, secret, algorithm="HS256")

def jwt_decode(token: str) -> dict | None:
    try:
        secret = (settings.JWT_SECRET or settings.BOT_TOKEN)
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.debug("JWT token expired")
    except jwt.InvalidTokenError as e:
        logger.debug(f"JWT decode error: {e}")
    except Exception as e:
        logger.debug(f"Unexpected JWT error: {e}")
    return None

async def require_telegram_user(request: Request) -> dict:
    bot_token_header = request.headers.get("X-Bot-Token", "")
    if bot_token_header and bot_token_header == settings.BOT_TOKEN:
        return {"id": 0, "first_name": "InternalBot", "is_local_admin": True}

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = jwt_decode(auth_header[7:])
        if payload: return payload
        raise HTTPException(status_code=401, detail="Сессия истекла")

    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if init_data:
        user = verify_telegram_init_data(init_data)
        if user: return user
        raise HTTPException(status_code=403, detail="Неверные данные Telegram")

    raise HTTPException(status_code=403, detail="Требуется авторизация")

async def require_admin(request: Request) -> dict:
    user = await require_telegram_user(request)
    if user.get("is_local_admin"): return user
    
    # Lazy import to avoid circular dependencies
    from services.common.members import member_service
    is_admin = await member_service.is_admin(user.get("id", 0))
    if is_admin or user.get("id", 0) in settings.admin_user_ids:
        return user
    
    if user.get("id", 0) not in admins:
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user

async def get_db():
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
