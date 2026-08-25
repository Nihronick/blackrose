"""
Этап 7: Контроль качества (Quality Gate) перед выкаткой на продакшен.
"""
import json
import re
from typing import Dict, List, Tuple

from .config import VALIDATION_REPORT_FILE


def _validate_single_guide(guide: Dict) -> Tuple[bool, List[str]]:
    """Проверка одного гайда по критериям качества."""
    errors = []

    title = guide.get("title_ru", "").strip()
    raw_title = guide.get("raw_title", "").strip()
    text = guide.get("text_ru", "").strip()
    raw_text = guide.get("raw_text", "").strip()
    photos = guide.get("photos", [])
    raw_photos = guide.get("raw_photos", [])
    videos = guide.get("videos", [])
    raw_videos = guide.get("raw_videos", [])

    # 1. Заголовок
    if not title:
        errors.append("Пустой заголовок")
    elif len(title) > 120:
        errors.append(f"Заголовок слишком длинный ({len(title)} символов)")

    # 2. Полнота контента
    if not text and not photos and not videos:
        errors.append("Полностью пустая статья (нет ни текста, ни медиа)")

    # 3. Сохранность фото и видео (0 потерь)
    if len(photos) != len(raw_photos):
        errors.append(f"Потеряны фото: исходных {len(raw_photos)}, переведено {len(photos)}")
    if len(videos) != len(raw_videos):
        errors.append(f"Потеряны видео: исходных {len(raw_videos)}, переведено {len(videos)}")

    # 4. Пропорция длины перевода к оригиналу (защита от обрыва)
    if raw_text and len(raw_text) > 100:
        ratio = len(text) / len(raw_text)
        if ratio < 0.35:
            errors.append(f"Подозрительно короткий перевод (коэффициент {ratio:.2f} от оригинала)")
        elif ratio > 3.0:
            errors.append(f"Подозрительно раздутый перевод (коэффициент {ratio:.2f} от оригинала)")

    # 5. Проверка на артефакты маскирования
    if re.search(r'XQB\d+BQX', text):
        errors.append("В тексте остались нераскрытые служебные плейсхолдеры XQB...BQX")

    # 6. Проверка на битые сырые теги Discord
    if re.search(r'<@!?\d+>', text):
        errors.append("В тексте содержатся сырые упоминания пользователей Discord <@...>")

    return len(errors) == 0, errors


def run(guides: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Этап 7: тестирование всех гайдов через Quality Gate."""
    print("\n" + "=" * 60)
    print("  🛡️ Этап 7: Quality Gate и проверка целостности данных")
    print("=" * 60)

    passed = []
    failed = []
    report_details = []

    for g in guides:
        is_ok, errors = _validate_single_guide(g)
        if is_ok:
            passed.append(g)
        else:
            failed.append(g)
            report_details.append({
                "guide_key": g.get("guide_key"),
                "title": g.get("title_ru") or g.get("raw_title"),
                "errors": errors
            })

    report = {
        "total_guides": len(guides),
        "passed_count": len(passed),
        "failed_count": len(failed),
        "pass_rate": f"{(len(passed) / max(len(guides), 1)) * 100:.1f}%",
        "failed_guides": report_details
    }

    try:
        with open(VALIDATION_REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [WARN] Не удалось сохранить validation_report.json: {e}")

    print(f"  📊 Результаты проверки:")
    print(f"     ✅ Прошли проверку (Ready to Deploy): {len(passed)}/{len(guides)}")
    if failed:
        print(f"     ⚠️ Отклонено Quality Gate:            {len(failed)}/{len(guides)}")
        for f_item in report_details[:5]:
            print(f"        ❌ {f_item['title']}: {', '.join(f_item['errors'])}")
        if len(report_details) > 5:
            print(f"        ...и еще {len(report_details) - 5} отклоненных (см. {VALIDATION_REPORT_FILE.name})")

    return passed, failed
