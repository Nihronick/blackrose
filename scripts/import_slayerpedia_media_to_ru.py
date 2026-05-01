import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SLAYERPEDIA_DIR = ROOT / "slayerpedia"
RU_DIR = ROOT / "guides" / "ru"
OUT_IMG = ROOT / "assets" / "images" / "slayerpedia" / "image"
OUT_VID = ROOT / "assets" / "images" / "slayerpedia" / "video"

CDN_BASE = "https://cdn.jsdelivr.net/gh/Nihronick/blackrose@main"

URL_RE = re.compile(r"https?://[^\s)\]\"']+")
ATT_RE = re.compile(
    r"^https?://(?:cdn|media)\.discordapp\.(?:com|net)/attachments/(\d+)/(\d+)/([^/?#]+)",
    re.IGNORECASE,
)

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def norm(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def clean_url(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}"


def ru_index() -> dict[tuple[str, str], Path]:
    idx: dict[tuple[str, str], Path] = {}
    for md in RU_DIR.rglob("*.md"):
        cat = norm(md.parent.name)
        stem = norm(md.stem)
        idx[(cat, stem)] = md
    return idx


def txt_to_ru(txt_file: Path, index: dict[tuple[str, str], Path]) -> Path | None:
    cat = norm(txt_file.parent.name)
    stem = norm(txt_file.stem)
    ru = index.get((cat, stem))
    if ru:
        return ru
    # fallback: tolerate underscore/space punctuation drift
    for (c, s), p in index.items():
        if c == cat and (s in stem or stem in s):
            return p
    return None


@dataclass
class Item:
    url: str
    channel_id: str
    attachment_id: str
    filename: str
    guide_slug: str
    kind: str


def detect_kind(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return "video" if ext in VIDEO_EXT else "image"


def collect_items() -> list[Item]:
    idx = ru_index()
    items: list[Item] = []
    seen: set[str] = set()

    for txt in SLAYERPEDIA_DIR.rglob("*.txt"):
        ru = txt_to_ru(txt, idx)
        if not ru:
            continue
        guide_slug = f"{norm(ru.parent.name)}-{norm(ru.stem)}"
        content = txt.read_text(encoding="utf-8", errors="ignore")
        for u in URL_RE.findall(content):
            m = ATT_RE.match(u)
            if not m:
                continue
            channel_id, attachment_id, filename = m.groups()
            if attachment_id in seen:
                continue
            seen.add(attachment_id)
            kind = detect_kind(filename)
            items.append(
                Item(
                    url=u,
                    channel_id=channel_id,
                    attachment_id=attachment_id,
                    filename=filename,
                    guide_slug=guide_slug,
                    kind=kind,
                )
            )
    return items


def download_candidates(url: str) -> list[str]:
    base = clean_url(url)
    out = [url]
    if base not in out:
        out.append(base)
    if "cdn.discordapp.com/attachments/" in base:
        alt = base.replace("cdn.discordapp.com", "media.discordapp.net")
        if alt not in out:
            out.append(alt)
    if "media.discordapp.net/attachments/" in base:
        alt = base.replace("media.discordapp.net", "cdn.discordapp.com")
        if alt not in out:
            out.append(alt)
    return out


def download(url: str, target: Path) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    for cand in download_candidates(url):
        try:
            with requests.get(cand, stream=True, timeout=60, headers=headers) as r:
                if r.status_code != 200:
                    continue
                with target.open("wb") as f:
                    for chunk in r.iter_content(1024 * 128):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception:
            continue
    return False


def optimize_image(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix.lower() == ".gif":
        shutil.copy2(src, dest)
        return
    with Image.open(src) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.save(dest, format="WEBP", quality=82, method=6)


def optimize_video(src: Path, dest: Path) -> bool:
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
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def process(items: list[Item], max_items: int = 0) -> tuple[dict[str, str], int]:
    temp_dir = ROOT / "temp_media" / "slayerpedia_tmp"
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    id_to_cdn: dict[str, str] = {}
    fallback_clean_links = 0
    done = 0

    for item in items:
        if max_items and done >= max_items:
            break

        if item.kind == "video":
            rel = Path("assets/images/slayerpedia/video") / f"{item.guide_slug}__{item.attachment_id}.mp4"
            out = ROOT / rel
        else:
            ext = Path(item.filename).suffix.lower()
            if ext in {".jpg", ".jpeg", ".png", ".webp"}:
                ext = ".webp"
            rel = Path("assets/images/slayerpedia/image") / f"{item.guide_slug}__{item.attachment_id}{ext}"
            out = ROOT / rel

        if out.exists():
            id_to_cdn[item.attachment_id] = f"{CDN_BASE}/{rel.as_posix()}"
            done += 1
            continue

        tmp = temp_dir / f"{item.attachment_id}_{Path(item.filename).name}"
        if not download(item.url, tmp):
            id_to_cdn[item.attachment_id] = clean_url(item.url)
            fallback_clean_links += 1
            done += 1
            continue

        if item.kind == "video":
            if not optimize_video(tmp, out):
                id_to_cdn[item.attachment_id] = clean_url(item.url)
                fallback_clean_links += 1
                done += 1
                continue
        else:
            optimize_image(tmp, out)

        id_to_cdn[item.attachment_id] = f"{CDN_BASE}/{rel.as_posix()}"
        done += 1

    return id_to_cdn, fallback_clean_links


def rewrite_ru(id_to_cdn: dict[str, str]) -> tuple[int, int, int]:
    changed_files = 0
    replaced_urls = 0
    fixed_link_artifacts = 0

    for md in RU_DIR.rglob("*.md"):
        raw = md.read_text(encoding="utf-8", errors="ignore")
        changed = False

        # Fix machine-translation artifact that appears in a few files.
        artifact_fixed = raw.replace(r"\n\n[Link:", "")
        if artifact_fixed != raw:
            fixed_link_artifacts += raw.count(r"\n\n[Link:")
            raw = artifact_fixed
            changed = True

        def repl(m: re.Match[str]) -> str:
            nonlocal changed, replaced_urls
            u = m.group(0)
            am = ATT_RE.match(u)
            if not am:
                return u
            aid = am.group(2)
            new = id_to_cdn.get(aid)
            if new and new != u:
                changed = True
                replaced_urls += 1
                return new
            return u

        out = URL_RE.sub(repl, raw)
        if changed and out != md.read_text(encoding="utf-8", errors="ignore"):
            md.write_text(out.rstrip() + "\n", encoding="utf-8")
            changed_files += 1

    return changed_files, replaced_urls, fixed_link_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Import media URLs from slayerpedia/*.txt and rewrite RU guides to canonical CDN links.")
    parser.add_argument("--max-items", type=int, default=0, help="Process at most N media attachments")
    args = parser.parse_args()

    items = collect_items()
    id_to_cdn, fallback_clean_links = process(items, max_items=max(0, args.max_items))
    changed_files, replaced_urls, fixed_artifacts = rewrite_ru(id_to_cdn)

    print(f"Slayerpedia attachment URLs found: {len(items)}")
    print(f"Resolvable attachment IDs: {len(id_to_cdn)}")
    print(f"Fallback clean attachment links: {fallback_clean_links}")
    print(f"RU files changed: {changed_files}")
    print(f"RU URLs replaced: {replaced_urls}")
    print(f"Artifact fixes applied: {fixed_artifacts}")


if __name__ == "__main__":
    main()
