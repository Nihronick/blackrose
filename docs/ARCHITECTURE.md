# Архитектура BlackRose (актуальная версия)

Документ фиксирует фактическую архитектуру и эксплуатационные ограничения, чтобы избегать расхождения между "идеальной схемой" и реальным продом.

> **Последнее обновление:** 14 августа 2026

## 1. Основные компоненты

| Слой | Технология | Роль |
|---|---|---|
| Frontend | React 18 + Vite 6 + TypeScript + Tailwind CSS v4 | UI, Telegram Mini App UX, запросы к API |
| Mobile | Capacitor (Android + iOS) | Нативные обёртки для мобильных платформ |
| Анимации | framer-motion (`AnimatePresence`) + View Transitions API | Плавные переходы между экранами и модалки |
| Backend API | FastAPI | Публичные/админ маршруты, auth, orchestration |
| Jobs | Inngest + фоновые функции | Долгие/асинхронные операции импорта |
| DB | Neon PostgreSQL (прод) / Postgres 15 (dev) | Гайды, категории, пользователи, гильдии, служебные данные |
| Media | HF Datasets + imgproxy | Хранение и трансформация медиа |
| Bot/Worker | aiogram + aiohttp + worker processes | Telegram интеграция и фоновые задачи |
| Sandbox | AIO Sandbox (Docker) | Изолированная среда для агентов: Browser, Shell, File, VSCode, Jupyter, MCP |

## 2. Критические потоки

### 2.1 Авторизация
1. Frontend отправляет Telegram initData / admin login payload.
2. Backend валидирует подпись (HMAC для TMA, credentials для admin) и выдает short-lived JWT.
3. При `401` frontend выполняет refresh и ретраит запрос.

### 2.2 Импорт Discord Guide
1. Frontend вызывает `/api/admin/lab/import`.
2. Backend создает Inngest event и сразу возвращает `202 Accepted`.
3. Inngest-функция выполняет синтез/нормализацию и сохраняет результат.
4. Контент и медиа сохраняются через сервисный слой.

### 2.3 Discord Sync (Stealth)
1. Admin сохраняет Discord user token через `/api/discord-sync/`.
2. Backend запускает `stealth_discord_worker` при старте приложения.
3. Worker парсит каналы Discord, синхронизирует данные с БД.

### 2.4 Чтение контента
1. Frontend запрашивает guides/comments через публичные роуты.
2. Backend читает из PostgreSQL и возвращает типизированные DTO.
3. Медиа рендерится через HF resolve/imgproxy URL.

### 2.5 Навигация и переходы между страницами
1. Все маршруты загружаются через `React.lazy()` и `Suspense` с Bento-скелетоном.
2. Переходы используют нативный **View Transitions API** (`document.startViewTransition`) для плавного cross-fade.
3. Модальные окна и элементы UI используют `framer-motion` (`AnimatePresence`).
4. Scroll Restoration автоматически сбрасывает позицию при переходе.

## 3. Где лежит код (логика -> файлы)

### 3.1 Frontend Views (16 экранов)

| Функционал | Frontend | Backend |
|---|---|---|
| Главный экран | `frontend/src/views/HomeView.tsx` | `backend/api/public.py` |
| Просмотр гайда | `frontend/src/views/GuideView.tsx` | `backend/api/public.py` |
| Список гайдов в категории | `frontend/src/views/GuidesView.tsx` | `backend/api/public.py` |
| Категории | `frontend/src/views/CategoriesView.tsx` | `backend/api/public.py` |
| Поиск | `frontend/src/views/SearchView.tsx` | `backend/api/public.py` |
| Калькулятор Билда | `frontend/src/views/BuildPlannerView.tsx` | client-side only |
| Гильдии (список) | `frontend/src/views/GuildsView.tsx` | `backend/api/guilds.py` |
| Ростер гильдии | `frontend/src/views/GuildRosterView.tsx` | `backend/api/guilds.py` |
| Избранное | `frontend/src/views/FavoritesView.tsx` | client-side (localStorage) |
| История просмотров | `frontend/src/views/HistoryView.tsx` | client-side (localStorage) |
| Профиль | `frontend/src/views/ProfileView.tsx` | `backend/api/public.py` |
| Roadmap | `frontend/src/views/RoadmapView.tsx` | client-side only |
| Онбординг | `frontend/src/views/OnboardingView.tsx` | client-side only |
| Результаты по тегу | `frontend/src/views/TagResultsView.tsx` | `backend/api/public.py` |
| Админ-панель | `frontend/src/views/AdminView.tsx` | `backend/api/admin.py` |
| Доступ запрещён | `frontend/src/views/AccessDeniedView.tsx` | — |

