import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
EN_DIR = ROOT / "guides" / "en"
RU_DIR = ROOT / "guides" / "ru"
SLAYERPEDIA_DIR = ROOT / "assets" / "images" / "slayerpedia"
SLAYER_IMAGE_DIR = SLAYERPEDIA_DIR / "image"
SLAYER_VIDEO_DIR = SLAYERPEDIA_DIR / "video"
ICONS_DISCORD_DIR = ROOT / "assets" / "images" / "icons" / "discord_migrated"

CDN_BASE = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main"

URL_RE = re.compile(r"https?://[^\s)\]\">]+")
ATTACH_RE = re.compile(
    r"^https?://(?:cdn|media)\.discordapp\.(?:com|net)/attachments/(\d+)/(\d+)/([^/?#]+)",
    re.IGNORECASE,
)
EMOJI_RE = re.compile(
    r"^https?://(?:cdn\.)?discordapp\.com/emojis/(\d+)\.(\w+)",
    re.IGNORECASE,
)
NUM_ID_RE = re.compile(r"\d{10,}")

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


@dataclass
class MediaItem:
    source_url: str
    source_url_no_query: str
    source_id: str
    guide_slug: str
    kind: str  # image|video|icon
    filename_hint: str
    dest_rel: Path


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "guide"


def detect_kind(filename: str, fallback_video: bool = False) -> str:
    ext = Path(filename).suffix.lower()
    if ext in VIDEO_EXT or fallback_video:
        return "video"
    if ext in IMAGE_EXT:
        return "image"
    return "image"


def parse_media_items() -> List[MediaItem]:
    items: List[MediaItem] = []
    seen: set[str] = set()

    for md in EN_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        guide_slug = slugify(md.stem)
        urls = URL_RE.findall(text)
        for u in urls:
            u_no_q = clean_url(u)
            if u_no_q in seen:
                continue

            m_att = ATTACH_RE.match(u_no_q)
            if m_att:
                _, attachment_id, filename = m_att.groups()
                kind = detect_kind(filename)
                if kind == "video":
                    dest_rel = Path("assets/images/slayerpedia/video") / f"{guide_slug}__{attachment_id}.mp4"
                else:
                    ext = Path(filename).suffix.lower()
                    if ext in {".jpg", ".jpeg", ".png", ".webp"}:
                        ext = ".webp"
                    dest_rel = Path("assets/images/slayerpedia/image") / f"{guide_slug}__{attachment_id}{ext}"
                items.append(
                    MediaItem(
                        source_url=u,
                        source_url_no_query=u_no_q,
                        source_id=attachment_id,
                        guide_slug=guide_slug,
                        kind=kind,
                        filename_hint=filename,
                        dest_rel=dest_rel,
                    )
                )
                seen.add(u_no_q)
                continue

            m_emoji = EMOJI_RE.match(u_no_q)
            if m_emoji:
                emoji_id, ext = m_emoji.groups()
                ext = ext.lower()
                out_ext = ".gif" if ext == "gif" else ".webp"
                dest_rel = Path("assets/images/icons/discord_migrated") / f"{emoji_id}{out_ext}"
                items.append(
                    MediaItem(
                        source_url=u,
                        source_url_no_query=u_no_q,
                        source_id=emoji_id,
                        guide_slug=guide_slug,
                        kind="icon",
                        filename_hint=f"{emoji_id}.{ext}",
                        dest_rel=dest_rel,
                    )
                )
                seen.add(u_no_q)
                continue
    return items


def download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    candidates = [url]
    no_q = clean_url(url)
    if no_q not in candidates:
        candidates.append(no_q)
    if "cdn.discordapp.com/attachments/" in no_q:
        media_alt = no_q.replace("cdn.discordapp.com", "media.discordapp.net")
        if media_alt not in candidates:
            candidates.append(media_alt)

    last_err: Optional[Exception] = None
    headers = {"User-Agent": "Mozilla/5.0"}
    for candidate in candidates:
        try:
            with requests.get(candidate, stream=True, timeout=90, headers=headers) as r:
                r.raise_for_status()
                with open(target, "wb") as f:
                    for chunk in r.iter_content(1024 * 128):
                        if chunk:
                            f.write(chunk)
                return
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("Download failed for unknown reason")


def optimize_image(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    ext = dest.suffix.lower()
    if ext == ".gif":
        shutil.copy2(src, dest)
        return

    with Image.open(src) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.save(dest, format="WEBP", quality=82, method=6)


def optimize_video(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-an",
        "-vf",
        "scale='min(1920,iw)':-2",
        "-movflags",
        "+faststart",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "28",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def replace_ru_urls(id_to_cdn: Dict[str, str]) -> Tuple[int, int]:
    files_changed = 0
    urls_replaced = 0
    for md in RU_DIR.rglob("*.md"):
        raw = md.read_text(encoding="utf-8", errors="ignore")
        changed = False

        def repl(match: re.Match[str]) -> str:
            nonlocal changed, urls_replaced
            url = match.group(0)
            for n in NUM_ID_RE.findall(url):
                if n in id_to_cdn:
                    changed = True
                    urls_replaced += 1
                    return id_to_cdn[n]
            return url

        updated = URL_RE.sub(repl, raw)
        if changed and updated != raw:
            md.write_text(updated, encoding="utf-8")
            files_changed += 1
    return files_changed, urls_replaced


def run(clean_assets: bool = True) -> None:
    items = parse_media_items()
    if not items:
        raise RuntimeError("No Discord media links found in guides/en")

    if clean_assets:
        shutil.rmtree(SLAYERPEDIA_DIR, ignore_errors=True)
        SLAYER_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        SLAYER_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    ICONS_DISCORD_DIR.mkdir(parents=True, exist_ok=True)

    tmp_dir = ROOT / "temp_media" / "discord_import_tmp"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    id_to_cdn: Dict[str, str] = {}
    ok = 0
    fail = 0

    for i, item in enumerate(items, start=1):
        tmp_src = tmp_dir / f"{i}_{Path(item.filename_hint).name}"
        dest_abs = ROOT / item.dest_rel
        try:
            download_file(item.source_url, tmp_src)
            if item.kind == "video":
                optimize_video(tmp_src, dest_abs)
            else:
                optimize_image(tmp_src, dest_abs)
            id_to_cdn[item.source_id] = f"{CDN_BASE}/{item.dest_rel.as_posix()}"
            ok += 1
        except Exception:
            fail += 1

    files_changed, urls_replaced = replace_ru_urls(id_to_cdn)

    print(f"Media discovered: {len(items)}")
    print(f"Imported ok: {ok}")
    print(f"Imported failed: {fail}")
    print(f"RU files changed: {files_changed}")
    print(f"RU URLs replaced: {urls_replaced}")
    print(f"ID->CDN entries: {len(id_to_cdn)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Discord media, optimize, and rewrite guides/ru URLs.")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean assets/images/slayerpedia before import")
    args = parser.parse_args()
    run(clean_assets=not args.no_clean)


if __name__ == "__main__":
    main()
