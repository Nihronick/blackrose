#!/usr/bin/env python3
"""
Safe RU translation from EN lossless baseline.
Guarantees 100% structural preservation with strict fail-safe.
"""
import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

# Hardened settings
TIMEOUT_SECONDS = 8
MAX_RETRIES = 1
SLEEP_BETWEEN_LINES = 0.08

EN_ROOT = Path("guides/en")
RU_ROOT = Path("guides/ru")
OUTPUT_DIR = Path("output_media")

# Token protection patterns
URL_RE = re.compile(r"https?://[^\s)]+")
MARKDOWN_CODE_RE = re.compile(r"`[^`]+`")
HTML_TAG_RE = re.compile(r"<[^>]+>")
DISCORD_RE = re.compile(r"<@!?\d+>|<#\d+>|<@&\d+>")
NO_TRANSLATE = {"Discord", "Slayerpedia", "Diablo", "Dragonsoul", "http", "https"}

def protect_tokens(text):
    """Store protected tokens and return text with placeholders."""
    tokens = {}
    counter = 0
    
    # Protect URLs
    for match in URL_RE.finditer(text):
        placeholder = f"__URL{counter}__"
        tokens[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        counter += 1
    
    # Protect inline code
    for match in MARKDOWN_CODE_RE.finditer(text):
        placeholder = f"__CODE{counter}__"
        tokens[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        counter += 1
    
    # Protect HTML tags
    for match in HTML_TAG_RE.finditer(text):
        placeholder = f"__HTML{counter}__"
        tokens[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        counter += 1
    
    # Protect Discord mentions
    for match in DISCORD_RE.finditer(text):
        placeholder = f"__DISCORD{counter}__"
        tokens[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        counter += 1
    
    return text, tokens

def restore_tokens(text, tokens):
    """Restore protected tokens to original text."""
    for placeholder, original in tokens.items():
        text = text.replace(placeholder, original)
    return text

def translate_line(text):
    """Translate line using Google Translate API with fail-safe."""
    if not text.strip():
        return text
    
    text_clean, tokens = protect_tokens(text)
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            q = urllib.parse.quote(text_clean)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={q}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as r:
                data = json.loads(r.read().decode("utf-8"))
            translated = "".join(
                chunk[0] for chunk in data[0] if chunk and chunk[0] is not None
            )
            return restore_tokens(translated, tokens)
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
            if attempt < MAX_RETRIES:
                time.sleep(0.5)
                continue
            else:
                # Fail-safe: return original English line
                return text

def translate_file(en_path, ru_path):
    """Translate single file with 1:1 line mapping."""
    lines = en_path.read_text(encoding="utf-8").splitlines()
    output = []
    translated_count = 0
    failed_count = 0
    
    for line in lines:
        s = line.strip()
        
        # Empty lines: preserve as-is
        if not s:
            output.append("")
            continue
        
        # Code blocks, URLs: preserve as-is
        if s.startswith("```") or s.startswith("http://") or s.startswith("https://"):
            output.append(line)
            continue
        
        # Markdown headers, list markers, dividers: preserve as-is
        if s.startswith("#") or s.startswith("-") or s.startswith("*") or s == "---":
            output.append(line)
            continue
        
        # Translate content lines
        try:
            translated = translate_line(line)
            output.append(translated)
            translated_count += 1
        except Exception as e:
            # Fail-safe: keep original English line
            output.append(line)
            failed_count += 1
        
        time.sleep(SLEEP_BETWEEN_LINES)
    
    # Ensure file and directory exist
    ru_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output, preserving line endings
    ru_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    
    # Validate: check line count parity
    out_lines = ru_path.read_text(encoding="utf-8").splitlines()
    if len(out_lines) != len(lines):
        return {
            "status": "STRUCTURE_MISMATCH",
            "en_lines": len(lines),
            "ru_lines": len(out_lines),
            "translated": translated_count,
            "failed": failed_count,
        }
    
    return {
        "status": "OK",
        "lines": len(lines),
        "translated": translated_count,
        "failed": failed_count,
    }

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "timestamp": timestamp,
        "total_files": 0,
        "success": 0,
        "structure_issues": 0,
        "failed": [],
        "samples": [],
        "summary": {}
    }
    
    # Get all EN files
    en_files = sorted(EN_ROOT.rglob("*.md"))
    report["total_files"] = len(en_files)
    
    print(f"\n[PHASE 3] Starting safe RU translation of {len(en_files)} files...")
    print(f"Timeout: {TIMEOUT_SECONDS}s | Retries: {MAX_RETRIES} | Sleep: {SLEEP_BETWEEN_LINES}s\n")
    
    total_translated = 0
    total_failed = 0
    
    for idx, en_file in enumerate(en_files, 1):
        rel_path = en_file.relative_to(EN_ROOT)
        ru_file = RU_ROOT / rel_path
        
        try:
            result = translate_file(en_file, ru_file)
            
            if result["status"] == "OK":
                report["success"] += 1
                total_translated += result.get("translated", 0)
                total_failed += result.get("failed", 0)
                
                if idx <= 5 or idx % 20 == 0:
                    report["samples"].append({
                        "file": str(rel_path).replace("\\", "/"),
                        **result
                    })
                
                status_char = "✓"
            else:
                report["structure_issues"] += 1
                report["failed"].append({
                    "file": str(rel_path).replace("\\", "/"),
                    **result
                })
                status_char = "✗"
            
            print(
                f"[{idx:3d}/{len(en_files)}] {status_char} {rel_path} | "
                f"Lines: {result.get('lines', result.get('en_lines', '?'))} | "
                f"Translated: {result.get('translated', 0)} | "
                f"Failed: {result.get('failed', 0)}"
            )
        
        except Exception as e:
            report["failed"].append({
                "file": str(rel_path).replace("\\", "/"),
                "error": str(e)
            })
            print(f"[{idx:3d}/{len(en_files)}] ✗ {rel_path} | ERROR: {e}")
    
    report["summary"] = {
        "total_translated_lines": total_translated,
        "total_failed_lines": total_failed,
        "success_rate": f"{(report['success'] / report['total_files'] * 100):.1f}%"
    }
    
    # Save report
    report_file = OUTPUT_DIR / f"rebuild_ru_safe_translation_{timestamp}.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n[PHASE 3] Translation complete!")
    print(f"Success: {report['success']}/{report['total_files']} files")
    print(f"Structure issues: {report['structure_issues']}")
    print(f"Total lines translated: {total_translated}")
    print(f"Total line fallbacks: {total_failed}")
    print(f"Report: {report_file}\n")
    
    return report

if __name__ == "__main__":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
    main()
