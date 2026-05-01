"""
Тесты для database.py — чистая логика без реальной БД.

Проверяет:
- _normalize_db_url: корректное преобразование URL для asyncpg
- _strip_html / _strip_markdown: парсинг текста
- _guide_to_dict: корректное преобразование ORM → dict

Запуск:
    pytest tests/test_database_logic.py -v
"""

import os
import sys
import types
import unittest.mock as mock

import pytest

# ── Stubs ──────────────────────────────────────────────────────
# database.py imports db_models and sqlalchemy — we need to stub them
# minimally so that _normalize_db_url and helpers can be tested.

# Ensure backend/ is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stub aiohttp (imported by utils.py)
sys.modules.setdefault("aiohttp", mock.MagicMock())

# Stub icons module
_icons_stub = types.ModuleType("icons")
_icons_stub.ALL_ICONS = {"HP": "https://cdn.example.com/hp.png"}
_icons_stub._ICONS_LOWER = {"hp": "HP"}
_icons_stub.get_icon = lambda name: _icons_stub.ALL_ICONS.get(name, "")
sys.modules.setdefault("icons", _icons_stub)

# Set env before importing modules
os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql://test/test")
os.environ.setdefault("ADMIN_USERS", "")

from database import _normalize_db_url, _strip_html, _strip_markdown


# ── _normalize_db_url ──────────────────────────────────────────


class TestNormalizeDbUrl:
    """URL нормализация для asyncpg."""

    def test_postgres_to_asyncpg(self):
        url = "postgres://user:pass@host/db"
        result = _normalize_db_url(url)
        assert result.startswith("postgresql+asyncpg://")
        assert "user:pass@host/db" in result

    def test_postgresql_to_asyncpg(self):
        url = "postgresql://user:pass@host/db"
        result = _normalize_db_url(url)
        assert result.startswith("postgresql+asyncpg://")

    def test_psycopg2_to_asyncpg(self):
        url = "postgresql+psycopg2://user:pass@host/db"
        result = _normalize_db_url(url)
        assert "asyncpg" in result
        assert "psycopg2" not in result

    def test_already_asyncpg_unchanged(self):
        url = "postgresql+asyncpg://user:pass@host/db"
        result = _normalize_db_url(url)
        assert result == url

    def test_sslmode_converted_to_ssl(self):
        url = "postgresql://user:pass@host/db?sslmode=require"
        result = _normalize_db_url(url)
        assert "ssl=require" in result
        assert "sslmode=require" not in result

    def test_channel_binding_removed(self):
        url = "postgresql://user:pass@host/db?sslmode=require&channel_binding=prefer"
        result = _normalize_db_url(url)
        assert "channel_binding" not in result

    def test_empty_string(self):
        assert _normalize_db_url("") == ""

    def test_strips_quotes_and_whitespace(self):
        url = "  'postgresql://user:pass@host/db'  "
        result = _normalize_db_url(url)
        assert result.startswith("postgresql+asyncpg://")
        assert "'" not in result

    def test_neon_pooler_url(self):
        """Реальный URL от Neon с pooler."""
        url = "postgresql://user:pass@ep-cool-thing-123-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
        result = _normalize_db_url(url)
        assert result.startswith("postgresql+asyncpg://")
        assert "ssl=require" in result
        assert "neon.tech" in result

    def test_no_scheme_with_at_sign(self):
        """URL без схемы, но с @."""
        url = "user:pass@host/db"
        result = _normalize_db_url(url)
        assert result.startswith("postgresql+asyncpg://")


# ── _strip_html ────────────────────────────────────────────────


class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<strong>bold</strong>") == "bold"

    def test_preserves_text(self):
        assert _strip_html("plain text") == "plain text"

    def test_handles_none(self):
        assert _strip_html(None) == ""

    def test_handles_empty(self):
        assert _strip_html("") == ""

    def test_nested_tags(self):
        assert _strip_html("<div><p>text</p></div>") == "text"


# ── _strip_markdown ───────────────────────────────────────────


class TestStripMarkdown:
    def test_removes_bold(self):
        assert _strip_markdown("**bold**") == "bold"

    def test_removes_italic(self):
        assert _strip_markdown("*italic*") == "italic"

    def test_removes_icons(self):
        assert _strip_markdown("{{HP}} text") == "text"

    def test_resolves_guide_links(self):
        assert "my_guide" in _strip_markdown("[[my_guide]]")

    def test_guide_link_with_pipe(self):
        result = _strip_markdown("[[guide_key|Подпись]]")
        assert "guide_key" in result

    def test_plain_text_unchanged(self):
        assert _strip_markdown("plain text") == "plain text"

    def test_handles_none(self):
        assert _strip_markdown(None) == ""


