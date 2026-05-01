#!/usr/bin/env python3
from pathlib import Path

spirit_files = list(Path("guides/ru/spirit").glob("*Meloning.md"))
if spirit_files:
    file = spirit_files[0]
    content = file.read_text(encoding='utf-8')
    if "## Мета-ссылки" not in content:
        content = content.rstrip() + "\n## Мета-ссылки\n- [[spirit_spirits]]\n- [[spirit_detailed_proscons_list_for_spirits]]"
        file.write_text(content, encoding='utf-8')
        print(f"✓ Добавлены meta-links к {file.name}")
