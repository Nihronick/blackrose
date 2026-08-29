import pytest
from pipeline.glossary import CANONICAL_TITLES, AI_TRANSLATE_PROMPT, TITLE_TRANSLATE_PROMPT

def test_canonical_titles_not_empty():
    assert len(CANONICAL_TITLES) > 10
    assert CANONICAL_TITLES["beginner guide"] == "Гайд для начинающих"
    assert CANONICAL_TITLES["character"] == "Персонаж"

def test_canonical_titles_structure():
    for en, ru in CANONICAL_TITLES.items():
        assert isinstance(en, str) and len(en) > 0
        assert isinstance(ru, str) and len(ru) > 0

def test_ai_translate_prompt_contains_rules():
    assert "Slayer Legend" in AI_TRANSLATE_PROMPT
    assert "КРИТИЧЕСКИЕ ПРАВИЛА" in AI_TRANSLATE_PROMPT
    assert "TITLE_TRANSLATE_PROMPT" in str(TITLE_TRANSLATE_PROMPT) or len(TITLE_TRANSLATE_PROMPT) > 10
