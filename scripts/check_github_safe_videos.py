from __future__ import annotations

from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIRS = [
    ROOT / "assets" / "images" / "slayerpedia" / "video",
    ROOT / "assets" / "media" / "guides",
]
MAX_SIZE = 50 * 1024 * 1024  # 50 MB
TARGET_SIZE = 45 * 1024 * 1024
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv"}


def iter_videos() -> list[Path]:
    items: list[Path] = []
    for base in VIDEO_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
                items.append(p)
    return items


def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def ffmpeg_compress(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src),
        "-an",
        "-movflags",
        "+faststart",
        "-vf",
        "scale='min(1280,iw)':-2",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "30",
        str(dst),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or compress videos to stay under GitHub/jsDelivr limits.")
    parser.add_argument("--compress", action="store_true", help="Re-encode files over 50 MB down to a safer target size.")
    args = parser.parse_args()

    videos = iter_videos()
    over_limit: list[Path] = []

    for path in sorted(videos):
        mb = size_mb(path)
        if mb > 50:
            over_limit.append(path)
        print(f"{mb:8.2f} MB  {path.relative_to(ROOT).as_posix()}")

    print(f"\nTotal videos: {len(videos)}")
    print(f"Over 50 MB: {len(over_limit)}")

    if not args.compress:
        return 0 if not over_limit else 1

    if not over_limit:
        print("Nothing to compress.")
        return 0

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found in PATH.")
        return 2

    for src in over_limit:
        tmp = src.with_suffix(".tmp.mp4")
        print(f"Compressing {src.name}...")
        ffmpeg_compress(src, tmp)
        if tmp.stat().st_size > TARGET_SIZE:
            print(f"Warning: {src.name} still above target after compression.")
        tmp.replace(src)

    print("Compression complete.")
    return 0


if __name__ == "__main__":
    import shutil
    raise SystemExit(main())
