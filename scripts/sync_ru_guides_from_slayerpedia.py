import re
import argparse
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from deep_translator import GoogleTranslator


ROOT = Path(__file__).resolve().parent.parent
RU_DIR = ROOT / "guides" / "ru"
SLAYER_DIR = ROOT / "slayerpedia"
ASSETS_DIR = ROOT / "assets" / "images" / "slayerpedia"
ICONS_PY = ROOT / "backend" / "icons.py"
TERMS_MD = ROOT / "guides" / "en" / "_glossary.md"

CDN_BASE = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main"

URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
DISCORD_CHANNEL_RE = re.compile(r"^https?://discord\.com/channels/\d+/(\d+)(?:/\d+)?$", re.IGNORECASE)
DISCORD_ATTACHMENT_RE = re.compile(
    r"^https?://(?:cdn|media)\.discordapp\.(?:com|net)/attachments/\d+/(\d+)/([^/?#]+)",
    re.IGNORECASE,
)
DISCORD_EMOJI_TAG_RE = re.compile(r"<a?:([A-Za-z0-9_]+):(\d{10,})>")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
ID_RE = re.compile(r"(\d{10,})")
INLINE_CODE_RE = re.compile(r"`[^`]+`")
ICON_TOKEN_RE = re.compile(r"\{\{[^{}]+\}\}")
CYBERLINK_RE = re.compile(r"\[\[[^\]]+\]\]")
TABLE_ROW_RE = re.compile(r"^\|.*\|$")
ABBR_LINE_RE = re.compile(r"^\s*\*\s*([A-Za-z0-9+]{2,})\s*=\s*([^\n\-]+)")

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
TRAILING_PUNCT = ",.;:!?)"

MANUAL_CHANNEL_MAP: dict[str, str] = {
    "1124549609784627280": "equipment_souls_and_soul_weapons",
    "1299025902595997726": "skills_familiars",
    "1370968101645979689": "early_game_promotions_stone",
    "1370968331707879564": "early_game_promotions_bronze",
    "1370968450595553372": "early_game_promotions_iron",
    "1370968571320074401": "early_game_promotions_silver",
    "1370968676370616320": "early_game_promotions_gold",
    "1370968748231757975": "early_game_promotions_mithril",
    "1370968829773217832": "early_game_promotions_orichalcum",
    "1370968915949125682": "early_game_promotions_arcanite",
    "1370969029031886859": "early_game_promotions_adamant",
    "1370969136745676851": "early_game_promotions_ether",
    "1370969324235395102": "mid_game_promotions_black_mythril",
    "1370969425167126649": "mid_game_promotions_demon_metal",
    "1370969530364334231": "mid_game_promotions_dragonos",
    "1370969665827766404": "mid_game_promotions_ragnablood",
    "1370969833570570331": "mid_game_promotions_warfrost",
    "1370970051003547759": "mid_game_promotions_dark_nox",
    "1370970165365440593": "mid_game_promotions_blue_abyss",
    "1370970289625632961": "mid_game_promotions_infinaut",
    "1370970624708710421": "mid_game_promotions_cyclos",
    "1370970872567042108": "mid_game_promotions_ancient_canine",
    "1370971028137705496": "late_game_promotions_gigarock",
    "1370971139836350514": "late_game_promotions_eisenhart",
    "1370971249760796782": "late_game_promotions_diadust",
    "1416434919131058377": "late_game_promotions_eldenwood",
}


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def slayer_key(category: str, stem: str) -> str:
    return f"{norm(category)}_{norm(stem)}"


def build_ru_path_map() -> dict[tuple[str, str], Path]:
    out: dict[tuple[str, str], Path] = {}
    for p in RU_DIR.rglob("*.md"):
        out[(norm(p.parent.name), norm(p.stem))] = p
    return out


