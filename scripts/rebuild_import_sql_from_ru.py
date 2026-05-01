from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
RU_DIR = ROOT / "guides" / "ru"
SQL_PATH = ROOT / "scripts" / "import_neon.sql"

CDN_BASE = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main"
URL_RE = re.compile(r"https?://[^\s)'\"]+")
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}

CATEGORY_RU_TITLES = {
    "adventure": "Приключение",
    "beginner-guide": "Гайд для новичков",
    "character": "Персонаж",
    "companion": "Спутник",
    "early-game-promotions": "Ранние продвижения",
    "mid-game-promotions": "Средние продвижения",
    "late-game-promotions": "Поздние продвижения",
    "equipment": "Снаряжение",
    "event-help": "Помощь по событиям",
    "misc": "Разное",
    "new_from_discord": "Новое из Discord",
    "skills": "Навыки",
    "slayer-playbook": "Slayer Playbook",
    "spirit": "Духи",
    "stage": "Стадии",
    "shop": "Магазин",
    "promotion-recommendation": "Рекомендации по продвижению",
    "disclaimer": "Дисклеймер",
}


def sql_escape(s: str) -> str:
    return s.replace("'", "''")


def normalize_key(category: str, filename: str) -> str:
    stem = filename.replace(".md", "")
    raw = f"{category}_{stem}".lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return re.sub(r"_+", "_", raw).strip("_")


def title_from_filename(filename: str) -> str:
    stem = filename.replace(".md", "").replace("_", " ").replace("-", " ")
    # Keep existing title casing from file name but avoid all-lower titles.
    return stem[:1].upper() + stem[1:] if stem else stem


def is_video(url: str) -> bool:
    p = urlparse(url).path.lower()
    return any(p.endswith(ext) for ext in VIDEO_EXT)


def clean_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


def normalize_link_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def alias_variants(alias: str) -> set[str]:
    variants: set[str] = set()
    if not alias:
        return variants

    variants.add(alias)

    for prefix in ("the_", "a_", "an_"):
        if alias.startswith(prefix):
            variants.add(alias[len(prefix) :])

    if alias.endswith("ies") and len(alias) > 4:
        variants.add(alias[:-3] + "y")
    if alias.endswith("es") and len(alias) > 3:
        variants.add(alias[:-2])
    if alias.endswith("s") and len(alias) > 2:
        variants.add(alias[:-1])

    return {v.strip("_") for v in variants if v.strip("_")}


def resolve_key(label: str, alias_to_key: dict[str, str]) -> str | None:
    base = normalize_link_label(label)
    for candidate in alias_variants(base):
        key = alias_to_key.get(candidate)
        if key:
            return key
    return None


