FROM python:3.11-slim

# === 1. Системные зависимости и Инструменты ===
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    ffmpeg \
    sudo \
    wget \
    procps \
    ca-certificates \
    gnupg \
    zsh \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Установка Node.js 20 и Docker CLI в одном слое для оптимизации
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    curl -fsSL https://get.docker.com | sh && \
    apt-get install -y nodejs && \
    # Установка системных зависимостей для Playwright (браузеров)
    npx -y playwright install-deps && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# === 2. Пользователь и Окружение ===
RUN useradd -m -u 1000 -s /bin/zsh developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer

# Установка Oh My Zsh + Плагины для супер-продуктивности
USER developer
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting && \
    sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc && \
    sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' ~/.zshrc

# Полезные алиасы для разработки
RUN echo 'alias run-api="python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"' >> ~/.zshrc && \
    echo 'alias test-all="pytest backend/tests"' >> ~/.zshrc && \
    echo 'alias lint="ruff check backend"' >> ~/.zshrc

# === 3. Python зависимости ===
USER root
COPY backend/requirements.txt backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir black ruff pytest mypy debugpy pre-commit concurrently

# === 4. Финализация ===
ENV PYTHONPATH=/app/backend
ENV PATH="/home/developer/.local/bin:${PATH}"
ENV ENV=development
ENV TERM=xterm-256color

WORKDIR /app/backend
USER developer
CMD ["sleep", "infinity"]
