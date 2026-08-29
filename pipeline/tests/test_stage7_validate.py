import pytest
from pipeline.stage7_validate import _validate_single_guide

def test_validate_valid_guide():
    valid_guide = {
        "title_ru": "Гайд по боссам",
        "raw_title": "Boss Guide",
        "text_ru": "Это подробный русский перевод руководства по убийству боссов.",
        "raw_text": "This is a detailed guide on killing bosses.",
        "photos": ["p1.png"],
        "raw_photos": ["p1.png"],
        "videos": [],
        "raw_videos": [],
    }
    is_valid, errors = _validate_single_guide(valid_guide)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_empty_title():
    guide = {
        "title_ru": "",
        "raw_title": "Boss Guide",
        "text_ru": "Some text",
        "raw_text": "Some text",
    }
    is_valid, errors = _validate_single_guide(guide)
    assert is_valid is False
    assert any("Пустой заголовок" in e for e in errors)

def test_validate_lost_photos():
    guide = {
        "title_ru": "Гайд",
        "raw_title": "Guide",
        "text_ru": "Текст",
        "raw_text": "Text",
        "photos": ["p1.png"],
        "raw_photos": ["p1.png", "p2.png"],
    }
    is_valid, errors = _validate_single_guide(guide)
    assert is_valid is False
    assert any("Потеряны фото" in e for e in errors)

def test_validate_masking_placeholders():
    guide = {
        "title_ru": "Гайд",
        "raw_title": "Guide",
        "text_ru": "Текст с артефактом XQB123BQX внутри",
        "raw_text": "Text with artifact",
    }
    is_valid, errors = _validate_single_guide(guide)
    assert is_valid is False
    assert any("плейсхолдеры" in e for e in errors)
