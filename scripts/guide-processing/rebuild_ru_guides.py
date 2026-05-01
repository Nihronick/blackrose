#!/usr/bin/env python3
"""
Rebuild guides/ru from guides/en with robust line-preserving translation.

Goals:
- Preserve all lines and markdown structure.
- Preserve URLs, Discord tags, emoji tokens, mentions, and no-translate terms.
- Avoid corrupted artifacts and escaped unicode garbage.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).parent
EN_ROOT = ROOT / "guides" / "en"
RU_ROOT = ROOT / "guides" / "ru"
REPORT_PATH = ROOT / "output_media" / "ru_rebuild_report.json"
GLOSSARY_PATH = ROOT / "output_media" / "glossary.json"

# Protect tokens that must never be translated.
URL_RE = re.compile(r"https?://[^\s)]+")
DISCORD_TAG_RE = re.compile(r"<:[^:>]+:\d+>|<a:[^:>]+:\d+>|<#\d+>|<@!?\d+>")
INLINE_CODE_RE = re.compile(r"`[^`]+`")


def google_translate(text: str, src: str = "en", dst: str = "ru", retries: int = 1) -> str:
    if not text.strip():
        return text

    query = urllib.parse.quote(text)
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={src}&tl={dst}&dt=t&q={query}"
    )

    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return "".join(chunk[0] for chunk in payload[0] if chunk and chunk[0] is not None)
        except Exception as err:
            last_err = err
            time.sleep(0.1 * (attempt + 1))

    raise RuntimeError(f"translate_failed: {last_err}")


def load_no_translate_terms() -> List[str]:
    if not GLOSSARY_PATH.exists():
        return []

    try:
        data = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
        cats = data.get("categories", {})
        terms: List[str] = []
        for values in cats.values():
            if isinstance(values, list):
                for v in values:
                    if isinstance(v, str) and v.strip():
                        terms.append(v.strip())
        # Longest first to avoid partial overlaps.
        terms = sorted(set(terms), key=len, reverse=True)
        return terms
    except Exception:
        return []


def protect_with_placeholders(text: str, terms: List[str]) -> Tuple[str, Dict[str, str]]:
    placeholders: Dict[str, str] = {}
    idx = 0

    def stash(match_text: str) -> str:
        nonlocal idx
        key = f"__PH_{idx}__"
        placeholders[key] = match_text
        idx += 1
        return key

    protected = text

    # URLs first.
    protected = URL_RE.sub(lambda m: stash(m.group(0)), protected)
    # Discord specific entities.
    protected = DISCORD_TAG_RE.sub(lambda m: stash(m.group(0)), protected)
    # Inline code spans.
    protected = INLINE_CODE_RE.sub(lambda m: stash(m.group(0)), protected)

    # Preserve no-translate terms using simple boundary-aware replacement.
    for term in terms:
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])")
        protected = pattern.sub(lambda m: stash(m.group(0)), protected)

    return protected, placeholders


def unprotect(text: str, placeholders: Dict[str, str]) -> str:
    out = text
    for key, value in placeholders.items():
        out = out.replace(key, value)
    return out


def translate_file(en_file: Path, ru_file: Path, terms: List[str]) -> Tuple[int, int]:
    src_lines = en_file.read_text(encoding="utf-8").splitlines()

    out_lines: List[str] = []
    translated_lines = 0
    fallback_lines = 0
    in_code_block = False

    for line in src_lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        # Keep blank lines and code blocks as-is.
        if not stripped or in_code_block:
            out_lines.append(line)
            continue

        # Keep pure URL lines as-is.
        if stripped.startswith("http://") or stripped.startswith("https://"):
            out_lines.append(line)
            continue

        protected, placeholders = protect_with_placeholders(line, terms)

        try:
            translated = google_translate(protected)
            translated = unprotect(translated, placeholders)
            # Keep exact line structure: one input line -> one output line.
            translated = translated.replace("\r", " ").replace("\n", " ")
            out_lines.append(translated)
            translated_lines += 1
        except Exception:
            # Strict no-loss fallback: keep original English line.
            out_lines.append(line)
            fallback_lines += 1

        # Light throttle to avoid API throttling.
        time.sleep(0.01)

    ru_file.parent.mkdir(parents=True, exist_ok=True)
    ru_file.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8")
    return translated_lines, fallback_lines


def main() -> None:
    if not EN_ROOT.exists():
        raise SystemExit("guides/en not found")

    terms = load_no_translate_terms()
    en_files = sorted(EN_ROOT.rglob("*.md"))

    report = {
        "total_files": len(en_files),
        "processed": 0,
        "total_translated_lines": 0,
        "total_fallback_lines": 0,
        "files": [],
    }

    print(f"Rebuilding RU guides from EN. Files: {len(en_files)}")

    for i, en_file in enumerate(en_files, 1):
        rel = en_file.relative_to(EN_ROOT)
        ru_file = RU_ROOT / rel

        translated_lines, fallback_lines = translate_file(en_file, ru_file, terms)

        report["processed"] += 1
        report["total_translated_lines"] += translated_lines
        report["total_fallback_lines"] += fallback_lines
        report["files"].append(
            {
                "file": str(rel).replace("\\", "/"),
                "translated_lines": translated_lines,
                "fallback_lines": fallback_lines,
            }
        )

        if i % 10 == 0 or i == len(en_files):
            print(f"  [{i}/{len(en_files)}] {rel}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Done.")
    print(f"Processed files: {report['processed']}")
    print(f"Translated lines: {report['total_translated_lines']}")
    print(f"Fallback lines: {report['total_fallback_lines']}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
