#!/usr/bin/env python3
"""Scan guides for Discord emoji IDs and download missing emoji assets.

The script scans both guides/en and guides/ru for Discord custom emoji tags
like <:name:123456789012345678> or direct emoji URLs, then downloads any
missing files into frontend/public/assets/images/icons/discord_migrated.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import requests


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GUIDE_DIRS = [ROOT / "guides" / "en", ROOT / "guides" / "ru"]
ICONS_DIR = ROOT / "frontend" / "public" / "assets" / "images" / "icons" / "discord_migrated"

DISCORD_TAG_RE = re.compile(r"<a?:([A-Za-z0-9_]+):(\d{17,19})>")
DISCORD_URL_RE = re.compile(r"https?://(?:cdn\.)?discordapp\.com/emojis/(\d{17,19})\.(\w+)", re.IGNORECASE)


def iter_markdown_files(guide_dirs: Iterable[Path]) -> Iterable[Path]:
    for guide_dir in guide_dirs:
        if guide_dir.exists():
            yield from guide_dir.rglob("*.md")


def scan_emoji_references(guide_dirs: Iterable[Path]) -> dict[str, dict[str, object]]:
    references: dict[str, dict[str, object]] = {}

    for md_file in iter_markdown_files(guide_dirs):
        text = md_file.read_text(encoding="utf-8", errors="ignore")

        for name, emoji_id in DISCORD_TAG_RE.findall(text):
            info = references.setdefault(
                emoji_id,
                {"files": set(), "names": set(), "ext": None},
            )
            info["files"].add(md_file)
            info["names"].add(name)

        for emoji_id, ext in DISCORD_URL_RE.findall(text):
            info = references.setdefault(
                emoji_id,
                {"files": set(), "names": set(), "ext": None},
            )
            info["files"].add(md_file)
            info["ext"] = ext.lower()

    return references


def candidate_urls(emoji_id: str, preferred_ext: str | None = None) -> list[str]:
    variants: list[tuple[str, str]] = []

    if preferred_ext:
        variants.append((preferred_ext, f"https://cdn.discordapp.com/emojis/{emoji_id}.{preferred_ext}?size=44"))

    variants.extend(
        [
            ("webp", f"https://cdn.discordapp.com/emojis/{emoji_id}.webp?size=44"),
            ("webp", f"https://cdn.discordapp.com/emojis/{emoji_id}.webp?size=48&quality=lossless"),
            ("gif", f"https://cdn.discordapp.com/emojis/{emoji_id}.gif?size=44&animated=true"),
            ("gif", f"https://cdn.discordapp.com/emojis/{emoji_id}.gif?size=48&animated=true&quality=lossless"),
            ("webp", f"https://media.discordapp.net/emojis/{emoji_id}.webp?size=44"),
        ]
    )

    seen: set[str] = set()
    ordered: list[str] = []
    for _, url in variants:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def download_emoji(emoji_id: str, preferred_ext: str | None = None, force: bool = False) -> tuple[bool, str | None]:
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    existing = list(ICONS_DIR.glob(f"{emoji_id}.*"))
    if existing and not force:
        return True, existing[0].name

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://discord.com/",
    }

    last_error: str | None = None
    for url in candidate_urls(emoji_id, preferred_ext):
        try:
            response = session.get(url, headers=headers, timeout=60)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if ".gif" in url or "gif" in content_type:
                suffix = ".gif"
            else:
                suffix = ".webp"

            target = ICONS_DIR / f"{emoji_id}{suffix}"
            target.write_bytes(response.content)
            return True, target.name
        except Exception as exc:
            last_error = str(exc)
            continue

    return False, last_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Discord emoji assets used in guides")
    parser.add_argument("--dry-run", action="store_true", help="List missing emoji files without downloading")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they already exist")
    parser.add_argument(
        "--dirs",
        nargs="*",
        default=[str(p) for p in DEFAULT_GUIDE_DIRS],
        help="Guide directories to scan (default: guides/en guides/ru)",
    )
    args = parser.parse_args()

    guide_dirs = [Path(p) for p in args.dirs]
    references = scan_emoji_references(guide_dirs)

    total = len(references)
    missing = []
    for emoji_id in sorted(references):
        target_exists = any(ICONS_DIR.glob(f"{emoji_id}.*"))
        if not target_exists or args.force:
            missing.append(emoji_id)

    print(f"emoji_ids={total}")
    print(f"missing_files={len(missing)}")

    if args.dry_run:
        for emoji_id in missing:
            files = sorted(str(p).replace('\\', '/') for p in references[emoji_id]["files"])
            print(f"MISSING {emoji_id} | used_in={len(files)} | first={files[0]}")
        return 0

    downloaded = 0
    skipped = 0
    failed = 0

    for emoji_id in missing:
        ext = references[emoji_id]["ext"]
        ok, result = download_emoji(emoji_id, preferred_ext=ext, force=args.force)
        if ok:
            downloaded += 1
            print(f"DOWNLOADED {emoji_id} -> {result}")
        else:
            failed += 1
            print(f"FAILED {emoji_id} -> {result}")

    for emoji_id in sorted(references):
        if emoji_id not in missing:
            skipped += 1

    print("\nSUMMARY")
    print(f"  downloaded: {downloaded}")
    print(f"  skipped: {skipped}")
    print(f"  failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())