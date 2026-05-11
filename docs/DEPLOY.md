# Деплой BlackRose

```text
Hugging Face Spaces  → backend API + Telegram bot + Inngest worker (Docker, бесплатно)
Neon                 → PostgreSQL БД (500MB, бесплатно)
Upstash              → Redis кэш + очереди (10k req/day, бесплатно)
GitHub Pages         → фронтенд + PWA (бесплатно)
HF Datasets          → медиа хранилище (бесплатно)
Honeybadger          → мониторинг ошибок (опционально)
```

---

## Автодеплой (GitHub Actions)

Деплой полностью автоматизирован. При пуше в ветку `main`:
1. **Frontend** собирается и пушится в ветку `gh-pages`. Оттуда GitHub Pages раздает статику.
2. **Backend** (содержимое папки `backend/` и корень `Dockerfile`) пушится напрямую в репозиторий Hugging Face Spaces (`Nihronick/blackrose-backend`).

Для работы автодеплоя бэкенда в настройках репозитория на GitHub (Settings -> Secrets and variables -> Actions -> Repository secrets) должен быть добавлен токен:
* `HF_TOKEN` — токен от Hugging Face с правами на запись (Write).

---

## Переменные окружения

Все переменные окружения для бэкенда задаются в настройках Space на Hugging Face (Settings -> Variables and secrets).

### Hugging Face Space (backend + bot)

| Переменная | Секрет/Переменная | Описание |
|---|---|---|
| `BOT_TOKEN` | Secret | Токен бота от @BotFather |
| `DATABASE_URL` | Secret | Строка из Neon (без `sslmode`, без `channel_binding`) `postgresql://...neon.tech/neondb?ssl=require` |
| `REDIS_URL` | Secret | Строка из Upstash (если используется) |
| `JWT_SECRET` | Secret | случайная строка 32 символа |
| `ADMIN_USERS` | Secret | Твой Telegram user_id |
| `ADMIN_PASSWORD` | Secret | Логин:пароль для веб-админки |
| `FRONTEND_URL` | Variable | `https://nihronick.github.io/blackrose` |
| `MINIAPP_URL` | Variable | `https://nihronick.github.io/blackrose` |
| `HF_TOKEN` | Secret | Токен от HF для доступа к HF Datasets (медиа) |
| `HF_DATASET_REPO` | Variable | `Nihronick/blackrose-media` |
| `PORT` | Auto | Задается HF (обычно `7860`) |

### GitHub Repository Variables (фронтенд)

Устанавливаются в GitHub Settings -> Variables -> Actions:

| Переменная | Значение |
|---|---|
| `VITE_API_URL` | `https://nihronick-blackrose-backend.hf.space` (URL твоего спейса) |
| `VITE_BOT_NAME` | `blackrosesl1_bot` |
| `VITE_HONEYBADGER_API_KEY` | (опционально) |

---

## Локальная разработка

Проект использует **VS Code DevContainers** для локальной разработки. Больше не нужно использовать `sanity-gravity` или ставить Python на хост.

1. Установи Docker Desktop и расширение Dev Containers в VS Code.
2. Открой проект в VS Code, нажми `F1` -> `Dev Containers: Reopen in Container`.
3. VS Code поднимет окружение с нужным Python и Node.js.

Команды (выполняются внутри контейнера в разных терминалах):
```bash
make dev-backend    # API на localhost:8000
cd frontend && npm run dev   # UI на localhost:5173
make test           # тесты
make lint           # линтер
```
