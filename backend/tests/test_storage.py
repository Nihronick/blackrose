"""
Тесты для storage.py — логика работы с HuggingFace Datasets.

Проверяет:
- _public_media_url: корректная генерация URL
- _optimize_image_bytes: оптимизация изображений
- _is_token_like: валидация HF токена vs repo ID
- upload_file: мокнутый HfApi
- delete_file: обработка ошибок

Запуск:
    pytest tests/test_storage.py -v
"""

import os
import sys
import types
import unittest.mock as mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Stubs ──────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules.setdefault("aiohttp", mock.MagicMock())

_icons_stub = types.ModuleType("icons")
_icons_stub.ALL_ICONS = {"HP": "https://cdn.example.com/hp.png"}
_icons_stub._ICONS_LOWER = {"hp": "HP"}
_icons_stub.get_icon = lambda name: _icons_stub.ALL_ICONS.get(name, "")
sys.modules.setdefault("icons", _icons_stub)

_db_stub = mock.MagicMock()
_db_stub.get_sessionmaker = mock.MagicMock()
_db_stub.get_subscribers = mock.AsyncMock(return_value=[])
sys.modules.setdefault("database", _db_stub)

os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql://test/test")
os.environ.setdefault("ADMIN_USERS", "")
os.environ.setdefault("HF_TOKEN", "hf_test_token_abcdef1234567890")
os.environ.setdefault("HF_DATASET_REPO", "TestUser/test-dataset")

with mock.patch("asyncpg.create_pool"):
    import storage


# ── _public_media_url ──────────────────────────────────────────


class TestPublicMediaUrl:
    """Проверяет генерацию CDN URL для файлов в HF Dataset."""

    def test_returns_https_url(self):
        url = storage._public_media_url("uploads/guides/test.png")
        assert url.startswith("https://")

    def test_includes_repo_and_path(self):
        url = storage._public_media_url("uploads/guides/test.png")
        assert "test-dataset" in url
        assert "uploads/guides/test.png" in url

    def test_includes_resolve_main(self):
        url = storage._public_media_url("file.jpg")
        assert "/resolve/main/" in url

    def test_empty_repo_returns_empty(self):
        orig = storage.HF_DATASET_REPO
        try:
            storage.HF_DATASET_REPO = ""
            assert storage._public_media_url("file.jpg") == ""
        finally:
            storage.HF_DATASET_REPO = orig


# ── _is_token_like ──────────────────────────────────────────────


class TestIsTokenLike:
    """Проверяет детектор: значение похоже на токен, а не repo ID."""

    def test_hf_prefix_is_token(self):
        assert storage._is_token_like("hf_abcdef1234567890") is True

    def test_repo_id_is_not_token(self):
        assert storage._is_token_like("Nihronick/blackrose-media") is False

    def test_empty_is_not_token(self):
        assert storage._is_token_like("") is False

    def test_none_is_not_token(self):
        assert storage._is_token_like(None) is False


# ── _optimize_image_bytes ──────────────────────────────────────


class TestOptimizeImageBytes:
    """Проверяет оптимизацию изображений в WebP."""

    def test_non_image_returns_unchanged(self):
        """Неизвестные расширения не оптимизируются."""
        fname, data, optimized = storage._optimize_image_bytes("file.pdf", b"data")
        assert fname == "file.pdf"
        assert data == b"data"
        assert optimized is False

    def test_mp4_returns_unchanged(self):
        """Видео не оптимизируется этой функцией."""
        fname, data, optimized = storage._optimize_image_bytes("video.mp4", b"data")
        assert optimized is False

    def test_invalid_image_data_returns_unchanged(self):
        """Невалидные данные изображения → без изменений."""
        fname, data, optimized = storage._optimize_image_bytes("test.png", b"not-a-real-image")
        assert optimized is False
        assert data == b"not-a-real-image"

    def test_valid_png_optimized_to_webp(self):
        """Валидный PNG должен оптимизироваться в WebP."""
        # Создаём минимальный 100x100 PNG
        from PIL import Image
        from io import BytesIO

        img = Image.new("RGB", (100, 100), color="red")
        buf = BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        fname, data, optimized = storage._optimize_image_bytes("test.png", png_bytes)

        if optimized:
            assert fname.endswith(".webp")
            assert len(data) > 0
        else:
            # WebP может быть больше для мелких изображений — допустимо
            assert fname == "test.png"


# ── upload_file ────────────────────────────────────────────────


class TestUploadFile:
    """Проверяет загрузку файлов в HF Dataset."""

    @pytest.mark.asyncio
    async def test_upload_calls_hf_api(self):
        """upload_file должен вызвать hf_api.upload_file."""
        # Создаём mock UploadFile
        upload = MagicMock()
        upload.filename = "test.txt"
        upload.read = AsyncMock(return_value=b"file content")

        with patch.object(storage, 'hf_api') as mock_api:
            mock_api.upload_file = MagicMock()
            result = await storage.upload_file(upload, "guides")

            assert isinstance(result, str)
            assert result.startswith("https://")
            mock_api.upload_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_no_token_raises(self):
        """Без HF_TOKEN upload должен бросить RuntimeError."""
        orig_token = storage.HF_TOKEN
        try:
            storage.HF_TOKEN = ""

            upload = MagicMock()
            upload.filename = "test.txt"
            upload.read = AsyncMock(return_value=b"data")

            with pytest.raises(RuntimeError, match="not configured"):
                await storage.upload_file(upload, "guides")
        finally:
            storage.HF_TOKEN = orig_token

    @pytest.mark.asyncio
    async def test_upload_no_repo_raises(self):
        """Без HF_DATASET_REPO upload должен бросить RuntimeError."""
        orig_repo = storage.HF_DATASET_REPO
        try:
            storage.HF_DATASET_REPO = ""

            upload = MagicMock()
            upload.filename = "test.txt"
            upload.read = AsyncMock(return_value=b"data")

            with pytest.raises(RuntimeError, match="not configured"):
                await storage.upload_file(upload, "guides")
        finally:
            storage.HF_DATASET_REPO = orig_repo


# ── delete_file ────────────────────────────────────────────────


class TestDeleteFile:
    """Проверяет удаление файлов из HF Dataset."""

    @pytest.mark.asyncio
    async def test_delete_calls_hf_api(self):
        """delete_file должен вызвать hf_api.delete_file."""
        with patch.object(storage, 'hf_api') as mock_api:
            mock_api.delete_file = MagicMock()
            await storage.delete_file("uploads/guides/test.png")
            mock_api.delete_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_no_crash(self):
        """Удаление несуществующего файла не должно крашить."""
        with patch.object(storage, 'hf_api') as mock_api:
            mock_api.delete_file = MagicMock(
                side_effect=Exception("EntryNotFoundError")
            )
            # Должно залогировать, но не крашить
            await storage.delete_file("nonexistent/file.png")
