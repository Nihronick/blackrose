from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEXT_EXTS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".sh",
    ".ps1",
    ".sql",
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".env",
}
SKIP_DIRS = {
    ".git",
    ".agent",
    ".gemini",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "playwright-report",
    "test-results",
    "coverage",
    "__pycache__",
}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bA(KIA|SIA)[A-Z0-9]{16}\b")),
    ("Telegram bot token", re.compile(r"\b\d{8,}:[A-Za-z0-9_-]{35,}\b")),
    ("Private key block", re.compile(r"-----BEGIN [^-]+ PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}\b")),
]


@dataclass(frozen=True)
class Finding:
    kind: str
    path: Path
    line: int
    snippet: str


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            continue
        if path.suffix.lower() not in TEXT_EXTS and path.name != "LICENSE":
            continue
        files.append(path)
    return files


def scan_file(path: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(kind, path, line_number, line.strip()))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan the repo for likely exposed secrets or API tokens.")
    parser.add_argument("--root", default=str(ROOT), help="Repository root to scan.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = iter_text_files(root)
    findings: list[Finding] = []

    for path in files:
        findings.extend(scan_file(path))

    if not findings:
        print(f"No likely secrets found in {len(files)} text files.")
        return 0

    print(f"Found {len(findings)} potential secret match(es):")
    for finding in findings:
        rel = finding.path.relative_to(root).as_posix()
        print(f"- {finding.kind}: {rel}:{finding.line}")
        print(f"  {finding.snippet}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
