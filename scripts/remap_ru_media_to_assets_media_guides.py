from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, urlparse


ROOT = Path.cwd()
if not (ROOT / "guides" / "ru").exists():
    ROOT = Path(__file__).resolve().parent.parent
RU_DIR = ROOT / "guides" / "ru"
MEDIA_ROOT = ROOT / "assets" / "media" / "guides"
CDN_PREFIX = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main/"

URL_RE = re.compile(r"https?://[^\s)\]\"']+")
TARGET_HOST_RE = re.compile(
    r"^(?:cdn\.discordapp\.com|media\.discordapp\.net|raw\.githubusercontent\.com|cdn\.jsdelivr\.net)$",
    re.I,
)

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def slug(s: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "_", s.lower())
    return re.sub(r"_+", "_", out).strip("_")


def path_to_cdn(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return CDN_PREFIX + quote(rel, safe="/")


def media_type(ext: str) -> str:
    ext = ext.lower()
    if ext in VIDEO_EXT:
        return "video"
    if ext in IMAGE_EXT:
        return "image"
    return "other"


def build_global_name_index() -> dict[str, list[Path]]:
    idx: dict[str, list[Path]] = {}
    if not MEDIA_ROOT.exists():
        return idx
    for p in MEDIA_ROOT.rglob("*"):
        if not p.is_file():
            continue
        idx.setdefault(p.name.lower(), []).append(p)
    return idx


def candidate_guide_dirs(md: Path) -> list[Path]:
    cat = md.parent.name
    stem = slug(md.stem)
    base = MEDIA_ROOT / cat
    out: list[Path] = []
    if not base.exists():
        return out

    direct = base / stem
    if direct.exists() and direct.is_dir():
        out.append(direct)

    # fallback: choose dirs by token overlap
    stem_tokens = set(stem.split("_"))
    scored: list[tuple[int, Path]] = []
    for d in base.iterdir():
        if not d.is_dir():
            continue
        dtok = set(slug(d.name).split("_"))
        score = len(stem_tokens & dtok)
        if score > 0:
            scored.append((score, d))
    for _, d in sorted(scored, key=lambda x: (-x[0], x[1].name)):
        if d not in out:
            out.append(d)

    return out


def build_local_name_index(dirs: list[Path]) -> dict[str, list[Path]]:
    idx: dict[str, list[Path]] = {}
    for d in dirs:
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            idx.setdefault(p.name.lower(), []).append(p)
    return idx


def normalize_if_target(url: str, local_idx: dict[str, list[Path]], global_idx: dict[str, list[Path]]) -> str:
    try:
        parsed = urlparse(url)
    except Exception:
        return url

    host = parsed.netloc.lower()
    if not TARGET_HOST_RE.match(host):
        return url

    # keep already canonical main assets/media links
    if "cdn.jsdelivr.net" in host and "/gh/Nihronick/blackrose@main/assets/media/guides/" in parsed.path:
        return url

    basename = Path(parsed.path).name
    if not basename:
        return url

    ext = Path(basename).suffix.lower()
    want_type = media_type(ext)

    # 1) same-guide exact filename match
    local_hits = [p for p in local_idx.get(basename.lower(), []) if media_type(p.suffix) == want_type or want_type == "other"]
    if len(local_hits) == 1:
        return path_to_cdn(local_hits[0])

    # 2) unique global exact filename match
    global_hits = [p for p in global_idx.get(basename.lower(), []) if media_type(p.suffix) == want_type or want_type == "other"]
    if len(global_hits) == 1:
        return path_to_cdn(global_hits[0])

    return url


def main() -> None:
    global_idx = build_global_name_index()

    files_changed = 0
    urls_changed = 0

    for md in sorted(RU_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="ignore")

        local_dirs = candidate_guide_dirs(md)
        local_idx = build_local_name_index(local_dirs)

        changed = False

        def repl(m: re.Match[str]) -> str:
            nonlocal changed, urls_changed
            old = m.group(0)
            new = normalize_if_target(old, local_idx, global_idx)
            if new != old:
                changed = True
                urls_changed += 1
            return new

        out = URL_RE.sub(repl, text)
        if changed and out != text:
            md.write_text(out, encoding="utf-8")
            files_changed += 1

    print(f"RU files changed: {files_changed}")
    print(f"URLs remapped: {urls_changed}")


if __name__ == "__main__":
    main()
