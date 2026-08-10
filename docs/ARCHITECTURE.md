# Архитектура BlackRose (актуальная версия)

Документ фиксирует фактическую архитектуру и эксплуатационные ограничения, чтобы избегать расхождения между "идеальной схемой" и реальным продом.

> **Последнее обновление:** 10 августа 2026

## 1. Основные компоненты

| Слой | Технология | Роль |
|---|---|---|
| Frontend | React 19 + Vite 6 + TypeScript + Tailwind CSS v4 | UI, Telegram Mini App UX, запросы к API |
| Backend API | FastAPI | Публичные/админ маршруты, auth, orchestration |
| Jobs | Inngest + фоновые функции | Долгие/асинхронные операции импорта |
| DB | Neon PostgreSQL | Гайды, категории, пользователи, гильдии, служебные данные |
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

### 2.4 Навигация и переходы между страницами
1. Все маршруты загружаются через `React.lazy()` и `Suspense` с Bento-скелетоном.
2. Переходы используют нативный **View Transitions API** (`document.startViewTransition`) для плавного cross-fade.
3. Scroll Restoration автоматически сбрасывает позицию при переходе.

## 3. Где лежит код (логика -> файлы)

| Функционал | Frontend | Backend |
|---|---|---|
| Главный экран | `frontend/src/views/HomeView.tsx` | `backend/api/public.py` |
| Просмотр гайда | `frontend/src/views/GuideView.tsx` | `backend/api/public.py` |
| Калькулятор Билда | `frontend/src/views/BuildPlannerView.tsx` | client-side only |
| Гильдии (список) | `frontend/src/views/GuildsView.tsx` | `backend/api/guilds.py` |
| Ростер гильдии | `frontend/src/views/GuildRosterView.tsx` | `backend/api/guilds.py` |
| Поиск | `frontend/src/views/SearchView.tsx` | `backend/api/public.py` |
| Категории | `frontend/src/views/CategoriesView.tsx` | `backend/api/public.py` |
| Импорт/медиа в админке | `frontend/src/views/AdminView.tsx` | `backend/api/admin.py` |
| Авторизация | `frontend/src/components/AdminLoginModal.tsx` | `backend/core/auth.py` |
| Навигация | `frontend/src/lib/navigation.ts` | — |
| Роутер приложения | `frontend/src/app/AppRouter.tsx` | — |
| Компоновка и Навигация | `frontend/src/app/AppLayout.tsx` | — |

## 4. Фронтенд-компоненты (новые)

| Компонент | Назначение |
|---|---|
| `Breadcrumbs.tsx` | Хлебные крошки (Главная / Категории / Гайд) |
| `EmptyState.tsx` | Универсальные пустые состояния (поиск, избранное, история) |
| `ScrollToTopFab.tsx` | Плавающая кнопка «Наверх» при прокрутке > 300px |

## 5. Эксплуатационные риски (не теоретические)

1. HF Spaces free-tier ограничивает ресурсы: тяжелые медиа-операции могут деградировать API.
2. Discord CDN ссылки короткоживущие: импорт должен быть быстрым и с прозрачной ошибкой для пользователя.
3. HF Dataset public resolve может иметь короткую eventual-consistency задержку.
4. Цепочка из нескольких сервисов (API, Jobs, Media, Bot, Sync) увеличивает blast radius любой ошибки.

## 6. Архитектурные правила

1. Бизнес-логика и внешние SDK остаются в `backend/services/`, роутеры должны быть тонкими.
2. Для backend import path используется плоская схема (`from api import ...`), без префикса `backend.`.
3. Все backend подпакеты должны содержать `__init__.py`.
4. Типы frontend должны оставаться строгими: без `any`, Telegram типы через `global.d.ts`.
5. Любое изменение деплоя и инфраструктуры должно быть синхронизировано с `docs/CLAUDE.md` и `docs/todo.md`.
6. Фронтенд использует **100% чистый Tailwind CSS v4** — никаких сторонних CSS-фреймворков (Layui, Bootstrap и пр.).
7. Все навигационные переходы оборачиваются в `View Transitions API` через хук `useAppNavigation`.
