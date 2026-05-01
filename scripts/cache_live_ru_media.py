import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
RU_DIR = ROOT / "guides" / "ru"
OUT_DIR = ROOT / "assets" / "images" / "slayerpedia"
OUT_IMG = OUT_DIR / "image"
OUT_VID = OUT_DIR / "video"

CDN_BASE = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main"

URL_RE = re.compile(r"https?://[^\s)\]\"']+")
ATT_RE = re.compile(
    r"^https?://(?:cdn|media)\.discordapp\.(?:com|net)/attachments/(\d+)/(\d+)/([^/?#]+)",
    re.IGNORECASE,
)
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


@dataclass
class Item:
    source_url: str
    attachment_id: str
    filename: str
    guide_slug: str
    guide_category: str
    kind: str  # image|video


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def guide_slug(md: Path) -> str:
    return f"{norm(md.parent.name)}-{norm(md.stem)}"


def detect_kind(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return "video" if ext in VIDEO_EXT else "image"


def clean_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


def collect_items(category_filter: set[str] | None = None) -> List[Item]:
    items: List[Item] = []
    seen: set[str] = set()
    for md in RU_DIR.rglob("*.md"):
        cat = norm(md.parent.name)
        if category_filter and cat not in category_filter:
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        slug = guide_slug(md)
        for u in URL_RE.findall(text):
            m = ATT_RE.match(u)
            if not m:
                continue
            _, attachment_id, filename = m.groups()
            key = attachment_id
            if key in seen:
                continue
            seen.add(key)
            items.append(
                Item(
                    source_url=u,
                    attachment_id=attachment_id,
                    filename=filename,
                    guide_slug=slug,
                    guide_category=cat,
                    kind=detect_kind(filename),
                )
            )
    return items


def download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    candidates = [url]
    no_q = clean_url(url)
    if no_q not in candidates:
        candidates.append(no_q)
    if "cdn.discordapp.com/attachments/" in no_q:
        alt = no_q.replace("cdn.discordapp.com", "media.discordapp.net")
        if alt not in candidates:
            candidates.append(alt)

    headers = {"User-Agent": "Mozilla/5.0"}
    last_err: Exception | None = None
    for c in candidates:
        try:
            with requests.get(c, stream=True, timeout=90, headers=headers) as r:
                r.raise_for_status()
                with target.open("wb") as f:
                    for chunk in r.iter_content(1024 * 128):
                        if chunk:
                            f.write(chunk)
                return
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise RuntimeError("download failed")


def optimize_image(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix.lower() == ".gif":
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
        "-an",  # remove audio
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


def process(items: List[Item], clean: bool, max_items: int = 0) -> Dict[str, str]:
    if clean:
        OUT_IMG.mkdir(parents=True, exist_ok=True)
        OUT_VID.mkdir(parents=True, exist_ok=True)

    tmp = ROOT / "temp_media" / "ru_live_cache_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)

    id_to_cdn: Dict[str, str] = {}
    processed = 0
    for i, item in enumerate(items, start=1):
        if max_items and processed >= max_items:
            break
        tmp_file = tmp / f"{i}_{Path(item.filename).name}"
        try:
            if item.kind == "video":
                dest_rel = Path("assets/images/slayerpedia/video") / f"{item.guide_slug}__{item.attachment_id}.mp4"
                dest_abs = ROOT / dest_rel
                if not dest_abs.exists():
                    download_file(item.source_url, tmp_file)
                    optimize_video(tmp_file, dest_abs)
            else:
                ext = Path(item.filename).suffix.lower()
                if ext in {".jpg", ".jpeg", ".png", ".webp"}:
                    ext = ".webp"
                dest_rel = Path("assets/images/slayerpedia/image") / f"{item.guide_slug}__{item.attachment_id}{ext}"
                dest_abs = ROOT / dest_rel
                if not dest_abs.exists():
                    download_file(item.source_url, tmp_file)
                    optimize_image(tmp_file, dest_abs)
            id_to_cdn[item.attachment_id] = f"{CDN_BASE}/{dest_rel.as_posix()}"
            processed += 1
        except Exception:
            continue
    return id_to_cdn


def rewrite_ru(id_to_cdn: Dict[str, str]) -> tuple[int, int]:
    changed_files = 0
    replaced = 0
    for md in RU_DIR.rglob("*.md"):
        raw = md.read_text(encoding="utf-8", errors="ignore")
        changed = False

        def repl(m: re.Match[str]) -> str:
            nonlocal changed, replaced
            u = m.group(0)
            am = ATT_RE.match(u)
            if not am:
                return u
            aid = am.group(2)
            new = id_to_cdn.get(aid)
            if new:
                changed = True
                replaced += 1
                return new
            return u

        out = URL_RE.sub(repl, raw)
        if changed and out != raw:
            md.write_text(out, encoding="utf-8")
            changed_files += 1
    return changed_files, replaced


def main() -> None:
    parser = argparse.ArgumentParser(description="Cache live Discord media from guides/ru and rewrite to repo CDN.")
    parser.add_argument("--clean", action="store_true", help="Do not purge old files; just ensure output dirs exist")
    parser.add_argument("--max-items", type=int, default=0, help="Process at most N attachment URLs")
    parser.add_argument("--category", action="append", default=[], help="Filter by RU category (repeatable)")
    args = parser.parse_args()

    category_filter = {norm(x) for x in args.category if x.strip()} or None
    items = collect_items(category_filter=category_filter)
    id_to_cdn = process(items, clean=args.clean, max_items=max(0, args.max_items))
    files_changed, urls_replaced = rewrite_ru(id_to_cdn)

    print(f"Attachment URLs found: {len(items)}")
    print(f"Cached media entries: {len(id_to_cdn)}")
    print(f"RU files changed: {files_changed}")
    print(f"RU URLs replaced: {urls_replaced}")


if __name__ == "__main__":
    main()
