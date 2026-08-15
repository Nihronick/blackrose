# Деплой и развертывание BlackRose

```text
Hugging Face Spaces  → backend API + Telegram bot + Inngest worker (Docker, бесплатно)
Neon                 → PostgreSQL БД (500MB, бесплатно)
Upstash              → Redis кэш + очереди (10k req/day, бесплатно)
GitHub Pages         → фронтенд + PWA (бесплатно)
HF Datasets          → медиа хранилище (бесплатно)
Honeybadger          → мониторинг ошибок (опционально)
AIO Sandbox          → изолированная агентная среда разработки (Browser, VSCode, Jupyter, MCP)
```

---

## Автодеплой (GitHub Actions)

Деплой полностью автоматизирован. При пуше в ветку `main`:
1. **Frontend** собирается (React 18 + Vite 6 + Tailwind CSS v4) и пушится в ветку `gh-pages`. Оттуда GitHub Pages раздает статику.
2. **Backend** (содержимое папки `backend/` и `Dockerfile.hf`) пушится напрямую в репозиторий Hugging Face Spaces (`Nihronick/blackrose-backend`).

Для работы автодеплоя бэкенда в настройках репозитория на GitHub (`Settings -> Secrets and variables -> Actions -> Repository secrets`) должен быть добавлен токен:
* `HF_TOKEN` — токен от Hugging Face с правами на запись (Write).

---

## Переменные окружения

Все переменные окружения для бэкенда задаются в настройках Space на Hugging Face (`Settings -> Variables and secrets`).

### Hugging Face Space (backend + bot)

| Переменная | Секрет/Переменная | Описание |
|---|---|---|
| `BOT_TOKEN` | Secret | Токен бота от @BotFather |
| `DATABASE_URL` | Secret | Строка подключения Neon `postgresql://...neon.tech/neondb?ssl=require` |
| `REDIS_URL` | Secret | Строка подключения Upstash Redis (если используется) |
| `JWT_SECRET` | Secret | Случайная строка 32+ символа для подписи JWT |
| `ADMIN_USERS` | Secret | Telegram user_id администраторов (через запятую) |
| `INITIAL_ADMINS` | Secret | Начальный логин:пароль для админки (напр. `admin:password123`) |
| `ADMIN_EMERGENCY_KEY` | Secret | Аварийный ключ прямого входа в панель администратора |
| `FRONTEND_URL` | Variable | `https://nihronick.github.io/blackrose` |
| `MINIAPP_URL` | Variable | `https://nihronick.github.io/blackrose` |
| `HF_TOKEN` | Secret | Токен HF с правами Write для доступа к `blackrose-media` |
| `HF_DATASET_REPO` | Variable | `Nihronick/blackrose-media` |
| `PORT` | Auto | Задается HF (обычно `7860`) |

### GitHub Repository Variables (фронтенд)

Устанавливаются в `GitHub Settings -> Variables -> Actions`:

| Переменная | Значение |
|---|---|
| `VITE_API_URL` | `https://nihronick-blackrose-backend.hf.space` |
| `VITE_BOT_NAME` | `blackrosesl1_bot` |
| `VITE_HONEYBADGER_API_KEY` | (опционально) |

---

## Локальная разработка и Docker Compose

### Вариант 1: Docker Compose (Рекомендуемый)

Включает Backend, PostgreSQL и AIO Sandbox:

```bash
# Запуск всех сервисов в фоне (Backend + DB + Sandbox)
make up

# Просмотр логов
make logs

# Выполнение миграций БД
make migrate

# Запуск тестов бэкенда
make test-backend

# Остановка контейнеров
make down
```

Сервисы локально:
- **Backend API**: `http://localhost:8000` (Swagger: `http://localhost:8000/docs`)
- **Frontend Dev**: `http://localhost:5173` (`cd frontend && npm run dev`)
- **AIO Sandbox**: `http://localhost:8080` (VS Code Web: `/vscode`, Jupyter: `/jupyter`)

### Вариант 2: Локальный запуск без Docker

```bash
# Бэкенд
cd backend
python -m venv venv
venv\Scripts\activate      # или source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Фронтенд
cd frontend
npm install
npm run dev
```

---

## Сборка Mobile (Capacitor Android / iOS)

BlackRose кроссплатформенен и поддерживает нативную сборку:

```bash
cd frontend

# 1. Сборка продакшен-бандла
npm run build

# 2. Синхронизация ассетов с нативными проектами
npx cap sync

# 3. Открытие в Android Studio
npx cap open android
```