### 3.2 Frontend App Layer

| Файл | Назначение |
|---|---|
| `frontend/src/app/AppRouter.tsx` | Роутер (React Router v7, 16 маршрутов, lazy loading) |
| `frontend/src/app/AppLayout.tsx` | Компоновка, Bottom Nav, View Transitions, Scroll Restoration |
| `frontend/src/app/AppProvider.tsx` | React Query + провайдеры |

### 3.3 Backend API Роуты

| Файл | Назначение |
|---|---|
| `backend/api/public.py` | Публичные эндпоинты: гайды, категории, поиск, комменты, профиль |
| `backend/api/admin.py` | Админ-панель: CRUD, импорт, настройки |
| `backend/api/guilds.py` | Гильдии: создание, заявки, ростер, настройки |
| `backend/api/discord_sync.py` | Discord Sync: токен, статус worker, каналы |
| `backend/api/users_admin.py` | Управление пользователями (админ) |
| `backend/api/media.py` | Загрузка и проксирование медиа |
| `backend/api/webhook_ingest.py` | Приём вебхуков от внешних сервисов |

### 3.4 Backend Services

| Сервис | Путь | Назначение |
|---|---|---|
| Guides | `backend/services/guides/` | CRUD гайдов, поиск, категории |
| Guilds | `backend/services/guilds/` | Бизнес-логика гильдий |
| Discord Lab | `backend/services/discord_lab/` | Импорт из Discord (Inngest) |
| Discord Sync | `backend/services/discord_sync/` | Stealth worker для синхронизации каналов |
| Media | `backend/services/media/` | Работа с медиа (HF Datasets, imgproxy) |
| Storage | `backend/services/storage/` | Абстракция файлового хранилища |
| Cache | `backend/services/cache/` | Redis кэш |
| Telegram Bot | `backend/services/telegram_bot/` | Бот (aiogram), inline WebApp |
| Translation | `backend/services/translation/` | Перевод контента (deep-translator) |
| Notifications | `backend/services/notifications/` | Система уведомлений |
| Common | `backend/services/common/` | Seed, setup, утилиты |
| Sandbox | `backend/services/sandbox/` | Клиент AIO Sandbox SDK |

### 3.5 Backend Core

| Файл | Назначение |
|---|---|
| `backend/core/config.py` | Pydantic Settings (все переменные окружения) |
| `backend/core/auth.py` | JWT, Telegram HMAC, admin auth |
| `backend/core/db.py` | SQLAlchemy async engine, session, pool |
| `backend/core/middleware.py` | CORS, security headers, Honeybadger |
| `backend/core/logging.py` | structlog, request context |
| `backend/core/rate_limit.py` | slowapi limiter |
| `backend/core/http.py` | aiohttp singleton client |
| `backend/core/inngest_client.py` | Inngest клиент |

## 4. Фронтенд-компоненты

### 4.1 Бизнес-компоненты (24 файла)

| Компонент | Назначение |
|---|---|
| `AdminLoginModal.tsx` | Модальное окно входа в админку |
| `UserAuthModal.tsx` | Авторизация пользователей (Telegram + web) |
| `Breadcrumbs.tsx` | Хлебные крошки (Главная / Категории / Гайд) |
| `CommentsSection.tsx` | Блок комментариев к гайду |
| `EmptyState.tsx` | Универсальные пустые состояния |
| `ErrorBoundary.tsx` | Обработка ошибок React |
| `ExportImport.tsx` | Экспорт/импорт данных (админ) |
| `FabButton.tsx` | Floating Action Button |
| `FavoriteButton.tsx` | Кнопка добавления в избранное |
| `GuildJoinModal.tsx` | Модальное окно заявки в гильдию |
| `GuildProfileModal.tsx` | Профиль гильдии |
| `GuildSettingsModal.tsx` | Настройки гильдии (админ) |
| `Header.tsx` | Шапка приложения |
| `HomeDashboard.tsx` | Дашборд главной страницы (29KB — крупнейший компонент) |
| `IconLibrary.tsx` | Библиотека иконок |
| `Lightbox.tsx` | Просмотр изображений на весь экран |
| `PtrIndicator.tsx` | Pull-to-Refresh индикатор |
| `QuickNav.tsx` | Быстрая навигация |
| `ReorderList.tsx` | Перетаскиваемый список |
| `ScrollToTopFab.tsx` | Кнопка «Наверх» при прокрутке > 300px |
| `SmartImage.tsx` | Lazy-загрузка изображений с fallback |
| `TableOfContents.tsx` | Оглавление гайда |
| `TagBadge.tsx` | Бейдж тега с цветовой кодировкой |
| `TopGuidesSection.tsx` | Секция топ-гайдов |

