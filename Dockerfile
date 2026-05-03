# Dockerfile для разработки и управления проектом
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для сборки и работы с БД
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копируем только файлы зависимостей для кэширования слоев
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для FastAPI
EXPOSE 8000

# Команда по умолчанию - запуск сервера с автоперезагрузкой
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
