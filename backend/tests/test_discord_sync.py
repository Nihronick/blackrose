import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from services.discord_sync.translator import sanitize_discord_markdown, translate_en_to_ru
from core.auth import require_admin

# Mock lifespan context
@pytest.fixture(autouse=True)
def mock_lifespan():
    with patch("main.app.router.lifespan_context") as mock:
        async def _noop_lifespan(app):
            yield
        mock.return_value = _noop_lifespan(app)
        yield


def test_sanitize_discord_markdown():
    raw = "Check this <@123456> build in <#987654>! <:blitz_gold:1001> ||Secret tip inside||"
    cleaned, photos, videos = sanitize_discord_markdown(raw)
    
    assert "<@123456>" not in cleaned
    assert "<#987654>" not in cleaned
    assert "cdn.discordapp.com/emojis/1001.webp" in cleaned
    assert "<details" in cleaned
    assert "Secret tip inside" in cleaned


@pytest.mark.asyncio
async def test_translate_en_to_ru_preserves_placeholders():
    english_text = "Use `skill_combo` with {{icon:fire}} for max DPS."
    translated = await translate_en_to_ru(english_text)
    
    assert "`skill_combo`" in translated
    assert "{{icon:fire}}" in translated


def test_discord_sync_api_unauthorized():
    client = TestClient(app)
    res = client.get("/api/admin/discord-sync/status")
    assert res.status_code in (401, 403)


@patch("services.discord_sync.service.discord_sync_service.get_all_channels", new_callable=AsyncMock)
def test_discord_sync_api_admin(mock_get_channels):
    mock_get_channels.return_value = []
    admin_user = {
        "id": 999,
        "first_name": "Admin",
        "username": "admin",
        "is_admin": True,
    }
    app.dependency_overrides[require_admin] = lambda: admin_user
    client = TestClient(app)

    try:
        # Check status
        res = client.get("/api/admin/discord-sync/status")
        assert res.status_code == 200
        data = res.json()
        assert "running" in data
        assert "channels_count" in data

        # Add channel rule validation failure for invalid channel ID
        invalid_res = client.post(
            "/api/admin/discord-sync/channels",
            json={"channel_id": "abc_invalid", "category_key": "skills"},
        )
        assert invalid_res.status_code == 422
    finally:
        app.dependency_overrides.clear()