def build_guide_key_lookup() -> tuple[dict[Path, str], dict[str, str]]:
    path_to_key: dict[Path, str] = {}
    alias_to_key: dict[str, str] = {}

    for category_dir in sorted(RU_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for guide_file in sorted(category_dir.glob("*.md")):
            key = normalize_key(category_dir.name, guide_file.name)
            resolved = guide_file.resolve()
            path_to_key[resolved] = key
            for alias in {
                normalize_link_label(guide_file.stem.replace("_", " ")),
                normalize_link_label(guide_file.stem.replace("-", " ")),
            }:
                for variant in alias_variants(alias):
                    alias_to_key.setdefault(variant, key)

    return path_to_key, alias_to_key


def rewrite_internal_links(
    content: str,
    current_file: Path,
    path_to_key: dict[Path, str],
    alias_to_key: dict[str, str],
) -> str:
    def replace_wikilink(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        label = (match.group(2) or "").strip()
        return match.group(0) if not label else f"[[{key}|{label}]]"

    content = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", replace_wikilink, content)

    def replace_markdown_link(match: re.Match[str]) -> str:
        label = match.group(1).strip()
        target = match.group(2).strip()

        if target.startswith(("http://", "https://")):
            key = resolve_key(label, alias_to_key)
            return f"[[{key}|{label}]]" if key else match.group(0)

        if target.endswith(".md"):
            resolved = (current_file.parent / target).resolve()
            key = path_to_key.get(resolved)
            if key:
                return f"[[{key}|{label}]]"

        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", replace_markdown_link, content)


def map_media_url(url: str) -> str:
    # Keep live Discord attachment links untouched (user explicitly asked to keep tokenized live media).
    if "discordapp.com/attachments/" in url or "discordapp.net/attachments/" in url:
        return clean_url(url)

    # Keep already-correct jsDelivr links for this repository.
    if "cdn.jsdelivr.net/gh/Nihronick/blackrose@main/assets/" in url:
        return url

    p = urlparse(url)
    path = p.path.lstrip("/")
    filename = Path(path).name
    ext = Path(filename).suffix.lower()

    # Existing slayerpedia links -> normalize to repository CDN path by filename
    if "/assets/images/slayerpedia/" in p.path:
        folder = "video" if is_video(url) else "image"
        return f"{CDN_BASE}/assets/images/slayerpedia/{folder}/{filename}"

    # Discord emoji -> icons/discord_migrated
    if "/emojis/" in p.path:
        return f"{CDN_BASE}/assets/images/icons/discord_migrated/{filename}"

    # Fallback: keep as-is
    return clean_url(url)


def collect_categories() -> list[str]:
    return sorted([d.name for d in RU_DIR.iterdir() if d.is_dir()])


def build_sql() -> str:
    categories = collect_categories()
    path_to_key, alias_to_key = build_guide_key_lookup()

    lines: list[str] = []
    lines.append("TRUNCATE TABLE guides CASCADE;")
    lines.append("TRUNCATE TABLE categories CASCADE;")

    for cat in categories:
        title = CATEGORY_RU_TITLES.get(cat, cat.replace("-", " ").replace("_", " ").title())
        lines.append(
            f"INSERT INTO categories (key, title) VALUES ('{sql_escape(cat)}', '{sql_escape(title)}') ON CONFLICT (key) DO NOTHING;"
        )

    for cat in categories:
        files = sorted((RU_DIR / cat).rglob("*.md"))
        for md in files:
            key = normalize_key(cat, md.name)
            title = title_from_filename(md.name)
            text = md.read_text(encoding="utf-8", errors="ignore")
            text = rewrite_internal_links(text, md, path_to_key, alias_to_key)

            # Map media links in text to gh-pages assets
            def repl(m: re.Match[str]) -> str:
                return map_media_url(m.group(0))

            text_mapped = URL_RE.sub(repl, text)

            lines.append("")
            lines.append("INSERT INTO guides (key, category_key, title, text, photo, video)")
            lines.append("VALUES (")
            lines.append(f"  '{sql_escape(key)}',")
            lines.append(f"  '{sql_escape(cat)}',")
            lines.append(f"  '{sql_escape(title)}',")
            lines.append(f"  '{sql_escape(text_mapped)}',")
            lines.append("  '{}',")
            lines.append("  '{}'")
            lines.append(") ON CONFLICT (key) DO UPDATE SET")
            lines.append("  text = EXCLUDED.text,")
            lines.append("  title = EXCLUDED.title,")
            lines.append("  photo = EXCLUDED.photo,")
            lines.append("  video = EXCLUDED.video,")
            lines.append("  updated_at = NOW();")

    return "\n".join(lines) + "\n"


def main() -> None:
    sql = build_sql()
    SQL_PATH.write_text(sql, encoding="utf-8")
    print("WROTE", SQL_PATH)
    print("GUIDE_INSERTS", sql.count("INSERT INTO guides (key, category_key, title, text, photo, video)"))
    print("GH_PAGES_URLS", len(re.findall(r"https?://cdn\.jsdelivr\.net/gh/Nihronick/blackrose@gh-pages/assets/", sql)))
    print("DISCORD_URLS", len(re.findall(r"discordapp\.(?:com|net)/attachments/", sql)))
    print("RAW_GH_URLS", len(re.findall(r"raw\.githubusercontent\.com", sql)))


if __name__ == "__main__":
    main()
