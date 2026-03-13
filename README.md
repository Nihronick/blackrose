# BlackRose Guides 🌹

Telegram Mini App — справочник гильдии BlackRose для игры Lost Ark.  
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
- 🔍 Поиск по всем гайдам
- ⭐ Избранное (Telegram CloudStorage)
- ⚙️ Админ-панель — редактирование гайдов и категорий прямо в приложении
- 🔒 Контроль доступа по whitelist пользователей
- 📱 Pull-to-refresh, быстрая навигация

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

### Bot
| Переменная | Описание |
|---|---|
| `TELEGRAM_API_TOKEN` | Токен Telegram-бота |
| `ALLOWED_USERS` | Whitelist пользователей |
| `MINIAPP_URL` | URL фронтенда |
| `ACCESS_MODE` | Режим доступа (`users` — только whitelist) |

### Frontend
| Переменная | Описание |
|---|---|
| `VITE_API_URL` | URL backend API |

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

## Лицензия

MIT — см. [LICENSE](LICENSE)
