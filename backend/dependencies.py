import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import parse_qs

from fastapi import HTTPException, Request

logger = logging.getLogger("blackrose")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
INIT_DATA_MAX_AGE = int(os.getenv("INIT_DATA_MAX_AGE", 86400))
# JWT secret для веб-сессий (генерируй случайную строку, храни в env)
JWT_SECRET = os.getenv("JWT_SECRET", "")


def _parse_ids(raw: str) -> set[int]:
    s: set[int] = set()
    for p in raw.replace(";", ",").split(","):
        p = p.strip()
        if p.lstrip("-").isdigit():
            s.add(int(p))
    return s


import secrets

ADMIN_USERS = _parse_ids(os.getenv("ADMIN_USERS", ""))


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
    except Exception:
        pass
    return False


# Админы по умолчанию для создания при первом запуске
# Поддерживает:
# - INITIAL_ADMIN=username:password (один админ, совместимость)
# - INITIAL_ADMINS=admin1:pass1;admin2:pass2 (несколько админов)
# - ADMIN_PASSWORD=username:password (legacy)
INITIAL_ADMIN = os.getenv("INITIAL_ADMIN", os.getenv("ADMIN_PASSWORD", ""))


async def get_admin_users() -> set[int]:
    """Возвращает set admin user_id: объединяет DB members и env."""
    res = set(ADMIN_USERS)
    try:
        from database import get_admin_member_ids

        db_ids = await get_admin_member_ids()
        if db_ids:
            res.update(db_ids)
    except Exception:
        pass
    return res


def verify_telegram_init_data(init_data: str) -> dict | None:
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        hash_val = parsed.get("hash", [None])[0]
        if not hash_val:
            logger.warning("verify: hash отсутствует в initData")
            return None
        check_string = "\n".join(
            f"{k}={v[0]}" for k, v in sorted(parsed.items()) if k != "hash"
        )
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        expected = hmac.new(
            secret_key, check_string.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            logger.warning(
                "verify: HMAC не совпадает — BOT_TOKEN не соответствует initData"
            )
            return None
        auth_date = int(parsed.get("auth_date", ["0"])[0])
        age = time.time() - auth_date
        if INIT_DATA_MAX_AGE > 0 and age > INIT_DATA_MAX_AGE:
            logger.warning(
                f"verify: initData просрочен — age={age:.0f}s > max={INIT_DATA_MAX_AGE}s"
            )
            return None
        user_str = parsed.get("user", [None])[0]
        if not user_str:
            logger.warning("verify: поле user отсутствует в initData")
            return None
        return json.loads(user_str)
    except Exception as e:
        logger.error(f"verify_telegram_init_data: {e}")
        return None


# ── JWT helpers ──────────────────────────────────────────────


def _jwt_encode(payload: dict) -> str:
    """Минимальный HS256 JWT без внешних зависимостей."""
    import base64

    header = (
        base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=").decode()
    )
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    sig_input = f"{header}.{body}".encode()
    sig = hmac.new(
        JWT_SECRET.encode() or BOT_TOKEN.encode(), sig_input, hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{header}.{body}.{sig_b64}"


def _jwt_decode(token: str) -> dict | None:
    """Верифицирует и декодирует JWT. Возвращает None при любой ошибке."""

    def _pad(s: str) -> str:
        return s + "=" * (-len(s) % 4)

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, body_b64, sig_b64 = parts
        sig_input = f"{header_b64}.{body_b64}".encode()
        secret = JWT_SECRET.encode() if JWT_SECRET else BOT_TOKEN.encode()
        expected_sig = hmac.new(secret, sig_input, hashlib.sha256).digest()
        import base64 as _b64

        actual_sig = _b64.urlsafe_b64decode(_pad(sig_b64))
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload = json.loads(_b64.urlsafe_b64decode(_pad(body_b64)))
        # Проверяем exp если есть
        if "exp" in payload and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None


# ── Telegram Login Widget verification ──────────────────────


def verify_telegram_login_widget(data: dict) -> dict | None:
    """
    Верифицирует данные от Telegram Login Widget.
    https://core.telegram.org/widgets/login#checking-authorization
    """
    try:
        hash_val = data.get("hash", "")
        if not hash_val:
            return None
        check_dict = {k: v for k, v in data.items() if k != "hash"}
        check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_dict.items()))
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        expected = hmac.new(
            secret_key, check_string.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, hash_val):
            logger.warning("widget: HMAC не совпадает")
            return None
        auth_date = int(data.get("auth_date", 0))
        if time.time() - auth_date > INIT_DATA_MAX_AGE:
            logger.warning("widget: auth_date просрочен")
            return None
        return {
            "id": int(data["id"]),
            "first_name": data.get("first_name", ""),
            "username": data.get("username", ""),
            "photo_url": data.get("photo_url", ""),
        }
    except Exception as e:
        logger.error(f"verify_telegram_login_widget: {e}")
        return None


# ── Auth dependencies ────────────────────────────────────────

_GUEST_USER = {"id": 0, "first_name": "Гость", "is_guest": True}


async def require_public_user(request: Request) -> dict:
    """
    Публичные эндпоинты — открыты для всех без авторизации.
    Если есть Telegram initData или JWT — используем для идентификации.
    Если нет — возвращаем гостя.
    Никогда не выбрасывает 403.
    """
    # 1. Telegram Mini App (опционально)
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if init_data:
        user = verify_telegram_init_data(init_data)
        if user:
            return user

    # 2. JWT веб-сессия (опционально)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = _jwt_decode(token)
        if payload:
            return payload

    # 3. Гость — всегда разрешён
    return _GUEST_USER


async def optional_user(request: Request) -> dict:
    """
    Для эндпоинтов, которые хотят знать пользователя, но не требуют авторизации.
    Если есть валидный initData/JWT — возвращает user dict.
    Если нет — возвращает гостя.
    """
    return await require_public_user(request)


async def require_telegram_user(request: Request) -> dict:
    """
    Требует авторизацию (Telegram или локальный админ).
    Сначала проверяем внутренний токен бота, затем JWT (явная авторизация),
    затем — initData (автоматическая авторизация в TMA).
    """
    # 0. Внутренний токен бота (для api_client.py)
    bot_token_header = request.headers.get("X-Bot-Token", "")
    if bot_token_header and bot_token_header == BOT_TOKEN:
        return {"id": 0, "first_name": "InternalBot", "is_local_admin": True}

    # 1. JWT Bearer Token (самый специфичный)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = _jwt_decode(token)
        if payload:
            return payload
        # Если токен есть, но неверный/протухший — кидаем 401
        raise HTTPException(status_code=401, detail="Сессия истекла, войдите снова")

    # 2. Telegram Mini App initData
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if init_data:
        user = verify_telegram_init_data(init_data)
        if user:
            return user
        raise HTTPException(
            status_code=403, detail="Неверные данные авторизации Telegram"
        )

    raise HTTPException(status_code=403, detail="Требуется авторизация")


async def require_admin(request: Request) -> dict:
    """
    Требует авторизацию + проверяет что user — админ (локальный или Telegram).
    """
    user = await require_telegram_user(request)
    if user.get("is_local_admin"):
        return user

    admins = await get_admin_users()
    if user.get("id", 0) not in admins:
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user


async def get_db():
    """FastAPI Dependency for providing an async database session."""
    from database import get_sessionmaker
    
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
