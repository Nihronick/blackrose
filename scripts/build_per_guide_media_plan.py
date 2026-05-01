from pathlib import Path
import csv
import re
from urllib.parse import urlparse

GUIDES_ROOT = Path("guides/ru")
MEDIA_ROOT = Path("assets/media/by-guide")
OUT_CSV = Path("scripts/media_drop_plan_by_guide.csv")
OUT_TXT = Path("scripts/media_drop_plan_by_guide.txt")

URL_RE = re.compile(r"https://[^\s)]+")
MEDIA_EXT_RE = re.compile(r"\.(png|jpg|jpeg|webp|gif|mp4|webm|mov)(?:\?|$)", re.IGNORECASE)


def slugify(text: str) -> str:
    t = text.lower()
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def is_media_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if not (
        "discordapp.com" in host
        or "discordapp.net" in host
        or "jsdelivr.net" in host
        or "githubusercontent.com" in host
    ):
        return False
    return MEDIA_EXT_RE.search(url) is not None


def guess_ext(url: str) -> str:
    m = MEDIA_EXT_RE.search(url)
    if not m:
        return "bin"
    ext = m.group(1).lower()
    if ext == "jpeg":
        return "jpg"
    return ext


def source_id(url: str) -> str:
    """Try to extract stable id from URL path (Discord attachment/message id or emoji id)."""
    path_parts = [p for p in urlparse(url).path.split("/") if p]
    numeric = [p for p in path_parts if p.isdigit()]
    if numeric:
        return numeric[-1]

    tail = path_parts[-1] if path_parts else "file"
    tail = tail.split(".")[0]
    tail = slugify(tail)
    return tail or "file"


def classify_type(ext: str) -> str:
    if ext in {"mp4", "webm", "mov"}:
        return "video"
    if ext == "gif":
        return "gif"
    return "image"


def build_plan():
    rows = []

    for md in sorted(GUIDES_ROOT.rglob("*.md")):
        category = md.parent.name
        guide_name = md.stem
        guide_slug = slugify(guide_name)

        # Strictly separate folder per guide
        guide_dir = MEDIA_ROOT / category / guide_slug
        guide_dir.mkdir(parents=True, exist_ok=True)

        content = md.read_text(encoding="utf-8")
        urls = [u for u in URL_RE.findall(content) if is_media_url(u)]

        for idx, url in enumerate(urls, start=1):
            ext = guess_ext(url)
            typ = classify_type(ext)
            sid = source_id(url)
            # Order is fixed by appearance in guide text.
            filename = f"{idx:03d}_{typ}_{sid}.{ext}"
            rel_target = (guide_dir / filename).as_posix()
            rows.append(
                {
                    "guide_path": md.as_posix(),
                    "category": category,
                    "guide_slug": guide_slug,
                    "order": idx,
                    "type": typ,
                    "source_id": sid,
                    "source_url": url,
                    "target_path": rel_target,
                    "target_filename": filename,
                }
            )

    return rows


def write_outputs(rows):
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "guide_path",
                "category",
                "guide_slug",
                "order",
                "type",
                "source_id",
                "source_url",
                "target_path",
                "target_filename",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    lines = []
    current_guide = None
    for r in rows:
        if r["guide_path"] != current_guide:
            current_guide = r["guide_path"]
            lines.append("")
            lines.append(f"=== {current_guide} ===")
            lines.append(f"folder: {Path(r['target_path']).parent.as_posix()}")
        lines.append(f"{r['order']:03d} -> {r['target_filename']}")
        lines.append(f"source: {r['source_url']}")

    OUT_TXT.write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")


def main():
    rows = build_plan()
    write_outputs(rows)
    guide_count = len({r["guide_path"] for r in rows})
    print(f"WROTE {OUT_CSV.as_posix()} ({len(rows)} rows)")
    print(f"WROTE {OUT_TXT.as_posix()}")
    print(f"GUIDES_WITH_MEDIA {guide_count}")


if __name__ == "__main__":
    main()
