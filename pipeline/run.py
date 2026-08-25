"""
Главный оркестратор ETL-пайплайна BlackRose (Этапы 1 → 8).
"""
import sys
import time
import argparse
from pathlib import Path

from .config import RAW_DIR, STRUCTURED_DIR, TRANSLATED_DIR
from . import stage1_extract
from . import stage2_store_raw
from . import stage3_structure
from . import stage4_parse
from . import stage5_media
from . import stage6_translate
from . import stage7_validate
from . import stage8_deploy


def main():
    parser = argparse.ArgumentParser(description="BlackRose 8-Stage Knowledge Pipeline (Discord -> Web)")
    parser.add_argument("--from-stage", type=int, default=1, help="Начать с этапа N (1..8), используя сохраненные данные")
    parser.add_argument("--only-stage", type=int, default=None, help="Выполнить ТОЛЬКО этап N и завершить работу")
    parser.add_argument("--skip-translate", action="store_true", help="Пропустить этап 6 (ИИ-перевод)")
    parser.add_argument("--skip-validate", action="store_true", help="Пропустить этап 7 (Quality Gate)")
    parser.add_argument("--dry-run", action="store_true", help="Выполнить обработку без деплоя на прод")
    args = parser.parse_args()

    start_time = time.time()

    print("=" * 70)
    print("  🌹 BLACKROSE 8-STAGE ETL KNOWLEDGE PIPELINE")
    print("=" * 70)
    print(f"  Режим запуска: from-stage={args.from_stage}, only-stage={args.only_stage}, dry-run={args.dry_run}")

    channels_data = []
    guides = []
    passed_guides = []

    # ── ЭТАП 1: EXTRACT ──
    if args.only_stage == 1 or (args.from_stage <= 1 and args.only_stage is None):
        channels_data = stage1_extract.run()
        if args.only_stage == 1:
            stage2_store_raw.save(channels_data)
            return

    # ── ЭТАП 2: STORE RAW ──
    if args.only_stage == 2 or (args.from_stage <= 2 and args.only_stage is None):
        if not channels_data:
            channels_data = stage2_store_raw.load()
        else:
            channels_data = stage2_store_raw.run(channels_data)
        if args.only_stage == 2:
            return
    elif args.from_stage > 2:
        channels_data = stage2_store_raw.load()

    # ── ЭТАП 3: STRUCTURE ──
    if args.only_stage == 3 or (args.from_stage <= 3 and args.only_stage is None):
        if not channels_data:
            channels_data = stage2_store_raw.load()
        guides = stage3_structure.run(channels_data)
        if args.only_stage == 3:
            return
    elif args.from_stage > 3:
        import json
        structured_file = STRUCTURED_DIR / "guides.json"
        if structured_file.exists():
            with open(structured_file, "r", encoding="utf-8") as f:
                guides = json.load(f)

    # ── ЭТАП 4: PARSE ──
    if args.only_stage == 4 or (args.from_stage <= 4 and args.only_stage is None):
        if not guides:
            import json
            with open(STRUCTURED_DIR / "guides.json", "r", encoding="utf-8") as f:
                guides = json.load(f)
        guides = stage4_parse.run(guides)
        if args.only_stage == 4:
            return
    elif args.from_stage > 4:
        import json
        parsed_file = STRUCTURED_DIR / "parsed_guides.json"
        if parsed_file.exists():
            with open(parsed_file, "r", encoding="utf-8") as f:
                guides = json.load(f)

    # ── ЭТАП 5: MEDIA ──
    if args.only_stage == 5 or (args.from_stage <= 5 and args.only_stage is None):
        if not guides:
            import json
            with open(STRUCTURED_DIR / "parsed_guides.json", "r", encoding="utf-8") as f:
                guides = json.load(f)
        guides = stage5_media.run(guides)
        if args.only_stage == 5:
            return

    # ── ЭТАП 6: TRANSLATE ──
    if args.only_stage == 6 or (args.from_stage <= 6 and args.only_stage is None):
        if not guides:
            import json
            with open(STRUCTURED_DIR / "parsed_guides.json", "r", encoding="utf-8") as f:
                guides = json.load(f)
        if not args.skip_translate:
            guides = stage6_translate.run(guides)
        else:
            print("\n  [!] Пропуск этапа 6 (--skip-translate)")
            for g in guides:
                g["title_ru"] = g.get("raw_title", "")
                g["text_ru"] = g.get("raw_text", "")
                g["category_title_ru"] = g.get("category_name", "")
                g["photos"] = g.get("raw_photos", [])
                g["videos"] = g.get("raw_videos", [])
        if args.only_stage == 6:
            return
    elif args.from_stage > 6:
        import json
        translated_file = TRANSLATED_DIR / "translated_guides.json"
        if translated_file.exists():
            with open(translated_file, "r", encoding="utf-8") as f:
                guides = json.load(f)

    # ── ЭТАП 7: VALIDATE ──
    if args.only_stage == 7 or (args.from_stage <= 7 and args.only_stage is None):
        if not guides:
            import json
            with open(TRANSLATED_DIR / "translated_guides.json", "r", encoding="utf-8") as f:
                guides = json.load(f)
        if not args.skip_validate:
            passed_guides, failed_guides = stage7_validate.run(guides)
        else:
            print("\n  [!] Пропуск этапа 7 (--skip-validate)")
            passed_guides = guides
        if args.only_stage == 7:
            return
    elif args.from_stage > 7:
        passed_guides = guides

    # ── ЭТАП 8: DEPLOY ──
    if args.only_stage == 8 or (args.from_stage <= 8 and args.only_stage is None):
        if not passed_guides:
            import json
            with open(TRANSLATED_DIR / "translated_guides.json", "r", encoding="utf-8") as f:
                passed_guides = json.load(f)
        if not args.dry_run:
            stage8_deploy.run(passed_guides, channels_data)
        else:
            print("\n  [!] Режим --dry-run: деплой на боевой сервер пропущен.")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  🏁 ВСЕ ЭТАПЫ ПАЙПЛАЙНА ЗАВЕРШЕНЫ ЗА {elapsed:.1f} сек!")
    print("=" * 70)


if __name__ == "__main__":
    main()
