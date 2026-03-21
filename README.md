# BlackRose Guides 🌹

Telegram Mini App — справочник гильдии BlackRose для игры Slayer Legend.
Позволяет участникам гильдии быстро находить гайды прямо в Telegram, не выходя из чата.

---

## Стек

| Слой | Технологии |
|---|---|
| Frontend | React + Vite, Telegram WebApp SDK |
| Backend | FastAPI (Python 3.11), asyncpg |
| База данных | PostgreSQL |
| Бот | aiogram 3, polling |
| Деплой | Railway (монорепо, 3 сервиса) |

---

## Структура монорепо

```
blackrose/
├── bot/          # Telegram-бот (aiogram, polling)
├── backend/      # REST API (FastAPI + PostgreSQL)
└── frontend/     # React SPA (Vite + nginx)
```

---

## Возможности

- 📚 Каталог гайдов по категориям с иконками
- 🔍 Поиск по всем гайдам (title, text, key)
- ⭐ Избранное (Telegram CloudStorage)
- ⚙️ Админ-панель — редактирование гайдов и категорий прямо в приложении
- 🎨 Визуальный выбор иконок в редакторе
- 🔒 Контроль доступа по whitelist пользователей
- 📱 Pull-to-refresh, быстрая навигация, haptic feedback

---

## Переменные окружения

### Backend
| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram-бота |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_USERS` | Список ID пользователей через запятую |
| `ADMIN_USERS` | ID администраторов через запятую |
| `INIT_DATA_MAX_AGE` | Время жизни initData в секундах (по умолчанию 86400) |
| `LOG_LEVEL` | Уровень логирования (INFO / DEBUG) |
| `FRONTEND_URL` | URL фронтенда (для CORS) |
| `BOT_NOTIFY_URL` | URL бота (если бот доступен по HTTP) для push-уведомлений подписчикам при создании нового гайда |

### Bot
| Переменная | Описание |
|---|---|
| `TELEGRAM_API_TOKEN` | Токен Telegram-бота |
| `ALLOWED_USERS` | Whitelist пользователей |
| `ADMIN_USERS` | ID администраторов (через запятую) |
| `MINIAPP_URL` | URL фронтенда |
| `ACCESS_MODE` | Режим доступа (`users` — только whitelist) |

### Frontend
| Переменная | Описание |
|---|---|
| `VITE_API_URL` | URL backend API |

---

## Доступ администратора

> ⚠️ **Важно:** reply-кнопки Telegram не передают `initData`, поэтому
> панель администратора доступна **только через inline-кнопку**.

Для входа в панель администратора:
1. Отправьте команду `/admin` боту
2. Нажмите кнопку **«⚙️ Открыть как администратор»** в ответном сообщении
3. Только эта кнопка передаёт корректные данные авторизации

При `/start` бот автоматически отправляет inline-кнопку администраторам.

---

## Деплой на Railway

Каждый сервис деплоится независимо через **Watch Paths**:

- Backend: `/backend/**`
- Frontend: `/frontend/**`
- Bot: `/bot/**`

```
railway link        # привязать проект
railway up          # задеплоить сервис
```

---

## Локальный запуск

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npx vite --host 0.0.0.0 --port 3000

# Bot
cd bot
pip install -r requirements.txt
python main.py
```

---

## CI/CD

Каждый push в `main` запускает GitHub Actions:

| Job | Что проверяет |
|---|---|
| `backend-test` | pytest 87 тестов |
| `backend-lint` | ruff lint + format |
| `bot-lint` | ruff lint |
| `frontend-build` | `npm run build` |
| `all-checks` | gate для Railway деплоя |

Railway деплоит только после зелёного `all-checks`. Настройка: Railway → сервис → Settings → вкладка **Deploy** → **Check CI status before deploying** → включить.

## Pre-commit хуки

```bash
pip install pre-commit
pre-commit install   # один раз после клонирования репо
```

После этого перед каждым `git commit` автоматически запускаются:
- ruff lint + format (Python)
- prettier (JS/JSX/CSS)
- проверка на случайно закоммиченные токены и ключи

## Тесты

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Покрытие:
- `tests/test_auth.py` — `verify_telegram_init_data`, `_parse_ids`, `_validate_key`
- `tests/test_formatting.py` — `format_guide_text`, `normalize_icon_syntax`
- `tests/test_api_endpoints.py` — HTTP endpoints (health, auth, search, guide, admin, top)

Тесты не требуют реальной БД или Telegram — все внешние зависимости заменены stub-ами.

---

## Лицензия

MIT — см. [LICENSE](LICENSE)