def build_guide_index() -> tuple[dict[str, set[str]], dict[str, str]]:
    aliases_by_key: dict[str, set[str]] = {}
    alias_to_key: dict[str, str] = {}
    for p in RU_DIR.rglob("*.md"):
        key = slayer_key(p.parent.name, p.stem)
        aliases = {
            norm(p.stem),
            norm(p.stem.replace("_", " ")),
            norm(p.stem.replace("_", " ").replace("-", " ")),
        }
        aliases_by_key[key] = aliases
        for a in aliases:
            if a and a not in alias_to_key:
                alias_to_key[a] = key
    return aliases_by_key, alias_to_key


def best_key_for_label(label: str, alias_to_key: dict[str, str], aliases_by_key: dict[str, set[str]]) -> str | None:
    n = norm(label)
    if not n:
        return None
    if n in alias_to_key:
        return alias_to_key[n]
    best: tuple[int, str] | None = None
    for key, aliases in aliases_by_key.items():
        score = 0
        for a in aliases:
            if n == a:
                score = max(score, 1000)
            elif n in a or a in n:
                score = max(score, min(len(a), len(n)))
        if score > 0 and (best is None or score > best[0]):
            best = (score, key)
    return best[1] if best else None


def parse_term_map() -> dict[str, str]:
    if not TERMS_MD.exists():
        return {}
    text = TERMS_MD.read_text(encoding="utf-8", errors="ignore")
    term_map: dict[str, str] = {}
    for line in text.splitlines():
        if not TABLE_ROW_RE.match(line.strip()):
            continue
        if line.strip().startswith("| :---"):
            continue
        parts = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(parts) < 2:
            continue
        en, ru = parts[0], parts[1]
        if en and ru and en.lower() != "оригинал (en)":
            term_map[en] = ru
    return term_map


def parse_abbrev_map() -> dict[str, str]:
    source = SLAYER_DIR / "Beginner-guide" / "Glossary of Terms.txt"
    if not source.exists():
        return {}
    text = source.read_text(encoding="utf-8", errors="ignore")
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = ABBR_LINE_RE.match(line)
        if not m:
            continue
        abbr = m.group(1).strip()
        full = m.group(2).strip()
        if abbr and full:
            out[abbr] = full
    return out


def protect_segments(text: str) -> tuple[str, dict[str, str]]:
    patterns = [
        URL_RE,
        ICON_TOKEN_RE,
        CYBERLINK_RE,
        INLINE_CODE_RE,
        re.compile(r"<a?:[A-Za-z0-9_]+:\d{10,}>"),
        re.compile(r"!\[[^\]]*\]\([^)]+\)"),
        re.compile(r"\[[^\]]+\]\([^)]+\)"),
        re.compile(r"\b[A-Z]{2,}\b"),
        re.compile(r"\d+\*?"),
    ]
    repls: dict[str, str] = {}
    idx = 0
    out = text

    def token(i: int) -> str:
        return f"@@PH{i}@@"

    for pat in patterns:
        def _r(m: re.Match[str]) -> str:
            nonlocal idx
            key = token(idx)
            idx += 1
            repls[key] = m.group(0)
            return key
        out = pat.sub(_r, out)
    return out, repls


def restore_segments(text: str, repls: dict[str, str]) -> str:
    out = text
    for _ in range(5):
        changed = False
        for k, v in repls.items():
            if k in out:
                out = out.replace(k, v)
                changed = True
        if not changed:
            break
    return out


def apply_glossary(text: str, term_map: dict[str, str]) -> str:
    out = text
    for en, ru in sorted(term_map.items(), key=lambda kv: len(kv[0]), reverse=True):
        out = re.sub(rf"(?<!\w){re.escape(en)}(?!\w)", ru, out, flags=re.IGNORECASE)
    return out


def expand_abbreviations(text: str, abbrev_map: dict[str, str]) -> str:
    out = text
    for abbr, full in sorted(abbrev_map.items(), key=lambda kv: len(kv[0]), reverse=True):
        out = re.sub(rf"(?<!\w){re.escape(abbr)}(?!\w)", full, out)
    return out


