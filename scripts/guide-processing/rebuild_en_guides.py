#!/usr/bin/env python3
"""Rebuild guides/en from slayerpedia (authoritative source)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SLAYERPEDIA_DIR = ROOT / "slayerpedia"
GUIDES_EN_DIR = ROOT / "guides" / "en"
OUTPUT_DIR = ROOT / "output_media"


def to_md_filename(txt_name: str) -> str:
    # Keep current project convention: spaces -> underscores, extension .md
    return txt_name.replace(" ", "_") + ".md"


def normalize_text(text: str) -> str:
    # Keep original content; only normalize line endings and ensure trailing newline.
    lines = text.replace("\r\n", "\n").replace("\r", "\n")
    return lines.rstrip() + "\n"


def rebuild_en() -> dict:
    if not SLAYERPEDIA_DIR.exists():
        raise SystemExit("slayerpedia directory not found")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Backup existing guides/en before rebuild.
    backup_root = ROOT / "guides" / f"en_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if GUIDES_EN_DIR.exists():
        shutil.copytree(GUIDES_EN_DIR, backup_root)
        shutil.rmtree(GUIDES_EN_DIR)
    GUIDES_EN_DIR.mkdir(parents=True, exist_ok=True)

    created_files = []
    category_stats = {}

    for category_dir in sorted(SLAYERPEDIA_DIR.iterdir()):
        if not category_dir.is_dir():
            continue

        txt_files = sorted(category_dir.glob("*.txt"))
        if not txt_files:
            continue

        target_category_dir = GUIDES_EN_DIR / category_dir.name
        target_category_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for txt_file in txt_files:
            content = txt_file.read_text(encoding="utf-8")
            md_name = to_md_filename(txt_file.stem)
            md_path = target_category_dir / md_name
            md_path.write_text(normalize_text(content), encoding="utf-8")
            created_files.append(str(md_path.relative_to(ROOT)).replace("\\", "/"))
            count += 1

        category_stats[category_dir.name] = count

    report = {
        "action": "REBUILD_EN_FROM_SLAYERPEDIA",
        "source": "slayerpedia",
        "target": "guides/en",
        "backup": str(backup_root.relative_to(ROOT)).replace("\\", "/") if backup_root.exists() else None,
        "categories": len(category_stats),
        "files_total": len(created_files),
        "by_category": category_stats,
        "sample_files": created_files[:25],
    }

    (OUTPUT_DIR / "rebuild_en_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return report


def verify_en_matches_slayerpedia() -> dict:
    source = {}
    target = {}

    for category_dir in sorted(SLAYERPEDIA_DIR.iterdir()):
        if category_dir.is_dir():
            names = sorted(f.stem for f in category_dir.glob("*.txt"))
            if names:
                source[category_dir.name] = names

    for category_dir in sorted(GUIDES_EN_DIR.iterdir()):
        if category_dir.is_dir():
            names = sorted(f.stem.replace("_", " ") for f in category_dir.glob("*.md"))
            if names:
                target[category_dir.name] = names

    missing = []
    extra = []

    all_categories = sorted(set(source.keys()) | set(target.keys()))
    for cat in all_categories:
        s = set(source.get(cat, []))
        t = set(target.get(cat, []))
        for name in sorted(s - t):
            missing.append(f"{cat}/{name}")
        for name in sorted(t - s):
            extra.append(f"{cat}/{name}")

    result = {
        "source_total": sum(len(v) for v in source.values()),
        "target_total": sum(len(v) for v in target.values()),
        "categories_source": len(source),
        "categories_target": len(target),
        "missing": missing,
        "extra": extra,
        "is_exact_match": len(missing) == 0 and len(extra) == 0,
    }

    (OUTPUT_DIR / "rebuild_en_verify.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


def main() -> None:
    report = rebuild_en()
    verify = verify_en_matches_slayerpedia()

    print("EN rebuild complete")
    print(f"Files created: {report['files_total']}")
    print(f"Categories: {report['categories']}")
    print(f"Exact match with slayerpedia: {verify['is_exact_match']}")
    print(f"Missing: {len(verify['missing'])}, Extra: {len(verify['extra'])}")
    print("Report: output_media/rebuild_en_report.json")
    print("Verify: output_media/rebuild_en_verify.json")


if __name__ == "__main__":
    main()
