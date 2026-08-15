# BlackRose 🌹

[![Frontend](https://img.shields.io/badge/Frontend-GitHub_Pages-blue?style=for-the-badge&logo=react)](https://nihronick.github.io/blackrose)
[![Backend](https://img.shields.io/badge/Backend-Hugging_Face-orange?style=for-the-badge&logo=fastapi)](https://huggingface.co/spaces/Nihronick/blackrose-backend)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**BlackRose** — единая интерактивная база знаний, справочник и сообщество для игроков **Slayer Legend**. Включает веб-приложение, Telegram Mini App (TMA), калькуляторы билдов, ростер гильдий и автоматический пайплайн синхронизации гайдов из Discord.

---

## ⚡ Архитектура и стек

- **Frontend:** React 18 + Vite 6 + TypeScript + Tailwind CSS v4 (100% чистый Tailwind, стеклянный Bento UI)
- **State & Data:** TanStack Query v5, Zustand, React Router v7, View Transitions API, framer-motion
- **Mobile & TMA:** Telegram WebApp SDK, Capacitor (Android + iOS)
- **Backend API:** FastAPI (Python 3.11+), SQLAlchemy 2.0 Async, Pydantic v2
- **Database:** Neon PostgreSQL (производство) / PostgreSQL 15 (разработка)
- **Cache & Queues:** Upstash Redis / Redis 7, Inngest для фонового импорта
- **Media Storage:** Hugging Face Datasets (`Nihronick/blackrose-media`) + imgproxy
- **Bot & Automation:** aiogram 3, aiohttp stealth listener
- **Sandbox Environment:** [AIO Sandbox](https://github.com/agent-infra/sandbox) (Browser, Shell, VS Code Server, Jupyter, MCP)

Подробная документация:
- Архитектурный регламент: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Инструкция по деплою и переменным: [`docs/DEPLOY.md`](docs/DEPLOY.md)
- Инженерные правила разработки: [`docs/CLAUDE.md`](docs/CLAUDE.md)
- Актуальный план задач: [`docs/todo.md`](docs/todo.md)

---

## 🚀 Быстрый старт (Локальная разработка)

### Требования
- Docker & Docker Compose (рекомендуется)
- Node.js 18+ и Python 3.11+ (при локальном запуске без Docker)

### 1. Настройка окружения
```bash
cp .env.example .env
```

### 2. Запуск через Docker Compose (Backend + PostgreSQL + AIO Sandbox)
```bash
# Запуск всех сервисов
make up

# Просмотр логов
make logs

# Выполнение миграций
make migrate
```

Сервисы:
- **Backend API:** `http://localhost:8000` (Swagger: `http://localhost:8000/docs`)
- **AIO Sandbox:** `http://localhost:8080` (VS Code Server: `/code-server/`, Jupyter: `/jupyter`)

### 3. Запуск фронтенда
```bash
cd frontend
npm install
npm run dev
```
Фронтенд будет доступен по адресу `http://localhost:5173`.

---

## 📱 Сборка Mobile (Capacitor)

```bash
cd frontend
npm run build
npx cap sync
npx cap open android
```

---

## 🔄 Деплой (CI/CD)

Деплой полностью автоматизирован через **GitHub Actions** при пуше в ветку `main`:
- **Frontend:** автосборка и деплой на GitHub Pages (`.github/workflows/deploy-frontend.yml`).
- **Backend:** автодеплой на Hugging Face Spaces (`.github/workflows/deploy-backend.yml`).

---

## 👤 Автор

**Maksim Morozov (Nihronick)**  
- GitHub: [@Nihronick](https://github.com/Nihronick)
- Telegram: [@nihronick](https://t.me/nihronick)
- Проект: [BlackRose Live](https://nihronick.github.io/blackrose)
