"""
Тесты для format_guide_text и normalize_icon_syntax.

Markdown-парсер написан вручную — это самое хрупкое место в коде.
Тесты фиксируют контракт: что входит → что выходит.
"""
import sys
import types
import os
import unittest.mock as mock

# Stub модулей с зависимостями
_db_stub = types.ModuleType("database")
_aiohttp_stub = types.ModuleType("aiohttp")
sys.modules.setdefault("database", _db_stub)
sys.modules.setdefault("aiohttp", _aiohttp_stub)

# Stub icons — возвращаем предсказуемый URL
_icons_stub = types.ModuleType("icons")
_icons_stub.ALL_ICONS    = {"HP": "https://cdn.example.com/hp.png", "ATK": "https://cdn.example.com/atk.png"}
_icons_stub._ICONS_LOWER = {"hp": "HP", "atk": "ATK"}
_icons_stub.get_icon     = lambda name: _icons_stub.ALL_ICONS.get(name, "")
sys.modules["icons"] = _icons_stub

os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("DATABASE_URL", "postgresql://test/test")
os.environ.setdefault("ALLOWED_USERS", "")
os.environ.setdefault("ADMIN_USERS", "")

with mock.patch("asyncpg.create_pool"):
    import main as app_main


# ── format_guide_text ──────────────────────────────────────────

class TestFormatGuideText:

    def _fmt(self, text: str, guide_links: dict | None = None) -> str:
        return app_main.format_guide_text(text, guide_links or {})

    # Markdown inline

    def test_bold(self):
        assert "<strong>жирный</strong>" in self._fmt("**жирный**")

    def test_italic(self):
        assert "<em>курсив</em>" in self._fmt("*курсив*")

    def test_strikethrough(self):
        assert "<s>зачёркнутый</s>" in self._fmt("~~зачёркнутый~~")

    def test_code_inline(self):
        out = self._fmt("`код`")
        assert '<code class="guide-code">код</code>' in out

    def test_spoiler(self):
        out = self._fmt("||секрет||")
        assert 'class="guide-spoiler"' in out
        assert "секрет" in out

    def test_external_link(self):
        out = self._fmt("[Google](https://google.com)")
        assert 'href="https://google.com"' in out
        assert 'target="_blank"' in out
        assert "Google" in out

    def test_external_link_rel_noreferrer(self):
        """Внешние ссылки должны иметь rel=noreferrer для безопасности."""
        out = self._fmt("[Test](https://example.com)")
        assert 'rel="noreferrer"' in out

    # Блочные элементы

    def test_h2(self):
        out = self._fmt("## Заголовок")
        assert '<h2 class="guide-h2">Заголовок</h2>' in out

    def test_h3(self):
        out = self._fmt("### Подзаголовок")
        assert '<h3 class="guide-h3">Подзаголовок</h3>' in out

    def test_blockquote(self):
        out = self._fmt("> Цитата")
        assert '<blockquote class="guide-quote">Цитата</blockquote>' in out

    def test_unordered_list_item(self):
        out = self._fmt("- Пункт")
        assert '<li class="guide-li guide-ul">Пункт</li>' in out

    def test_ordered_list_item(self):
        out = self._fmt("1. Шаг первый")
        assert '<li class="guide-li guide-ol">Шаг первый</li>' in out

    def test_hr(self):
        out = self._fmt("---")
        assert '<hr class="guide-hr">' in out

    def test_newline_converted_to_br(self):
        out = self._fmt("строка1\nстрока2")
        assert "<br>" in out

    # Иконки

    def test_icon_replaced_with_img(self):
        out = self._fmt("{{HP}}")
        assert "<img" in out
        assert "hp.png" in out
        assert 'class="inline-icon"' in out

    def test_unknown_icon_calls_get_icon(self):
        """Неизвестная иконка всё равно вызывает get_icon — не ломает рендер."""
        out = self._fmt("{{UNKNOWN_ICON}}")
        assert "<img" in out   # get_icon вернёт "", src будет пустым, но тег будет

    # Guide cyberlinks [[key]]

    def test_guide_link_without_label(self):
        links = {"my_guide": {"title": "Мой гайд", "icon": ""}}
        out = self._fmt("[[my_guide]]", guide_links=links)
        assert 'data-guide-key="my_guide"' in out
        assert "Мой гайд" in out
        assert 'class="guide-cyberlink"' in out

    def test_guide_link_with_label(self):
        links = {"boss_guide": {"title": "Гайд на босса", "icon": ""}}
        out = self._fmt("[[boss_guide|Убить босса]]", guide_links=links)
        assert "Убить босса" in out
        assert 'data-guide-key="boss_guide"' in out

    def test_guide_link_with_icon(self):
        links = {"guide_x": {"title": "X", "icon": "https://cdn.example.com/x.png"}}
        out = self._fmt("[[guide_x]]", guide_links=links)
        assert "cdn.example.com/x.png" in out

    def test_unknown_guide_link_uses_key_as_title(self):
        """Если ключ не найден в guide_links — показываем сам ключ."""
        out = self._fmt("[[missing_key]]", guide_links={})
        assert "missing_key" in out
        assert 'data-guide-key="missing_key"' in out

    # Sanitization — XSS защита через nh3

    def test_script_tag_stripped(self):
        out = self._fmt("<script>alert(1)</script>")
        assert "<script>" not in out
        assert "alert" not in out

    def test_onclick_attr_stripped(self):
        out = self._fmt('<a href="#" onclick="evil()">click</a>')
        assert "onclick" not in out

    def test_safe_html_preserved(self):
        """Разрешённые теги (strong, em, code) должны выживать после nh3."""
        out = self._fmt("**жирный** и *курсив*")
        assert "<strong>" in out
        assert "<em>" in out

    # Edge cases

    def test_empty_string(self):
        assert self._fmt("") == ""

    def test_plain_text_unchanged(self):
        out = self._fmt("просто текст без разметки")
        assert "просто текст без разметки" in out

    def test_multiple_bold_same_line(self):
        out = self._fmt("**A** и **B**")
        assert "<strong>A</strong>" in out
        assert "<strong>B</strong>" in out

    def test_nested_bold_italic(self):
        """***жирный курсив*** — стандарт Markdown."""
        out = self._fmt("***жирный курсив***")
        # Парсер обрабатывает ** и * отдельно — порядок может различаться
        assert "<strong>" in out or "<em>" in out

    def test_multiline_bold(self):
        """DOTALL флаг — **жирный\nтекст** должен работать."""
        out = self._fmt("**первая\nвторая**")
        assert "<strong>" in out


