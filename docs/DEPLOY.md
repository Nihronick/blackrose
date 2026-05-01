# Деплой BlackRose

```
Back4App Containers  → backend API + Telegram bot (Docker, бесплатно)
Neon                 → PostgreSQL БД (500MB, бесплатно)
Upstash              → Redis кэш + очереди (10k req/day, бесплатно)
GitHub Pages         → фронтенд + PWA (бесплатно)
Honeybadger          → мониторинг ошибок (опционально)
```

---

## Переменные окружения

Все переменные используются **один раз** — в Back4App.
Бот живёт в том же контейнере что и API, поэтому `API_URL=http://localhost:8080` — постоянный.

### Back4App (backend + bot)

| Переменная | Значение | Описание |
|---|---|---|
| `BOT_TOKEN` | `123:ABC...` | Токен бота от @BotFather |
| `DATABASE_URL` | `postgresql://...neon.tech/neondb?ssl=require` | Строка из Neon (без `sslmode`, без `channel_binding`) |
| `REDIS_URL` | `rediss://...upstash.io:6380` | Строка из Upstash |
| `JWT_SECRET` | случайная строка 32 символа | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_USERS` | `123456789` | Твой Telegram user_id |
| `ADMIN_PASSWORD` | `nihronn:пароль` | Логин:пароль для веб-админки |
| `FRONTEND_URL` | `https://nihronick.github.io/blackrose` | URL фронтенда (без слэша в конце) |
| `MINIAPP_URL` | `https://nihronick.github.io/blackrose` | То же что FRONTEND_URL |
| `PORT` | `8080` | Порт сервера |
| `LOG_LEVEL` | `info` | Уровень логов |
| `HONEYBADGER_API_KEY` | (опционально) | Ключ Honeybadger |
| `R2_*` | (опционально) | Cloudflare R2 для медиафайлов |

### GitHub Repository Variables (фронтенд)

| Переменная | Значение |
|---|---|
| `VITE_API_URL` | `https://blackrose-xxxxxxxx.b4a.run` (с **https**!) |
| `VITE_BOT_NAME` | `blackrosesl1_bot` |
| `VITE_HONEYBADGER_API_KEY` | (опционально) |

---

## Neon — важно про DATABASE_URL

Neon даёт строку вида:
```
postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require&channel_binding=require
```

Нужно заменить на:
```
postgresql://user:pass@ep-xxx.neon.tech/neondb?ssl=require
```

Убрать `sslmode=` (asyncpg использует `ssl=`) и убрать `channel_binding=require` (asyncpg не поддерживает).

---

## После каждого деплоя на Back4App

Back4App меняет URL контейнера при каждом деплое. Обновить нужно только одну переменную:

**GitHub → Settings → Variables → `VITE_API_URL`** → новый URL вида `https://blackrose-xxxxxxxx.b4a.run`

Затем нажми **Re-run** на последнем деплое в GitHub Actions, или сделай пустой коммит:
```bash
git commit --allow-empty -m "redeploy: update API URL"
git push
```

---

## Команды разработки

```bash
make dev-backend    # API на localhost:8000
make dev-frontend   # UI на localhost:3000
make dev-bot        # бот в polling режиме
make test           # тесты
make lint           # линтер
make migrate        # применить миграции
```
