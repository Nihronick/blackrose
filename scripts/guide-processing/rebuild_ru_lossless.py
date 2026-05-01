#!/usr/bin/env python3
"""Create a lossless RU baseline by mirroring guides/en to guides/ru exactly (line-by-line)."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
EN_ROOT = ROOT / "guides" / "en"
RU_ROOT = ROOT / "guides" / "ru"
OUT = ROOT / "output_media"


def main() -> None:
    if not EN_ROOT.exists():
        raise SystemExit("guides/en not found")

    OUT.mkdir(parents=True, exist_ok=True)

    backup = ROOT / "guides" / f"ru_backup_lossless_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if RU_ROOT.exists():
        shutil.copytree(RU_ROOT, backup)
        shutil.rmtree(RU_ROOT)

    copied = []
    for en_file in sorted(EN_ROOT.rglob("*.md")):
        rel = en_file.relative_to(EN_ROOT)
        ru_file = RU_ROOT / rel
        ru_file.parent.mkdir(parents=True, exist_ok=True)
        ru_file.write_text(en_file.read_text(encoding="utf-8"), encoding="utf-8")
        copied.append(str(rel).replace("\\", "/"))

    report = {
        "action": "REBUILD_RU_LOSSLESS_FROM_EN",
        "backup": str(backup.relative_to(ROOT)).replace("\\", "/") if backup.exists() else None,
        "copied_files": len(copied),
        "sample": copied[:25],
    }
    (OUT / "rebuild_ru_lossless_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("RU lossless rebuild complete")
    print(f"Copied files: {len(copied)}")
    print(f"Backup: {report['backup']}")
    print("Report: output_media/rebuild_ru_lossless_report.json")


if __name__ == "__main__":
    main()
