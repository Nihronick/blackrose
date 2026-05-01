#!/usr/bin/env python3
"""
Auto-fix common translation issues in all RU guide files.
Patterns to fix:
- English headers (# What, # How, # When, # Why, # Is, etc.)
- ":призывать" / "призыва" → "получить" / "получа"
- Inconsistent terminology
"""
import re
from pathlib import Path

RU_ROOT = Path("guides/ru")

# Pattern mappings: (find_pattern, replacement, explanation)
FIXES = [
    # English bold headers - PRIORITY
    (r'^\*\*Skill Mastery Info\*\*$', r'**Информация об освоении навыков**', "Translate Skill Mastery header"),
    (r'^\*\*Each Pages? Skill Upgrade\*\*$', r'**Улучшение навыков на каждой странице**', "Translate skills upgrade header"),
    (r'^\*\*(\d+) Companions?\*\*$', r'**\1 Спутник(и)**', "Translate companions header"),
    (r'^\*\*Information\*\*$', r'**Информация**', "Translate Information header"),
    (r'^\*{0,3}\*?Adventures?\*?\*{0,3}$', r'**Приключения**', "Translate Adventures header"),
    (r"^# ([A-Z][a-z]+'s Passives)$", r'# Пассивные умения \1', "Translate passive abilities header"),
    
    # English in-text headers
    (r'^## Страница I$', r'## Страница 1', "Roman numeral I → Arabic 1"),
    (r'^## Страница II$', r'## Страница 2', "Roman numeral II → Arabic 2"),
    (r'^## Страница III$', r'## Страница 3', "Roman numeral III → Arabic 3"),
    
    # Inconsistent terminology
    (r'Требовать:', 'Требуется:', "Fix inconsistent 'Требовать' vs 'Требуется'"),
    (r'бриллианты', 'алмазы', "Replace 'бриллианты' with 'алмазы'"),
    
    # Incomplete sentences
    (r'комплектация для\.$', 'рекомендуемое оборудование.', "Fix incomplete sentence"),
]

def fix_file(file_path):
    """Apply fixes to a single file."""
    content = file_path.read_text(encoding='utf-8')
    original = content
    changed = False
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        fixed_line = line
        
        for pattern, replacement, reason in FIXES:
            new_line = re.sub(pattern, replacement, fixed_line, flags=re.IGNORECASE | re.MULTILINE)
            if new_line != fixed_line:
                fixed_line = new_line
                changed = True
        
        fixed_lines.append(fixed_line)
    
    result = '\n'.join(fixed_lines)
    
    if result != original:
        file_path.write_text(result, encoding='utf-8')
        return True
    return False

def main():
    files = list(RU_ROOT.rglob("*.md"))
    fixed_count = 0
    total_count = len(files)
    
    print(f"Scanning {total_count} RU files for common issues...\n")
    
    for idx, file in enumerate(files, 1):
        rel_path = file.relative_to(RU_ROOT)
        if fix_file(file):
            fixed_count += 1
            print(f"[{idx:3d}/{total_count}] ✓ {rel_path}")
        else:
            if idx % 20 == 0:
                print(f"[{idx:3d}/{total_count}]   {rel_path}")
    
    print(f"\n✅ Fixed {fixed_count}/{total_count} files")

if __name__ == "__main__":
    main()
