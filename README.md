# 🌹 BlackRose: Ультимативная Гибридная Платформа Знаний

[![Website](https://img.shields.io/badge/Сайт-blackrosesl.me-blueviolet?style=for-the-badge&logo=react)](https://blackrosesl.me)
[![Backend](https://img.shields.io/badge/Бэкенд-Hugging_Face-orange?style=for-the-badge&logo=fastapi)](https://huggingface.co/spaces/Nihronick/blackrose-backend)
[![License](https://img.shields.io/badge/Лицензия-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)

**BlackRose** — это высокопроизводительная и защищенная база знаний для экосистемы **Slayer Legend**, построенная на архитектуре **Ultimate Hybrid Core**. Проект разработан русским разработчиком и полностью оптимизирован для работы в качестве **Telegram Mini App (TMA)** и современного **PWA**, обеспечивая мгновенный доступ к игровым гайдам с премиальным уровнем UX.

---

## ✨ Основные особенности

*   **Premium UI/UX ("Renaissance")**: Интерфейс с использованием Mesh-градиентов, эффекта стекла (Glassmorphism) и плавных анимаций на базе Framer Motion.
*   **Оптимизация под TMA**: Полная интеграция с Telegram SDK, поддержка нативных кнопок, тактильной отдачи (Haptic Feedback) и автоматическое определение платформы.
*   **Умная Синхронизация**: Автоматический импорт, синтез и перевод гайдов из Discord-лаборатории с сохранением игрового глоссария.
*   **Predictive Performance**: Упреждающая загрузка контента (prefetching) и продвинутое кэширование для работы в условиях медленного интернета.

---

## 🏗️ Техническая Архитектура (Hybrid Core)

BlackRose использует уникальную гибридную архитектуру, которая адаптируется под контекст пользователя (TMA vs Web).

```mermaid
graph TD
    A[Пользователь] --> B{Определение среды}
    B -->|Telegram Mini App| C[Контекст TMA]
    B -->|Web / PWA| D[Контекст Браузера]

    C --> E[Telegram SDK / Native UI]
    D --> F[Premium Web UI]

    E & F --> G[FastAPI Backend]

    subgraph "Уровень Безопасности"
    G --> H{Стратегия Auth}
    H -- "TMA: initData (HMAC-SHA256)" --> I[JWT Сессия]
    H -- "Web: JWT + Refresh" --> I
    end

    I --> J[(PostgreSQL / Neon)]
    I --> K[Redis / Cache]
    G --> L[HF Datasets / Media]
```

---

## 🔐 Безопасность и Надежность

Проект прошел глубокую закалку (hardening) для стабильной работы:
- **Криптографическая валидация**: Проверка `initData` по официальному алгоритму Telegram (HMAC-SHA256).
- **Защита от атак**: Rate Limiting с поддержкой прокси (Hugging Face / Cloudflare) через `X-Forwarded-For`.
- **Мониторинг**: Интеграция с Telegram для мгновенных алертов о критических ошибках бэкенда.
- **Чистая архитектура**: Децентрализованная обработка медиа и автоматическая очистка временных файлов.

---

## 🚀 Быстрый запуск (Локальная разработка)

### 1. Требования
- Docker и Docker Compose
- Node.js 18+ (для фронтенда)

### 2. Настройка окружения
```bash
cp .env.example .env
# Отредактируйте .env, добавив ваш BOT_TOKEN и другие ключи
```

### 3. Запуск Бэкенда (с БД и Redis)
```bash
docker-compose up --build
```
API будет доступно по адресу `http://localhost:8000`.

### 4. Запуск Фронтенда
```bash
cd frontend
npm install
npm run dev
```
Интерфейс будет доступен по адресу `http://localhost:5173`.

---

## 🛠️ Стек Технологий

- **Бэкенд**: FastAPI (Python 3.11+), SQLAlchemy 2.0, Alembic, Pydantic v2, ARQ (для фоновых задач).
- **Фронтенд**: React 18, Vite, Tailwind CSS 4, Framer Motion, TanStack Query.
- **Инфраструктура**: PostgreSQL (Neon.tech), Redis, Docker, GitHub Actions.

---

## 👤 Автор

**Максим Морозов (Nihronick)**
- **GitHub**: [@Nihronick](https://github.com/Nihronick)
- **Статус**: Production Ready | SEO Optimized | Hybrid Core Enabled

---
*BlackRose — это доказательство того, что профессиональный софт можно строить на современных инструментах с креативным подходом к инфраструктуре. Сделано с ❤️ в России.*
