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

## Миграция данных в PostgreSQL

Если база данных пустая, запустите скрипт один раз:

```bash
cd backend
DATABASE_URL=postgresql://... python migrate_content.py
```

После успешной миграции файлы `guides_original.py`, `guides.py` и `migrate_content.py`
можно удалить — они больше не используются.

---

## Лицензия

MIT — см. [LICENSE](LICENSE)
