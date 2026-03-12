# BlackRose — монорепо

Один репозиторий, три Railway-сервиса.

```
blackrose/
├── bot/        → Railway сервис «bot»      (aiogram, worker)
├── backend/    → Railway сервис «backend»  (FastAPI, Dockerfile)
├── frontend/   → Railway сервис «frontend» (React+Vite→nginx, Dockerfile)
└── .gitignore
```

## Railway: настройка сервисов

### Shared Variables (Settings → Shared Variables)
Задать один раз — все сервисы наследуют:
```
ALLOWED_USERS   = 123456789,987654321
```

### Сервис: bot
| Параметр | Значение |
|---|---|
| Root Directory | `bot` |
| Start Command | `python main.py` |
| **Variables** | |
| `TELEGRAM_API_TOKEN` | токен бота |
| `ALLOWED_USERS` | (из Shared) |
| `ACCESS_MODE` | `users` |
| `MINIAPP_URL` | URL frontend-сервиса |

### Сервис: backend
| Параметр | Значение |
|---|---|
| Root Directory | `backend` |
| Dockerfile | авто-определение |
| **Variables** | |
| `BOT_TOKEN` | токен бота |
| `ALLOWED_USERS` | (из Shared) |

### Сервис: frontend
| Параметр | Значение |
|---|---|
| Root Directory | `frontend` |
| Dockerfile | авто-определение |
| **Variables** | |
| `VITE_API_URL` | URL backend-сервиса |

## Порядок деплоя

1. Создать Railway-проект → подключить этот репозиторий
2. Добавить Shared Variable `ALLOWED_USERS`
3. Задеплоить **backend** → скопировать его URL
4. Задеплоить **frontend** (добавить `VITE_API_URL` = URL backend) → скопировать его URL
5. Задеплоить **bot** (добавить `MINIAPP_URL` = URL frontend)

## Локальная разработка

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (другой терминал)
cd frontend && npm install && npm run dev

# Bot (другой терминал)
cd bot && pip install -r requirements.txt
cp .env.example .env  # заполнить токены
python main.py
```
