import pytest
from unittest.mock import MagicMock, patch
from fastapi import UploadFile
from services.storage.hf_storage import HFStorageService

@pytest.fixture
def storage():
    return HFStorageService()

def test_get_public_url(storage):
    path = "uploads/guides/test.png"
    url = storage._get_public_url(path)
    assert "huggingface.co/datasets" in url
    assert "resolve/main" in url
    assert path in url

def test_optimize_image_non_image(storage):
    filename = "test.txt"
    content = b"not an image"
    opt_name, opt_content, optimized = storage._optimize_image(filename, content)
    assert opt_name == filename
    assert opt_content == content
    assert optimized is False

@pytest.mark.asyncio
async def test_upload_unconfigured(storage):
    with patch("core.config.settings.HF_TOKEN", ""):
        file = MagicMock(spec=UploadFile)
        with pytest.raises(RuntimeError, match="Media storage not configured"):
            await storage.upload(file)

@pytest.mark.asyncio
async def test_delete_invalid_url(storage):
    assert await storage.delete("https://google.com") is False

@pytest.mark.asyncio
async def test_ping_healthy(storage):
    with patch.object(storage.api, 'repo_info', return_value=True):
        res = await storage.ping()
        assert res["status"] == "healthy"
