from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
GUIDES_ROOT = ROOT / "assets" / "media" / "guides"
MAX_BYTES = 50 * 1024 * 1024
TARGETS = (".mp4", ".mov", ".webm", ".m4v", ".avi", ".mkv")


def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def compress(src: Path) -> None:
    tmp = src.with_suffix(src.suffix + ".tmp.mp4")
    passes = [
        (960, 34),
        (854, 36),
        (720, 38),
        (640, 40),
    ]

    best = None
    for width, crf in passes:
        if tmp.exists():
            tmp.unlink()
        vf = f"scale='min({width},iw)':-2"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-an",
            "-movflags",
            "+faststart",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            str(tmp),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        best = tmp.stat().st_size
        if best <= MAX_BYTES:
            src.unlink()
            tmp.rename(src)
            print(f"OK   {size_mb(src):6.2f} MB  {src.relative_to(ROOT).as_posix()}")
            return

    if best is not None:
        src.unlink()
        tmp.rename(src)
        print(f"WARN {size_mb(src):6.2f} MB  {src.relative_to(ROOT).as_posix()}  (still above limit)")


def main() -> int:
    videos = [p for p in GUIDES_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in TARGETS]
    oversized = [p for p in videos if p.stat().st_size > MAX_BYTES]

    print(f"Total guide videos: {len(videos)}")
    print(f"Over 50 MB: {len(oversized)}")

    for p in sorted(oversized, key=lambda x: x.stat().st_size, reverse=True):
        print(f"SRC {size_mb(p):6.2f} MB  {p.relative_to(ROOT).as_posix()}")
        compress(p)

    remaining = [p for p in videos if p.stat().st_size > MAX_BYTES]
    print(f"Remaining over limit: {len(remaining)}")
    for p in sorted(remaining, key=lambda x: x.stat().st_size, reverse=True):
        print(f"LEFT {size_mb(p):6.2f} MB  {p.relative_to(ROOT).as_posix()}")

    return 0 if not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main())