### 4.2 UI-примитивы (shadcn-style, `components/ui/`)

`alert`, `badge`, `button`, `card`, `dialog`, `input`, `label`, `sheet`, `skeleton`, `textarea`, `BrandIcon`

### 4.3 Hooks (10 файлов)

| Хук | Назначение |
|---|---|
| `queries.ts` | TanStack Query хуки для API |
| `useAppEnv.tsx` | Определение среды (TMA / Web / PWA) |
| `useAppInitialization.ts` | Инициализация приложения |
| `useFavorites.ts` | Управление избранным (localStorage) |
| `useHistory.ts` | История просмотров |
| `usePullToRefresh.ts` | Pull-to-Refresh жест |
| `useSearchHistory.ts` | История поиска |
| `useSheet.ts` | Управление Bottom Sheet |
| `useSubscriptions.ts` | Подписки на контент |
| `useTelegramBackButton.ts` | Кнопка «Назад» в Telegram |

### 4.4 Lib (17 файлов)

| Модуль | Назначение |
|---|---|
| `api.ts` | HTTP-клиент (fetch + auth headers) |
| `auth.ts` | Клиентская логика авторизации |
| `navigation.ts` | `useAppNavigation` — навигация с View Transitions API |
| `types.ts` | TypeScript типы (Guide, Category, Guild и др.) |
| `markdown.ts` | Рендеринг Markdown (marked + DOMPurify) |
| `telegram.ts` | Telegram WebApp API обёртки |
| `capacitor.ts` | Capacitor native API (haptics, status bar) |
| `haptic.ts` | Тактильная обратная связь |
| `theme.ts` | Управление темой |
| `storage.ts` | Абстракция localStorage |
| `utils.ts` | Утилиты |
| `constants.ts` | Константы |
| `gameIcons.ts` | Иконки из игры (22KB) |
| `rankIcons.ts` | Иконки рангов |
| `icons.ts` | Системные иконки |
| `language.ts` | Локализация |

## 5. Эксплуатационные риски (не теоретические)

1. HF Spaces free-tier ограничивает ресурсы: тяжелые медиа-операции могут деградировать API.
2. Discord CDN ссылки короткоживущие: импорт должен быть быстрым и с прозрачной ошибкой для пользователя.
3. HF Dataset public resolve может иметь короткую eventual-consistency задержку.
4. Цепочка из нескольких сервисов (API, Jobs, Media, Bot, Sync, Sandbox) увеличивает blast radius любой ошибки.
5. Capacitor mobile builds требуют тестирования на реальных устройствах — эмуляторы не покрывают edge cases.
6. AIO Sandbox потребляет ~2GB RAM — на слабых машинах может конфликтовать с другими контейнерами.

## 6. Архитектурные правила

1. Бизнес-логика и внешние SDK остаются в `backend/services/`, роутеры должны быть тонкими.
2. Для backend import path используется плоская схема (`from api import ...`), без префикса `backend.`.
3. Все backend подпакеты должны содержать `__init__.py`.
4. Типы frontend должны оставаться строгими: без `any`, Telegram типы через `globals.d.ts`.
5. Любое изменение деплоя и инфраструктуры должно быть синхронизировано с `docs/CLAUDE.md` и `docs/todo.md`.
6. Фронтенд использует **100% чистый Tailwind CSS v4** — никаких сторонних CSS-фреймворков. Все legacy-компоненты удалены.
7. Все навигационные переходы оборачиваются в `View Transitions API` через хук `useAppNavigation`.
8. Линтер фронтенда — **Biome** (не ESLint). Команда: `npm run lint` / `npm run lint:fix`.
9. Тесты: backend — pytest, frontend — vitest + Testing Library, E2E — Playwright.
