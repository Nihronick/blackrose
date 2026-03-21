"""
Тесты для verify_telegram_init_data.

Функция проверяет HMAC-подпись initData от Telegram WebApp.
Тесты полностью автономны — не требуют БД или сети.
"""
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

# Патчим модуль до импорта, чтобы не нужна была реальная БД
import sys
import types

# Stub для database и icons модулей — они не нужны для тестов auth
for mod_name in ("database", "icons", "aiohttp"):
    sys.modules.setdefault(mod_name, types.ModuleType(mod_name))

TEST_TOKEN = "1234567890:AAFakeTokenForTestingPurposesOnly"

import os
os.environ["BOT_TOKEN"]     = TEST_TOKEN
os.environ.setdefault("DATABASE_URL",  "postgresql://test/test")
os.environ.setdefault("ALLOWED_USERS", "")
os.environ.setdefault("ADMIN_USERS",   "")

import unittest.mock as mock

with mock.patch("asyncpg.create_pool"):
    import main as app_main

# Патчим BOT_TOKEN прямо в модуле — он мог быть загружен раньше с другим значением
app_main.BOT_TOKEN = TEST_TOKEN


def _make_init_data(
    user: dict,
    bot_token: str = TEST_TOKEN,
    auth_date: int | None = None,
) -> str:
    """Генерирует валидный initData с правильной HMAC-подписью."""
    if auth_date is None:
        auth_date = int(time.time())

    params = {
        "user":      json.dumps(user, ensure_ascii=False),
        "auth_date": str(auth_date),
        "chat_type": "private",
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    signature  = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    params["hash"] = signature
    return urlencode(params)


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def patch_bot_token():
    """Гарантируем что app_main.BOT_TOKEN = TEST_TOKEN перед каждым тестом."""
    original = app_main.BOT_TOKEN
    app_main.BOT_TOKEN = TEST_TOKEN
    yield
    app_main.BOT_TOKEN = original


# ── Тесты ──────────────────────────────────────────────────────

class TestVerifyTelegramInitData:
    """verify_telegram_init_data должна возвращать dict пользователя при валидных данных
    и None при любой ошибке."""

    def test_valid_data_returns_user(self):
        user = {"id": 123456, "first_name": "Тест", "username": "testuser"}
        init_data = _make_init_data(user)
        result = app_main.verify_telegram_init_data(init_data)
        assert result is not None
        assert result["id"] == 123456
        assert result["first_name"] == "Тест"

    def test_empty_string_returns_none(self):
        assert app_main.verify_telegram_init_data("") is None

    def test_missing_hash_returns_none(self):
        init_data = "user=%7B%22id%22%3A1%7D&auth_date=1700000000"
        assert app_main.verify_telegram_init_data(init_data) is None

    def test_wrong_hash_returns_none(self):
        user = {"id": 99, "first_name": "Bad"}
        init_data = _make_init_data(user)
        # Подменяем hash на мусор
        tampered = init_data.replace(
            init_data.split("hash=")[1][:10],
            "0000000000",
        )
        assert app_main.verify_telegram_init_data(tampered) is None

    def test_wrong_token_returns_none(self):
        user = {"id": 42, "first_name": "Wrong"}
        # Подписано другим токеном
        init_data = _make_init_data(user, bot_token="9999999999:AAwrongtoken")
        assert app_main.verify_telegram_init_data(init_data) is None

    def test_expired_auth_date_returns_none(self):
        user = {"id": 7, "first_name": "Old"}
        old_ts = int(time.time()) - 999_999   # ~11 дней назад
        init_data = _make_init_data(user, auth_date=old_ts)
        # INIT_DATA_MAX_AGE = 86400 по умолчанию, 999999 > 86400
        assert app_main.verify_telegram_init_data(init_data) is None

    def test_future_auth_date_is_accepted(self):
        """auth_date в будущем проходит — Telegram иногда присылает с небольшим drift."""
        user = {"id": 8, "first_name": "Future"}
        future_ts = int(time.time()) + 60
        init_data = _make_init_data(user, auth_date=future_ts)
        # future ts: time.time() - future_ts < 0 < MAX_AGE, должен пройти
        result = app_main.verify_telegram_init_data(init_data)
        assert result is not None

    def test_malformed_json_user_returns_none(self):
        user = {"id": 5, "first_name": "Ok"}
        init_data = _make_init_data(user)
        # Ломаем JSON пользователя, но hash уже посчитан — подпись будет неверной
        broken = init_data.replace("%7B", "%FF")
        assert app_main.verify_telegram_init_data(broken) is None

    def test_user_without_username_is_ok(self):
        """username необязателен в Telegram."""
        user = {"id": 999, "first_name": "Аноним"}
        init_data = _make_init_data(user)
        result = app_main.verify_telegram_init_data(init_data)
        assert result is not None
        assert result.get("username") is None

    def test_non_string_input_returns_none(self):
        assert app_main.verify_telegram_init_data(None) is None  # type: ignore


class TestParseIds:
    """_parse_ids парсит строку ID-шников в set[int]."""

    def test_comma_separated(self):
        assert app_main._parse_ids("123,456,789") == {123, 456, 789}

    def test_semicolon_separated(self):
        assert app_main._parse_ids("1;2;3") == {1, 2, 3}

    def test_mixed_separators(self):
        assert app_main._parse_ids("1,2;3") == {1, 2, 3}

    def test_empty_string(self):
        assert app_main._parse_ids("") == set()

    def test_spaces_stripped(self):
        assert app_main._parse_ids(" 10 , 20 ") == {10, 20}

    def test_non_digit_skipped(self):
        assert app_main._parse_ids("abc,123,xyz") == {123}

    def test_negative_id_accepted(self):
        """Telegram group IDs могут быть отрицательными."""
        assert -100123456 in app_main._parse_ids("-100123456")


class TestValidateKey:
    """_validate_key разрешает только строчные буквы, цифры, _ и - до 64 символов.
    Бросает HTTPException(422) при нарушении — так FastAPI возвращает 422, не 500."""

    def test_valid_simple(self):
        assert app_main._validate_key("my_guide") == "my_guide"

    def test_valid_with_dash(self):
        assert app_main._validate_key("guide-123") == "guide-123"

    def test_valid_numbers(self):
        assert app_main._validate_key("guide123") == "guide123"

    def test_uppercase_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            app_main._validate_key("MyGuide")
        assert exc.value.status_code == 422
        assert "Ключ" in exc.value.detail

    def test_spaces_raise(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            app_main._validate_key("my guide")
        assert exc.value.status_code == 422

    def test_empty_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            app_main._validate_key("")
        assert exc.value.status_code == 422

    def test_too_long_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            app_main._validate_key("a" * 65)
        assert exc.value.status_code == 422

    def test_max_length_ok(self):
        key = "a" * 64
        assert app_main._validate_key(key) == key

    def test_cyrillic_raises(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            app_main._validate_key("гайд")
        assert exc.value.status_code == 422
