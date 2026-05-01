import re
from pathlib import Path
from urllib.parse import urlparse


def resolve_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    if (cwd / "guides" / "ru").exists():
        return cwd

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "guides" / "ru").exists():
            return parent
    return here.parents[3]


ROOT = resolve_repo_root()
SQL_PATH = ROOT / "scripts" / "guide-processing" / "db" / "import_neon.sql"
RU_DIR = ROOT / "guides" / "ru"

URL_RE = re.compile(r"https?://[^\s)'\"]+")
MEDIA_URL_RE = re.compile(
    r"https?://(?:cdn\.jsdelivr\.net/gh/Nihronick/blackrose@gh-pages/assets/|raw\.githubusercontent\.com/.*/assets/images/slayerpedia/|(?:cdn|media)\.discordapp\.(?:com|net)/attachments/)",
    re.I,
)
ID_RE = re.compile(r"\d{10,}")

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}


def normalize_key(category_dir: str, filename: str) -> str:
    return f"{category_dir}_{filename.replace('.md', '')}".lower().replace("-", "_")


def slug_tokens(name: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", name.lower()) if t}


def is_video(url: str, line: str = "") -> bool:
    path = urlparse(url).path.lower()
    if any(path.endswith(ext) for ext in VIDEO_EXT):
        return True
    return "[Video:" in line


def clean_discord_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


def build_ru_media_map() -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    for md in RU_DIR.rglob("*.md"):
        key = normalize_key(md.parent.name, md.name)
        text = md.read_text(encoding="utf-8", errors="ignore")
        urls = []
        for u in URL_RE.findall(text):
            if (
                "/assets/images/slayerpedia/" in u
                or "cdn.discordapp.com/attachments/" in u
                or "media.discordapp.net/attachments/" in u
            ):
                urls.append(clean_discord_url(u) if "discordapp." in u else u)
        data[key] = urls
    return data


def list_gh_assets() -> tuple[list[str], dict[str, list[str]], dict[str, list[str]], dict[str, str]]:
    # Read from checked-out working tree paths that mirror gh-pages content
    # (in this repo, gh-pages paths are available via CDN; here we map to same logical paths).
    # We use git ls-tree output saved from local origin refs by running commands externally.
    # Fallback to scanning known local assets folder if present.
    all_assets: list[str] = []
    local_assets = ROOT / "assets"
    if local_assets.exists():
        for f in local_assets.rglob("*"):
            if f.is_file():
                all_assets.append(f.relative_to(ROOT).as_posix())

    by_cat: dict[str, list[str]] = {}
    by_kind: dict[str, list[str]] = {"image": [], "video": []}
    by_name: dict[str, str] = {}

    for p in sorted(all_assets):
        parts = p.split("/")
        if len(parts) < 3:
            continue
        ext = Path(p).suffix.lower()
        kind = "video" if ext in VIDEO_EXT else "image"
        by_kind[kind].append(p)
        by_name[Path(p).name.lower()] = p
        if parts[0] == "assets" and parts[1] != "images":
            by_cat.setdefault(parts[1], []).append(p)

    return all_assets, by_cat, by_kind, by_name


def pick_asset(
    src_url: str,
    category: str,
    by_cat: dict[str, list[str]],
    by_kind: dict[str, list[str]],
    by_name: dict[str, str],
    rr_idx: dict[str, int],
) -> str | None:
    src_path = urlparse(src_url).path
    src_name = Path(src_path).name.lower()
    src_tokens = slug_tokens(Path(src_name).stem)
    kind = "video" if is_video(src_url) else "image"

    # 1) exact filename match anywhere
    if src_name in by_name:
        return by_name[src_name]

    # 2) same numeric id in filename
    ids = set(ID_RE.findall(src_name))
    if ids:
        candidates = by_cat.get(category, []) + by_kind[kind]
        for p in candidates:
            if ids & set(ID_RE.findall(Path(p).name)):
                return p

    # 3) token similarity in same category
    cat_candidates = [p for p in by_cat.get(category, []) if ("video" if Path(p).suffix.lower() in VIDEO_EXT else "image") == kind]
    best = None
    best_score = 0
    for p in cat_candidates:
        score = len(src_tokens & slug_tokens(Path(p).stem))
        if score > best_score:
            best_score = score
            best = p
    if best is not None and best_score > 0:
        return best

    # 4) round-robin fallback in same category, then global by kind
    if cat_candidates:
        i = rr_idx[kind] % len(cat_candidates)
        rr_idx[kind] += 1
        return cat_candidates[i]

    global_candidates = by_kind[kind]
    if global_candidates:
        i = rr_idx[kind] % len(global_candidates)
        rr_idx[kind] += 1
        return global_candidates[i]
    return None


def remap_sql() -> tuple[int, int]:
    text = SQL_PATH.read_text(encoding="utf-8")
    ru_map = build_ru_media_map()
    _, by_cat, by_kind, by_name = list_gh_assets()

    chunks = text.split("INSERT INTO guides")
    out = [chunks[0]]
    replaced = 0
    kept = 0

    for chunk in chunks[1:]:
        block = "INSERT INTO guides" + chunk
        m = re.search(r"VALUES\s*\(\s*'((?:[^']|'')*)'\s*,\s*'((?:[^']|'')*)'", block, re.S)
        key = m.group(1).replace("''", "'") if m else ""
        category = m.group(2).replace("''", "'") if m else ""

        source_urls = ru_map.get(key, [])
        source_pos = {"image": 0, "video": 0}
        rr_idx = {"image": 0, "video": 0}

        lines = block.splitlines(keepends=True)
        new_lines = []
        for line in lines:
            def repl(mu: re.Match[str]) -> str:
                nonlocal replaced, kept
                old = mu.group(0)
                if not MEDIA_URL_RE.search(old):
                    return old

                kind = "video" if is_video(old, line) else "image"
                src_candidates = [u for u in source_urls if is_video(u) == (kind == "video")]
                src = None
                idx = source_pos[kind]
                if idx < len(src_candidates):
                    src = src_candidates[idx]
                    source_pos[kind] += 1
                elif src_candidates:
                    src = src_candidates[-1]

                if src is None:
                    kept += 1
                    return old

                picked = pick_asset(src, category, by_cat, by_kind, by_name, rr_idx)
                if not picked:
                    kept += 1
                    return old

                new_url = f"https://cdn.jsdelivr.net/gh/Nihronick/blackrose@gh-pages/{picked}"
                if new_url != old:
                    replaced += 1
                return new_url

            new_lines.append(URL_RE.sub(repl, line))
        out.append("".join(new_lines))

    SQL_PATH.write_text("".join(out), encoding="utf-8")
    return replaced, kept


if __name__ == "__main__":
    replaced, kept = remap_sql()
    print(f"REPLACED {replaced}")
    print(f"KEPT {kept}")
