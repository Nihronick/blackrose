"""
Интеграционные тесты FastAPI endpoints.

Используют httpx.AsyncClient + lifespan override — реальная БД не нужна.
Проверяют: статус-коды, структуру ответов, поведение при неверной авторизации.

Запуск:
    pip install -r requirements-dev.txt
    pytest tests/test_api_endpoints.py -v
"""

import hashlib
import hmac
import json
import os
import sys
import time
import types
import unittest.mock as mock
from unittest.mock import AsyncMock, MagicMock

import pytest

# ── Stub-модули ────────────────────────────────────────────────
import unittest.mock as mock
import types

# Создаем базовый мок для базы данных. Все атрибуты по умолчанию - AsyncMock
class AsyncMockModule(mock.MagicMock):
    def __getattr__(self, name):
        attr = super().__getattr__(name)
        if isinstance(attr, mock.MagicMock) and not isinstance(attr, mock.AsyncMock):
            # Превращаем в AsyncMock при первом доступе, если это еще не он
            setattr(self, name, mock.AsyncMock())
            return getattr(self, name)
        return attr

_db = AsyncMockModule()
sys.modules["database"] = _db
_db_stub = _db # Coвместимость

# Настраиваем возвращаемые значения
_db.get_admin_member_ids.return_value = set()
_db.get_all_tags.return_value = []
_db.get_categories_with_counts.return_value = []
_db.get_category.return_value = None
_db.get_comments.return_value = []
_db.get_guide.return_value = None
_db.get_guide_tags.return_value = []
_db.get_guides_by_category.return_value = []
_db.get_guides_by_tag.return_value = []
_db.get_top_guides.return_value = []
_db.get_user_subscriptions.return_value = []
_db.increment_views.return_value = 0
_db.search_guides.return_value = []
_db.get_subscribers.return_value = []
_db.get_all_guides.return_value = []
# Синхронные методы
_db.get_sessionmaker = mock.MagicMock()

# Icons stub
_icons = mock.MagicMock()
_icons.ALL_ICONS = {"HP": "https://cdn.example.com/hp.png"}
_icons._ICONS_LOWER = {"hp": "HP"}
_icons.get_icon.side_effect = lambda name: _icons.ALL_ICONS.get(name, f"mock://{name}")
sys.modules["icons"] = _icons
_icons_stub = _icons

sys.modules["aiohttp"] = mock.MagicMock()

TEST_TOKEN = "9876543210:AATestTokenForEndpointTests"
TEST_UID = 111222333
ADMIN_UID = 999888777

os.environ["BOT_TOKEN"] = TEST_TOKEN
os.environ["DATABASE_URL"] = "postgresql://test/test"
os.environ["ALLOWED_USERS"] = str(TEST_UID)
os.environ["ADMIN_USERS"] = str(ADMIN_UID)

with mock.patch("asyncpg.create_pool"):
    import main as app_main # type: ignore
    import dependencies # type: ignore

# Обновляем whitelist после env переменных (модуль уже загружен)
dependencies.ALLOWED_USERS = {TEST_UID, ADMIN_UID}
dependencies.ADMIN_USERS = {ADMIN_UID}


# ── Helpers ────────────────────────────────────────────────────


