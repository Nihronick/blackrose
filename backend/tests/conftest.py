import sys
import os

# Этот файл лежит в backend/tests/
# Добавляем backend/ в sys.path чтобы `import main` нашёл main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))