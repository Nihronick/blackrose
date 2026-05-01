from pathlib import Path
from urllib.parse import urlparse, unquote
import csv
import re

GUIDE_DIR = Path("guides/ru/Beginner-guide")
MEDIA_ROOT = Path("assets/media/guides/Beginner-guide")
OUT_CSV = Path("scripts/beginner_download_friendly_plan.csv")
OUT_TXT = Path("scripts/beginner_download_friendly_plan.txt")

URL_RE = re.compile(r"https://[^\s)]+")


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def is_media(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if not ("discordapp.com" in host or "discordapp.net" in host or "jsdelivr.net" in host):
        return False
    u = url.lower()
    return any(x in u for x in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mov"]) 


def ext_from_url(url: str) -> str:
    u = url.lower()
    for ext in ["png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "mov"]:
        if f".{ext}" in u:
            return "jpg" if ext == "jpeg" else ext
    return "bin"


def downloaded_name(url: str) -> str:
    # Browser usually suggests basename from path.
    parsed = urlparse(url)
    base = unquote(Path(parsed.path).name)
    if base and "." in base:
        return base

    # Fallback for uncommon cases.
    ext = ext_from_url(url)
    parts = [p for p in parsed.path.split("/") if p]
    nums = [p for p in parts if p.isdigit()]
    if nums:
        return f"{nums[-1]}.{ext}"
    return f"file.{ext}"


rows = []
for md in sorted(GUIDE_DIR.glob("*.md")):
    guide_slug = slugify(md.stem)
    folder = MEDIA_ROOT / guide_slug
    folder.mkdir(parents=True, exist_ok=True)

    content = md.read_text(encoding="utf-8")
    urls = [u for u in URL_RE.findall(content) if is_media(u)]

    seen = set()
    # Deduplicate same URL within one guide (e.g. repeated emoji links)
    for order, url in enumerate(urls, start=1):
        if url in seen:
            continue
        seen.add(url)

        fname = downloaded_name(url)
        target = folder / fname

        rows.append(
            {
                "guide_file": md.name,
                "guide_slug": guide_slug,
                "order_in_text": order,
                "source_url": url,
                "save_to_folder": folder.as_posix(),
                "save_as_filename": fname,
                "target_path": target.as_posix(),
            }
        )

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "guide_file",
            "guide_slug",
            "order_in_text",
            "source_url",
            "save_to_folder",
            "save_as_filename",
            "target_path",
        ],
    )
    w.writeheader()
    w.writerows(rows)

lines = []
current = None
for r in rows:
    if r["guide_file"] != current:
        current = r["guide_file"]
        lines.append("")
        lines.append(f"=== {r['guide_file']} ===")
        lines.append(f"folder: {r['save_to_folder']}")
    lines.append(f"{int(r['order_in_text']):03d}. {r['save_as_filename']}")
    lines.append(f"    {r['source_url']}")

OUT_TXT.write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")

print(f"WROTE {OUT_CSV.as_posix()} with {len(rows)} unique media rows")
print(f"WROTE {OUT_TXT.as_posix()}")