def translate_block(text: str, translator: GoogleTranslator, term_map: dict[str, str], abbrev_map: dict[str, str]) -> str:
    text = expand_abbreviations(text, abbrev_map)
    protected, repls = protect_segments(text)
    lines = protected.splitlines()
    out_lines = lines[:]

    translatable_idx: list[int] = []
    translatable_lines: list[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or TABLE_ROW_RE.match(s):
            continue
        translatable_idx.append(i)
        translatable_lines.append(line)

    chunk = 40
    for i in range(0, len(translatable_lines), chunk):
        part = translatable_lines[i : i + chunk]
        try:
            tr_part = translator.translate_batch(part)  # type: ignore[attr-defined]
            if not isinstance(tr_part, list):
                tr_part = [translator.translate(x) or x for x in part]
        except Exception:
            tr_part = []
            for x in part:
                try:
                    tr_part.append(translator.translate(x) or x)
                except Exception:
                    tr_part.append(x)
        for j, original in enumerate(part):
            translated = tr_part[j] if j < len(tr_part) else original
            if not isinstance(translated, str) or not translated:
                translated = original
            out_lines[translatable_idx[i + j]] = translated

    out = "\n".join(out_lines)
    out = restore_segments(out, repls)
    out = apply_glossary(out, term_map)
    return out


def build_channel_map(alias_to_key: dict[str, str], aliases_by_key: dict[str, set[str]]) -> dict[str, str]:
    channel_to_key: dict[str, str] = {}
    for txt in SLAYER_DIR.rglob("*.txt"):
        raw = txt.read_text(encoding="utf-8", errors="ignore")
        for m in MARKDOWN_LINK_RE.finditer(raw):
            label = m.group(1).strip()
            url = m.group(2).strip()
            cm = DISCORD_CHANNEL_RE.match(url)
            if not cm:
                continue
            channel_id = cm.group(1)
            key = best_key_for_label(label, alias_to_key, aliases_by_key)
            if key and channel_id not in channel_to_key:
                channel_to_key[channel_id] = key
    channel_to_key.update(MANUAL_CHANNEL_MAP)
    return channel_to_key


def build_asset_id_index() -> dict[str, list[Path]]:
    idx: dict[str, list[Path]] = {}
    if not ASSETS_DIR.exists():
        return idx
    for f in ASSETS_DIR.rglob("*.*"):
        rel = f.relative_to(ROOT)
        for media_id in ID_RE.findall(f.name):
            idx.setdefault(media_id, []).append(rel)
    return idx


def is_video_url(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in VIDEO_EXT


def is_image_url(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in IMAGE_EXT


def map_attachment_url(url: str, guide_stem_norm: str, asset_idx: dict[str, list[Path]]) -> str:
    m = DISCORD_ATTACHMENT_RE.match(url)
    if not m:
        return url
    attach_id, filename = m.groups()
    expected_video = Path(filename).suffix.lower() in VIDEO_EXT
    candidates = asset_idx.get(attach_id, [])
    if not candidates:
        return url
    preferred = [c for c in candidates if (c.suffix.lower() in VIDEO_EXT) == expected_video] or candidates
    best = next((c for c in preferred if guide_stem_norm in norm(c.stem)), preferred[0])
    return f"{CDN_BASE}/{best.as_posix()}"


def map_raw_github_url(url: str) -> str:
    p = urlparse(url)
    if p.netloc.lower() != "raw.githubusercontent.com":
        return url
    marker = "/assets/"
    i = p.path.find(marker)
    if i == -1:
        return url
    return f"{CDN_BASE}/{p.path[i+1:]}"


def map_other_url(url: str, guide_stem_norm: str, channel_map: dict[str, str], asset_idx: dict[str, list[Path]]) -> str:
    cm = DISCORD_CHANNEL_RE.match(url)
    if cm:
        key = channel_map.get(cm.group(1))
        return f"[[{key}]]" if key else ""
    mapped = map_attachment_url(url, guide_stem_norm, asset_idx)
    if mapped != url:
        return mapped
    return map_raw_github_url(url)


def split_url_trailing_punct(url: str) -> tuple[str, str]:
    tail = ""
    while url and url[-1] in TRAILING_PUNCT:
        tail = url[-1] + tail
        url = url[:-1]
    return url, tail


def replace_discord_emoji_tags(text: str, known_icon_ids: set[str]) -> str:
    def repl(m: re.Match[str]) -> str:
        name, emoji_id = m.groups()
        return f"{{{{icon_{emoji_id}}}}}" if emoji_id in known_icon_ids else f":{name}:"
    return DISCORD_EMOJI_TAG_RE.sub(repl, text)


def replace_markdown_links(text: str, alias_to_key: dict[str, str], aliases_by_key: dict[str, set[str]], channel_map: dict[str, str], guide_stem_norm: str, asset_idx: dict[str, list[Path]]) -> str:
    def repl(m: re.Match[str]) -> str:
        label = m.group(1).strip()
        url = m.group(2).strip()
        cm = DISCORD_CHANNEL_RE.match(url)
        if cm:
            key = channel_map.get(cm.group(1)) or best_key_for_label(label, alias_to_key, aliases_by_key)
            return f"[[{key}|{label}]]" if key else label
        replaced = map_attachment_url(url, guide_stem_norm, asset_idx)
        if replaced != url:
            if is_video_url(replaced):
                return f"[Video: {Path(urlparse(replaced).path).name}]({replaced})"
            if is_image_url(replaced):
                return f"![{label}]({replaced})"
            return f"[{label}]({replaced})"
        replaced = map_raw_github_url(url)
        if replaced != url:
            if is_video_url(replaced):
                return f"[Video: {Path(urlparse(replaced).path).name}]({replaced})"
            if is_image_url(replaced):
                return f"![{label}]({replaced})"
            return f"[{label}]({replaced})"
        return m.group(0)
    return MARKDOWN_LINK_RE.sub(repl, text)


def replace_plain_urls(text: str, guide_stem_norm: str, channel_map: dict[str, str], asset_idx: dict[str, list[Path]]) -> str:
    def repl(m: re.Match[str]) -> str:
        full = m.group(0)
        core, tail = split_url_trailing_punct(full)
        return map_other_url(core, guide_stem_norm, channel_map, asset_idx) + tail
    return URL_RE.sub(repl, text)


def normalize_url_lines(text: str) -> str:
    out_lines: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("http://") or s.startswith("https://"):
            if is_video_url(s):
                out_lines.append(f"[Video: {Path(urlparse(s).path).name}]({s})")
                continue
            if is_image_url(s):
                out_lines.append(f"![image]({s})")
                continue
        out_lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out_lines)).strip() + "\n"


def download_bytes(url: str) -> bytes:
    candidates = [url]
    clean = f"{urlparse(url).scheme}://{urlparse(url).netloc}{urlparse(url).path}"
    if clean not in candidates:
        candidates.append(clean)
    if "cdn.discordapp.com/attachments/" in clean:
        candidates.append(clean.replace("cdn.discordapp.com", "media.discordapp.net"))
    last_err: Exception | None = None
    for c in candidates:
        try:
            req = Request(c, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise RuntimeError("download failed")


def cache_discord_media_in_ru() -> tuple[int, int, int]:
    changed_files = 0
    downloaded = 0
    failed = 0
    for p in RU_DIR.rglob("*.md"):
        raw = p.read_text(encoding="utf-8", errors="ignore")
        out = raw
        for url in sorted(set(URL_RE.findall(raw)), key=len, reverse=True):
            m = DISCORD_ATTACHMENT_RE.match(url)
            if not m:
                continue
            attach_id, filename = m.groups()
            ext = Path(filename).suffix.lower() or ".png"
            kind = "video" if ext in VIDEO_EXT else "image"
            dest_rel = Path(f"assets/images/slayerpedia/{kind}/discord-{attach_id}{ext}")
            dest_abs = ROOT / dest_rel
            new_url = f"{CDN_BASE}/{dest_rel.as_posix()}"
            if not dest_abs.exists():
                try:
                    dest_abs.parent.mkdir(parents=True, exist_ok=True)
                    dest_abs.write_bytes(download_bytes(url))
                    downloaded += 1
                except Exception:
                    failed += 1
                    continue
            out = out.replace(url, new_url)
        out = re.sub(
            r"https?://raw\.githubusercontent\.com/Nihronick/blackrose/main/(assets/[^\s)\]\"']+)",
            lambda mm: f"{CDN_BASE}/{mm.group(1)}",
            out,
        )
        if out != raw:
            p.write_text(out, encoding="utf-8")
            changed_files += 1
    return changed_files, downloaded, failed


def read_known_icon_ids() -> set[str]:
    raw = ICONS_PY.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"\"icon_(\d{10,})\"\s*:", raw))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync/translate Slayerpedia txt into guides/ru")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Slayerpedia category folder name (repeatable), e.g. adventure",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=0,
        help="Process at most N Slayerpedia files (0 = all)",
    )
    parser.add_argument(
        "--skip-media-cache",
        action="store_true",
        help="Do not download/cache unresolved Discord attachments",
    )
    args = parser.parse_args()

    category_filter = {norm(x) for x in args.category if x.strip()}
    max_files = max(0, args.max_files)

    ru_map = build_ru_path_map()
    aliases_by_key, alias_to_key = build_guide_index()
    channel_map = build_channel_map(alias_to_key, aliases_by_key)
    asset_idx = build_asset_id_index()
    known_icon_ids = read_known_icon_ids()
    terms = parse_term_map()
    abbrev_map = parse_abbrev_map()
    translator = GoogleTranslator(source="auto", target="ru")

    changed = 0
    synced = 0
    missing = 0

    processed = 0
    for src in sorted(SLAYER_DIR.rglob("*.txt")):
        if category_filter and norm(src.parent.name) not in category_filter:
            continue
        if max_files and processed >= max_files:
            break

        src_cat_norm = norm(src.parent.name)
        src_stem_norm = norm(src.stem)
        dst = ru_map.get((src_cat_norm, src_stem_norm))
        if not dst:
            # Create missing RU guide path from Slayerpedia structure.
            matched_category_dir = next((d for d in RU_DIR.iterdir() if d.is_dir() and norm(d.name) == src_cat_norm), None)
            category_dir = matched_category_dir if matched_category_dir else (RU_DIR / src.parent.name.lower().replace(" ", "-"))
            category_dir.mkdir(parents=True, exist_ok=True)
            filename = src.stem.replace(" ", "_") + ".md"
            dst = category_dir / filename
            ru_map[(src_cat_norm, src_stem_norm)] = dst
            missing += 1
        synced += 1

        raw = src.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
        out = translate_block(raw, translator, terms, abbrev_map)
        out = replace_discord_emoji_tags(out, known_icon_ids)
        out = replace_markdown_links(out, alias_to_key, aliases_by_key, channel_map, norm(src.stem), asset_idx)
        out = replace_plain_urls(out, norm(src.stem), channel_map, asset_idx)
        out = normalize_url_lines(out)

        prev = dst.read_text(encoding="utf-8", errors="ignore") if dst.exists() else ""
        if out != prev:
            dst.write_text(out, encoding="utf-8")
            changed += 1
        processed += 1

    print(f"Slayer files processed: {processed}")
    print(f"Slayer files synced: {synced}")
    print(f"RU guides changed: {changed}")
    print(f"Slayer files without RU match: {missing}")
    print(f"Channel mappings built: {len(channel_map)}")

    if not args.skip_media_cache:
        media_files_changed, media_downloaded, media_failed = cache_discord_media_in_ru()
        print(f"RU media rewrite changed files: {media_files_changed}")
        print(f"Discord media downloaded: {media_downloaded}")
        print(f"Discord media failed: {media_failed}")
    else:
        print("RU media cache skipped")


if __name__ == "__main__":
    main()
