from pathlib import Path
import re
import csv

ROOT = Path("guides/ru/Beginner-guide")
OUT_CSV = Path("scripts/beginner_media_drop_plan.csv")
OUT_TXT = Path("scripts/beginner_media_drop_plan.txt")
BASE_TARGET = Path("assets/media/guides/Beginner-guide")

URL_RE = re.compile(r"https://[^\s)]+")


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def infer_ext(url: str) -> str:
    u = url.lower()
    if ".gif" in u:
        return "gif"
    if ".webp" in u:
        return "webp"
    if ".jpg" in u or ".jpeg" in u:
        return "jpg"
    if ".mp4" in u:
        return "mp4"
    if ".webm" in u:
        return "webm"
    if ".mov" in u:
        return "mov"
    return "png"


def is_media(url: str) -> bool:
    media_hosts = (
        "cdn.discordapp.com",
        "media.discordapp.net",
        "cdn.jsdelivr.net",
    )
    return any(h in url for h in media_hosts)


rows = []
for md in sorted(ROOT.glob("*.md")):
    guide_slug = slugify(md.stem)
    target_dir = BASE_TARGET / guide_slug
    target_dir.mkdir(parents=True, exist_ok=True)

    content = md.read_text(encoding="utf-8")
    urls = [u for u in URL_RE.findall(content) if is_media(u)]

    for i, url in enumerate(urls, start=1):
        ext = infer_ext(url)
        target = target_dir / f"{i:02d}.{ext}"
        rows.append((md.name, i, url, str(target).replace('\\\\', '/')))

with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["guide_file", "index", "source_url", "target_path"])
    w.writerows(rows)

lines = []
current = None
for guide_file, idx, source_url, target_path in rows:
    if guide_file != current:
        current = guide_file
        lines.append(f"\n=== {guide_file} ===")
    lines.append(f"{idx:02d}. {target_path}")
    lines.append(f"    {source_url}")

OUT_TXT.write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")
print(f"WROTE {OUT_CSV} ({len(rows)} media rows)")
print(f"WROTE {OUT_TXT}")
