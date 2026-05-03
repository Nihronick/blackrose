from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
GUIDES_ROOT = ROOT / "backend" / "assets" / "media" / "guides" # Adjusted for current backend-centric structure
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
# ... (keeping it simple)
