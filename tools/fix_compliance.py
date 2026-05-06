import os
import re

# Определяем корень проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_SRC = os.path.join(BASE_DIR, "frontend", "src")

def fix_backend_init():
    """Добавляет __init__.py во все поддиректории бэкенда."""
    print("🔍 Checking backend __init__.py markers...")
    for root, dirs, _ in os.walk(BACKEND_DIR):
        if "__pycache__" in root or ".pytest_cache" in root or ".ruff_cache" in root:
            continue
        for d in dirs:
            dir_path = os.path.join(root, d)
            if d.startswith(".") or d == "__pycache__":
                continue
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    pass
                print(f"✅ Created {os.path.relpath(init_file, BASE_DIR)}")

def fix_react_namespaces():
    """Заменяет React.FC на FC и т.д. (согласно CLAUDE.md)"""
    print("🔍 Checking React namespaces in frontend...")
    for root, _, files in os.walk(FRONTEND_SRC):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Находим использования React.X
                react_usages = set(re.findall(r'React\.([A-Z]\w*)', content))
                if not react_usages:
                    continue

                # Заменяем React.X на X
                content = re.sub(r'React\.([A-Z]\w*)', r'\1', content)
                
                # Добавляем именованный импорт, если его нет
                for usage in react_usages:
                    if f"import {{ {usage}" not in content and f"import {{ type {usage}" not in content:
                        # Простая вставка в начало для надежности
                        content = f"import {{ {usage} }} from 'react';\n" + content

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"🔧 Fixed React namespaces in {os.path.relpath(filepath, FRONTEND_SRC)}")

def cleanup_stale_files():
    """Удаляет устаревшие или ошибочно созданные файлы."""
    stale = [
        os.path.join(FRONTEND_SRC, "global.d.ts"),
        os.path.join(BACKEND_DIR, "bot", "main.py"), # Если бот теперь в core/main.py
    ]
    for f in stale:
        if os.path.exists(f):
            os.remove(f)
            print(f"🗑️ Deleted stale file: {os.path.relpath(f, BASE_DIR)}")

def main():
    print("=== BlackRose Architecture Compliance Tool ===\n")
    fix_backend_init()
    fix_react_namespaces()
    cleanup_stale_files()
    print("\n✅ Compliance check completed.")

if __name__ == "__main__":
    main()