# ── _guide_to_dict ─────────────────────────────────────────────


class TestGuideToDictContract:
    """
    Проверяет контракт _guide_to_dict — что возвращённый dict содержит
    все необходимые поля в правильном формате.
    """

    def test_required_fields(self):
        """Dict должен содержать все поля, которые фронтенд ожидает."""
        from database import _guide_to_dict

        # Создаём mock объект Guide
        guide = mock.MagicMock()
        guide.key = "test-key"
        guide.category_key = "cat1"
        guide.title = "Test Guide"
        guide.icon_url = "https://example.com/icon.png"
        guide.text = "Some **markdown** text"
        guide.photo = ["https://example.com/photo.jpg"]
        guide.video = []
        guide.document = []
        guide.sort_order = 0
        guide.views = 42
        guide.tags = []

        result = _guide_to_dict(guide)

        # Required fields
        assert result["key"] == "test-key"
        assert result["category_key"] == "cat1"
        assert result["title"] == "Test Guide"
        assert result["icon_url"] == "https://example.com/icon.png"
        assert result["views"] == 42
        assert result["sort_order"] == 0

        # Media arrays
        assert isinstance(result["photo"], list)
        assert isinstance(result["video"], list)
        assert isinstance(result["document"], list)

        # Booleans
        assert result["has_photo"] is True
        assert result["has_video"] is False
        assert result["has_document"] is False

        # Preview
        assert isinstance(result["preview"], str)
        assert len(result["preview"]) <= 200

        # Tags
        assert isinstance(result["tags"], list)

    def test_none_media_becomes_empty_list(self):
        """photo=None, video=None, document=None → пустые списки."""
        from database import _guide_to_dict

        guide = mock.MagicMock()
        guide.key = "k"
        guide.category_key = "c"
        guide.title = "T"
        guide.icon_url = None
        guide.text = ""
        guide.photo = None
        guide.video = None
        guide.document = None
        guide.sort_order = 0
        guide.views = None
        guide.tags = []

        result = _guide_to_dict(guide)

        assert result["photo"] == []
        assert result["video"] == []
        assert result["document"] == []
        assert result["views"] == 0

    def test_preview_strips_markdown(self):
        """Preview не должен содержать markdown-разметку."""
        from database import _guide_to_dict

        guide = mock.MagicMock()
        guide.key = "k"
        guide.category_key = "c"
        guide.title = "T"
        guide.icon_url = None
        guide.text = "**bold** and *italic* and {{HP}} icon"
        guide.photo = []
        guide.video = []
        guide.document = []
        guide.sort_order = 0
        guide.views = 0
        guide.tags = []

        result = _guide_to_dict(guide)

        assert "**" not in result["preview"]
        assert "*" not in result["preview"]
        assert "{{" not in result["preview"]

    def test_tags_from_relationship(self):
        """Теги должны извлекаться из relationship."""
        from database import _guide_to_dict

        guide = mock.MagicMock()
        guide.key = "k"
        guide.category_key = "c"
        guide.title = "T"
        guide.icon_url = None
        guide.text = ""
        guide.photo = []
        guide.video = []
        guide.document = []
        guide.sort_order = 0
        guide.views = 0

        tag1 = mock.MagicMock()
        tag1.tag = "pvp"
        tag2 = mock.MagicMock()
        tag2.tag = "guild"
        guide.tags = [tag1, tag2]

        result = _guide_to_dict(guide)

        assert result["tags"] == ["pvp", "guild"]

    def test_tags_lazy_load_failure_returns_empty(self):
        """Если tags relationship не загружен — возвращаем []."""
        from database import _guide_to_dict

        guide = mock.MagicMock()
        guide.key = "k"
        guide.category_key = "c"
        guide.title = "T"
        guide.icon_url = None
        guide.text = ""
        guide.photo = []
        guide.video = []
        guide.document = []
        guide.sort_order = 0
        guide.views = 0
        # Simulate lazy load failure
        type(guide).tags = mock.PropertyMock(side_effect=Exception("lazy load"))

        result = _guide_to_dict(guide)

        assert result["tags"] == []
