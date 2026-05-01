import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
RU_DIR = ROOT / "guides" / "ru"
MEDIA_DIR = ROOT / "assets" / "images" / "slayerpedia"

MAIN_PREFIX = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main/"
GHP_PREFIX = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@gh-pages/"
DISCORD_ASSET_RE = re.compile(
    r"https://cdn\.jsdelivr\.net/gh/Nihronick/blackrose@(?:main|gh-pages)/(assets/images/slayerpedia/(?:image|video)/discord-\d+\.(?:png|jpg|jpeg|gif|webp|mp4|mov|webm))"
)
URL_RE = re.compile(r"https?://[^\s)\]\"']+")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build_hash_index() -> dict[tuple[str, str], Path]:
    index: dict[tuple[str, str], Path] = {}
    for p in MEDIA_DIR.rglob("*.*"):
        if not p.is_file():
            continue
        if p.name.startswith("discord-"):
            continue
        key = (p.suffix.lower(), sha256(p))
        index.setdefault(key, p)
    return index


def build_discord_to_canonical() -> dict[str, str]:
    canon_idx = build_hash_index()
    mapping: dict[str, str] = {}
    for p in MEDIA_DIR.rglob("discord-*.*"):
        if not p.is_file():
            continue
        key = (p.suffix.lower(), sha256(p))
        hit = canon_idx.get(key)
        if not hit:
            continue
        rel = hit.relative_to(ROOT).as_posix()
        mapping[p.name] = f"{GHP_PREFIX}{rel}"
    return mapping


def normalize_url(url: str, discord_map: dict[str, str]) -> str:
    m = DISCORD_ASSET_RE.match(url)
    if m:
        filename = Path(m.group(1)).name
        if filename in discord_map:
            return discord_map[filename]
        return url
    if url.startswith(MAIN_PREFIX + "assets/"):
        return url.replace(MAIN_PREFIX, GHP_PREFIX, 1)
    return url


def main() -> None:
    discord_map = build_discord_to_canonical()
    changed_files = 0
    replaced = 0

    for md in RU_DIR.rglob("*.md"):
        raw = md.read_text(encoding="utf-8", errors="ignore")
        changed = False

        def repl(m: re.Match[str]) -> str:
            nonlocal changed, replaced
            url = m.group(0)
            n = normalize_url(url, discord_map)
            if n != url:
                changed = True
                replaced += 1
            return n

        out = URL_RE.sub(repl, raw)
        if changed and out != raw:
            md.write_text(out, encoding="utf-8")
            changed_files += 1

    print(f"Discord canonical mappings: {len(discord_map)}")
    print(f"RU files changed: {changed_files}")
    print(f"URLs replaced: {replaced}")


if __name__ == "__main__":
    main()
