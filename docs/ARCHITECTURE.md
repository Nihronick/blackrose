# Архитектура BlackRose (актуальная версия)

Документ фиксирует фактическую архитектуру и эксплуатационные ограничения, чтобы избегать расхождения между "идеальной схемой" и реальным продом.

## 1. Основные компоненты

| Слой | Технология | Роль |
|---|---|---|
| Frontend | React + Vite + TypeScript | UI, Telegram Mini App UX, запросы к API |
| Backend API | FastAPI | Публичные/админ маршруты, auth, orchestration |
| Jobs | Inngest + фоновые функции | Долгие/асинхронные операции импорта |
| DB | Neon PostgreSQL | Гайды, категории, пользователи, служебные данные |
| Media | HF Datasets + imgproxy | Хранение и трансформация медиа |
| Bot/Worker | aiogram + worker processes | Telegram интеграция и фоновые задачи |

## 2. Критические потоки

### 2.1 Авторизация
1. Frontend отправляет Telegram initData / login payload.
2. Backend валидирует подпись и выдает short-lived JWT.
3. При `401` frontend выполняет refresh и ретраит запрос.

### 2.2 Импорт Discord Guide
1. Frontend вызывает `/api/admin/lab/import`.
2. Backend создает Inngest event и сразу возвращает `202 Accepted`.
3. Inngest-функция выполняет синтез/нормализацию и сохраняет результат.
4. Контент и медиа сохраняются через сервисный слой.

### 2.3 Чтение контента
1. Frontend запрашивает guides/comments через публичные роуты.
2. Backend читает из PostgreSQL и возвращает типизированные DTO.
3. Медиа рендерится через HF resolve/imgproxy URL.

## 3. Где лежит код (логика -> файлы)

| Функционал | Frontend | Backend |
|---|---|---|
| Главный экран | `frontend/src/components/HomeDashboard.tsx` | `backend/api/public.py` |
| Просмотр гайда | `frontend/src/views/GuideView.tsx` | `backend/api/public.py` |
| Импорт/медиа в админке | `frontend/src/components/ExportImport.tsx` | `backend/api/admin.py` |
| Авторизация | `frontend/src/components/AdminLoginModal.tsx` | `backend/core/auth.py` |
| История поиска | `frontend/src/hooks/useSearchHistory.ts` | client-side only |

## 4. Эксплуатационные риски (не теоретические)

1. HF Spaces free-tier ограничивает ресурсы: тяжелые медиа-операции могут деградировать API.
2. Discord CDN ссылки короткоживущие: импорт должен быть быстрым и с прозрачной ошибкой для пользователя.
3. HF Dataset public resolve может иметь короткую eventual-consistency задержку.
4. Цепочка из нескольких сервисов (API, Jobs, Media, Bot, Sync) увеличивает blast radius любой ошибки.

## 5. Архитектурные правила

1. Бизнес-логика и внешние SDK остаются в `backend/services/`, роутеры должны быть тонкими.
2. Для backend import path используется плоская схема (`from api import ...`), без префикса `backend.`.
3. Все backend подпакеты должны содержать `__init__.py`.
4. Типы frontend должны оставаться строгими: без `any`, Telegram типы через `global.d.ts`.
5. Любое изменение деплоя и инфраструктуры должно быть синхронизировано с `docs/CLAUDE.md` и `docs/todo.md`.