def _make_init_data(uid: int, first_name: str = "Test") -> str:
    user = {"id": uid, "first_name": first_name}
    auth_date = int(time.time())
    params = {
        "user": json.dumps(user, ensure_ascii=False),
        "auth_date": str(auth_date),
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", TEST_TOKEN.encode(), hashlib.sha256).digest()
    sig = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = sig
    from urllib.parse import urlencode

    return urlencode(params)


USER_HEADERS = {"X-Telegram-Init-Data": _make_init_data(TEST_UID)}
ADMIN_HEADERS = {"X-Telegram-Init-Data": _make_init_data(ADMIN_UID, "Admin")}
NO_AUTH = {}


# ── Fixtures ───────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def patch_auth_state():
    """Гарантируем правильный BOT_TOKEN и whitelist перед каждым тестом.
    test_auth.py загружается первым и может перезаписать BOT_TOKEN в модуле."""
    orig_token = dependencies.BOT_TOKEN
    orig_allowed = dependencies.ALLOWED_USERS
    orig_admins = dependencies.ADMIN_USERS
    dependencies.BOT_TOKEN = TEST_TOKEN
    dependencies.ALLOWED_USERS = {TEST_UID, ADMIN_UID}
    dependencies.ADMIN_USERS = {ADMIN_UID}
    yield
    dependencies.BOT_TOKEN = orig_token
    dependencies.ALLOWED_USERS = orig_allowed
    dependencies.ADMIN_USERS = orig_admins


@pytest.fixture
def client():
    """Синхронный TestClient — подходит для большинства тестов."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("fastapi[testclient] / httpx not installed")

    # Переопределяем lifespan чтобы не поднимать реальное соединение с БД
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    app_main.app.router.lifespan_context = noop_lifespan
    with TestClient(app_main.app, raise_server_exceptions=False) as c:
        yield c


# ── /api/health ────────────────────────────────────────────────


class TestHealth:
    def test_returns_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_version_present(self, client):
        r = client.get("/api/health")
        assert "version" in r.json()


# ── /api/auth ──────────────────────────────────────────────────


class TestAuthEndpoint:
    def test_no_header_is_guest(self, client):
        r = client.get("/api/auth", headers=NO_AUTH)
        assert r.status_code == 200
        assert r.json()["is_guest"] is True

    def test_valid_user_returns_authorized(self, client):
        r = client.get("/api/auth", headers=USER_HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert body["authorized"] is True
        assert body["user_id"] == TEST_UID
        assert body["is_admin"] is False

    def test_admin_user_is_admin_true(self, client):
        r = client.get("/api/auth", headers=ADMIN_HEADERS)
        assert r.status_code == 200
        assert r.json()["is_admin"] is True

    def test_garbage_init_data_is_guest(self, client):
        r = client.get("/api/auth", headers={"X-Telegram-Init-Data": "garbage"})
        assert r.status_code == 200
        assert r.json()["is_guest"] is True


# ── /api/categories ────────────────────────────────────────────


class TestCategoriesEndpoint:
    def test_no_auth_is_ok(self, client):
        r = client.get("/api/categories", headers=NO_AUTH)
        assert r.status_code == 200

    def test_valid_user_returns_list(self, client):
        _db_stub.get_pool.return_value = _make_pool_mock([])
        r = client.get("/api/categories", headers=USER_HEADERS)
        assert r.status_code == 200
        assert "categories" in r.json()

    def test_categories_is_list(self, client):
        _db_stub.get_pool.return_value = _make_pool_mock([])
        r = client.get("/api/categories", headers=USER_HEADERS)
        assert isinstance(r.json()["categories"], list)


# ── /api/search ────────────────────────────────────────────────


class TestSearchEndpoint:
    def test_no_auth_is_ok(self, client):
        r = client.get("/api/search?q=test", headers=NO_AUTH)
        assert r.status_code == 200

    def test_short_query_returns_empty(self, client):
        r = client.get("/api/search?q=a", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_missing_q_returns_empty(self, client):
        r = client.get("/api/search", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["results"] == []

    def test_valid_query_calls_db(self, client):
        _db_stub.search_guides.return_value = [
            {"key": "g1", "title": "Гайд 1", "icon_url": None, "category_key": "cat1"}
        ]
        r = client.get("/api/search?q=гайд", headers=USER_HEADERS)
        assert r.status_code == 200
        results = r.json()["results"]
        assert len(results) == 1
        assert results[0]["key"] == "g1"

    def test_search_result_has_required_fields(self, client):
        _db_stub.search_guides.return_value = [
            {"key": "g2", "title": "Test", "icon_url": "https://x.com/i.png", "category_key": "c"}
        ]
        r = client.get("/api/search?q=test", headers=USER_HEADERS)
        item = r.json()["results"][0]
        for field in ("key", "title", "icon", "category_key"):
            assert field in item, f"Поле '{field}' отсутствует в результате поиска"


# ── /api/guide/:key ────────────────────────────────────────────


class TestGuideEndpoint:
    def test_no_auth_is_ok(self, client):
        r = client.get("/api/guide/test", headers=NO_AUTH)
        assert r.status_code == 200 or r.status_code == 404

    def test_missing_guide_returns_404(self, client):
        _db_stub.get_guide.return_value = None
        r = client.get("/api/guide/missing", headers=USER_HEADERS)
        assert r.status_code == 404

    def test_existing_guide_returns_200(self, client):
        _db_stub.get_guide.return_value = {
            "key": "test_guide",
            "title": "Тест",
            "icon_url": None,
            "text": "**жирный текст**",
            "photo": [],
            "video": [],
            "document": [],
            "views": 5,
        }
        _db_stub.get_guide_tags.return_value = ["тег1"]
        r = client.get("/api/guide/test_guide", headers=USER_HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert body["key"] == "test_guide"
        assert "**жирный текст**" in body["text"]  # markdown не отрендерен на бэкенде
        assert body["views"] == 5
        assert "тег1" in body["tags"]

    def test_guide_text_is_markdown(self, client):
        _db_stub.get_guide.return_value = {
            "key": "g",
            "title": "G",
            "icon_url": None,
            "text": "## Заголовок\n- пункт",
            "photo": [],
            "video": [],
            "document": [],
            "views": 0,
        }
        _db_stub.get_guide_tags.return_value = []
        r = client.get("/api/guide/g", headers=USER_HEADERS)
        assert "## Заголовок" in r.json()["text"]


# ── Admin endpoints — доступ ───────────────────────────────────


class TestAdminAccess:
    def test_regular_user_cannot_access_admin(self, client):
        r = client.get("/api/admin/guides", headers=USER_HEADERS)
        assert r.status_code == 403

    def test_admin_can_access_admin_guides(self, client):
        _db_stub.get_all_guides.return_value = []
        r = client.get("/api/admin/guides", headers=ADMIN_HEADERS)
        assert r.status_code == 200

    def test_admin_guide_put_validates_key(self, client):
        """Ключ с заглавными буквами должен отклоняться."""
        payload = {
            "category_key": "cat1",
            "title": "Тест",
            "text": "",
            "photo": [],
            "video": [],
            "document": [],
            "sort_order": 0,
        }
        r = client.put("/api/admin/guide/InvalidKey", json=payload, headers=ADMIN_HEADERS)
        assert r.status_code == 422

    def test_admin_guide_put_empty_title_rejected(self, client):
        payload = {
            "category_key": "cat1",
            "title": "   ",  # только пробелы
            "text": "",
            "photo": [],
            "video": [],
            "document": [],
            "sort_order": 0,
        }
        r = client.put("/api/admin/guide/valid_key", json=payload, headers=ADMIN_HEADERS)
        assert r.status_code == 422

    def test_admin_delete_nonexistent_guide_returns_404(self, client):
        _db_stub.get_guide.return_value = None
        r = client.delete("/api/admin/guide/nope", headers=ADMIN_HEADERS)
        assert r.status_code == 404


# ── /api/top ──────────────────────────────────────────────────


class TestTopEndpoint:
    def test_no_auth_is_ok(self, client):
        r = client.get("/api/top", headers=NO_AUTH)
        assert r.status_code == 200

    def test_returns_results_list(self, client):
        _db_stub.get_top_guides.return_value = []
        r = client.get("/api/top", headers=USER_HEADERS)
        assert r.status_code == 200
        assert "results" in r.json()


# ── /api/guide/:key/view ──────────────────────────────────────


class TestViewEndpoint:
    def test_increments_view(self, client):
        _db_stub.increment_views.return_value = 42
        _db_stub.get_guide.return_value = {"key": "g", "title": "G"}
        r = client.post("/api/guide/some_guide/view", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["views"] == 42


# ── Helpers ────────────────────────────────────────────────────


def _make_pool_mock(rows):
    """Мок asyncpg Pool для endpoints, которые делают прямые conn.fetch."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=rows)
    conn.fetchrow = AsyncMock(return_value=None)
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)

    pool = AsyncMock()
    pool.acquire = MagicMock(return_value=conn)
    return pool
