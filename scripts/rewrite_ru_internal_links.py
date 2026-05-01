#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "guides" / "en"
RU_DIR = ROOT / "guides" / "ru"


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9а-яё]+", "_", text.lower()).strip("_")


def alias_variants(alias: str) -> set[str]:
    variants: set[str] = set()
    if not alias:
        return variants

    variants.add(alias)

    for prefix in ("the_", "a_", "an_"):
        if alias.startswith(prefix):
            variants.add(alias[len(prefix) :])

    # Lightweight singularization for common labels (e.g. mines -> mine).
    if alias.endswith("ies") and len(alias) > 4:
        variants.add(alias[:-3] + "y")
    if alias.endswith("es") and len(alias) > 3:
        variants.add(alias[:-2])
    if alias.endswith("s") and len(alias) > 2:
        variants.add(alias[:-1])

    return {v.strip("_") for v in variants if v.strip("_")}


def resolve_key(label: str, alias_to_key: Dict[str, str]) -> Optional[str]:
    base = normalize(label)
    for candidate in alias_variants(base):
        key = alias_to_key.get(candidate)
        if key:
            return key
    return None


def key_for(category: str, filename: str) -> str:
    stem = filename[:-3] if filename.endswith(".md") else filename
    raw = f"{category}_{stem}".lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return re.sub(r"_+", "_", raw).strip("_")


def file_aliases(path: Path) -> set[str]:
    aliases: set[str] = set()
    aliases.add(normalize(path.stem))
    aliases.add(normalize(path.stem.replace("_", " ")))
    aliases.add(normalize(path.stem.replace("-", " ")))

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return aliases

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            stripped = stripped.lstrip("# ").strip()
        stripped = re.sub(r"<:[^:>]+:\d+>", " ", stripped)
        stripped = re.sub(r"\[[^\]]+\]\([^\)]+\)", lambda m: m.group(0), stripped)
        stripped = re.sub(r"[>*`_~]+", " ", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if stripped:
            aliases.add(normalize(stripped))
            # collect first two meaningful lines only for stability
            if len(aliases) > 24:
                break
    return aliases


def build_guide_index() -> Tuple[Dict[Path, str], Dict[str, str]]:
    path_to_key: Dict[Path, str] = {}
    alias_to_key: Dict[str, str] = {}

    for lang_dir in [EN_DIR, RU_DIR]:
        if not lang_dir.exists():
            continue
        for category_dir in sorted(lang_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            for md in sorted(category_dir.glob("*.md")):
                key = key_for(category_dir.name, md.name)
                resolved = md.resolve()
                path_to_key[resolved] = key
                for alias in file_aliases(md):
                    for variant in alias_variants(alias):
                        alias_to_key.setdefault(variant, key)

    return path_to_key, alias_to_key


LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://discord\.com/channels/[^\)]+)\)")
BARE_DISCORD_RE = re.compile(r"https?://(?:discord\.com|discordapp\.com)/channels/\S+")


def extract_heading_label(line: str) -> Optional[str]:
    if not line.lstrip().startswith("#"):
        return None

    label = re.sub(r"^#+\s*", "", line).strip()
    label = re.sub(r"<:[^:>]+:\d+>", " ", label)
    label = re.sub(r"[\-—–•`*_~]+", " ", label)
    label = re.sub(r"\s+", " ", label).strip()
    return label or None


def bare_url_candidates(line_prefix: str, current_heading: Optional[str]) -> List[str]:
    candidates: List[str] = []

    prefix = re.sub(r"<:([^:>]+):\d+>", r"\1", line_prefix)
    prefix = re.sub(r"\[[^\]]+\]\([^\)]+\)", " ", prefix)
    prefix = re.sub(r"[>*`_~]+", " ", prefix)
    prefix = re.sub(r"[\-—–:|]+", " ", prefix)
    prefix = re.sub(r"\s+", " ", prefix).strip()
    if prefix:
        candidates.append(prefix)

    emoji_names = re.findall(r"<:([^:>]+):\d+>", line_prefix)
    for emoji_name in emoji_names:
        if emoji_name not in candidates:
            candidates.append(emoji_name)

    if current_heading and current_heading not in candidates:
        candidates.append(current_heading)

    return candidates


def rewrite_content(content: str, current_file: Path, path_to_key: Dict[Path, str], alias_to_key: Dict[str, str]) -> Tuple[str, List[str]]:
    meta_links: List[str] = []

    def add_meta(key: str) -> None:
        if key and key not in meta_links:
            meta_links.append(key)

    def resolve_from_label(label: str) -> Optional[str]:
        key = resolve_key(label, alias_to_key)
        if not key and "&" in label:
            key = resolve_key(label.replace("&", " and "), alias_to_key)
        return key

    def replace_markdown_link(match: re.Match[str]) -> str:
        label = match.group(1).strip()

        key = resolve_from_label(label)

        if key:
            add_meta(key)
            return f"[[{key}|{label}]]"
        return match.group(0)

    lines = content.splitlines()
    out_lines: List[str] = []
    current_heading: Optional[str] = None
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            out_lines.append(line)
            continue

        if in_code_block:
            out_lines.append(line)
            continue

        heading_label = extract_heading_label(line)
        if heading_label:
            current_heading = heading_label

        line = LINK_RE.sub(replace_markdown_link, line)

        def replace_bare_discord(match: re.Match[str]) -> str:
            line_prefix = line[: match.start()]
            for candidate in bare_url_candidates(line_prefix, current_heading):
                key = resolve_from_label(candidate)
                if key:
                    add_meta(key)
                    return f"[[{key}]]"
            return match.group(0)

        if BARE_DISCORD_RE.search(line):
            line = BARE_DISCORD_RE.sub(replace_bare_discord, line)

        out_lines.append(line)

    content = "\n".join(out_lines)

    # Existing wikilinks should also count as meta links.
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", content):
        add_meta(m.group(1).strip())

    return content, meta_links


def update_meta_section(content: str, meta_links: list[str]) -> str:
    if not meta_links:
        return content

    meta_block = "## Мета-ссылки\n" + "\n".join(f"- [[{key}]]" for key in meta_links) + "\n"
    if re.search(r"^##\s+Мета-ссылки\s*$", content, flags=re.MULTILINE):
        content = re.sub(
            r"(?ms)^##\s+Мета-ссылки\s*$.*$",
            meta_block.rstrip(),
            content,
            count=1,
        )
        if not content.endswith("\n"):
            content += "\n"
        return content

    if not content.endswith("\n"):
        content += "\n"
    return content + "\n" + meta_block


def main() -> None:
    path_to_key, alias_to_key = build_guide_index()
    updated = 0
    skipped = 0

    for md in sorted(RU_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        new_text, meta_links = rewrite_content(text, md, path_to_key, alias_to_key)
        new_text = update_meta_section(new_text, meta_links)

        if new_text != text:
            md.write_text(new_text.rstrip() + "\n", encoding="utf-8")
            updated += 1
        else:
            skipped += 1

    print(f"updated={updated} skipped={skipped}")


if __name__ == "__main__":
    main()