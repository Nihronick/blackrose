# BlackRose — единый контейнер: API + Bot + ARQ Worker
# Back4app: Root Directory = ./backend  →  build context = ./backend/
# Все нужные файлы (включая bot/) лежат внутри backend/

FROM python:3.11-slim

# Подавляет предупреждения debconf в логах Docker
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Backend зависимости
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Bot зависимости
COPY backend/bot/requirements.txt ./bot-requirements.txt
RUN pip install --no-cache-dir -r bot-requirements.txt

# Копируем содержимое backend и папку assets
COPY backend/ .
COPY assets/ ./assets/

RUN chmod +x entrypoint.sh && mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/api/health || exit 1

EXPOSE 7860

CMD ["./entrypoint.sh"]
