import pytest
import time
import json
import hmac
import hashlib
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from core.config import settings

# ── Test Data ──────────────────────────────────────────────────
TEST_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
TEST_UID = 12345678
ADMIN_UID = 987654321
settings.BOT_TOKEN = TEST_TOKEN
settings.ADMIN_USERS = f"{ADMIN_UID}"

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

@pytest.fixture
def client():
    # Disable lifespan for tests to avoid DB/Inngest init
    with patch("main.app.router.lifespan_context", AsyncMock()):
        with TestClient(app) as c:
            yield c

# ── Tests ──────────────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

class TestAuth:
    def test_auth_guest(self, client):
        r = client.get("/api/auth")
        assert r.status_code == 200
        assert r.json()["is_guest"] is True

    def test_auth_user(self, client):
        r = client.get("/api/auth", headers=USER_HEADERS)
        assert r.status_code == 200
        assert r.json()["authorized"] is True
        assert r.json()["is_admin"] is False

    def test_auth_admin(self, client):
        r = client.get("/api/auth", headers=ADMIN_HEADERS)
        assert r.status_code == 200
        assert r.json()["is_admin"] is True

class TestGuides:
    @patch("services.guides.service.GuideService.get_categories")
    def test_get_categories(self, mock_get_categories, client):
        mock_get_categories.return_value = [{"key": "test", "title": "Test"}]
        r = client.get("/api/categories")
        assert r.status_code == 200
        assert len(r.json()["categories"]) == 1

    @patch("services.guides.service.GuideService.get_guide")
    def test_get_guide_not_found(self, mock_get_guide, client):
        mock_get_guide.return_value = None
        r = client.get("/api/guide/missing")
        assert r.status_code == 404

    @patch("services.guides.service.GuideService.get_guide")
    def test_get_guide_found(self, mock_get_guide, client):
        mock_get_guide.return_value = {
            "key": "test",
            "title": "Test Guide",
            "text": "Hello",
            "category_key": "cat"
        }
        r = client.get("/api/guide/test")
        assert r.status_code == 200
        assert r.json()["title"] == "Test Guide"

class TestAdmin:
    def test_admin_access_denied(self, client):
        r = client.get("/api/admin/guides", headers=USER_HEADERS)
        assert r.status_code == 403

    @patch("services.guides.service.GuideService.get_all_guides")
    def test_admin_access_granted(self, mock_get_guides, client):
        mock_get_guides.return_value = []
        r = client.get("/api/admin/guides", headers=ADMIN_HEADERS)
        assert r.status_code == 200