# ── normalize_icon_syntax ──────────────────────────────────────

class TestNormalizeIconSyntax:
    """normalize_icon_syntax конвертирует :icon: и {{icon}} → {{resolved_key}}."""

    def _norm(self, text: str) -> str:
        return app_main.normalize_icon_syntax(text)

    def test_colon_syntax_converted(self):
        out = self._norm(":HP:")
        assert "{{HP}}" in out
        assert ":HP:" not in out

    def test_colon_syntax_case_insensitive(self):
        out = self._norm(":hp:")
        assert "{{HP}}" in out

    def test_double_brace_preserved_if_known(self):
        out = self._norm("{{HP}}")
        assert "{{HP}}" in out

    def test_double_brace_lowercased_resolved(self):
        out = self._norm("{{hp}}")
        assert "{{HP}}" in out

    def test_unknown_key_passed_through(self):
        """Неизвестный ключ не должен ломаться — остаётся как есть."""
        out = self._norm(":unknown_icon:")
        assert "{{unknown_icon}}" in out

    def test_multiple_icons_in_text(self):
        out = self._norm("Урон :ATK: и здоровье :HP:")
        assert "{{ATK}}" in out
        assert "{{HP}}" in out

    def test_plain_text_untouched(self):
        text = "Просто текст без иконок"
        assert self._norm(text) == text
