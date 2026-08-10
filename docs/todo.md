## 🤖 Swarm Missions (Активные миссии консилиума)

| ID | Миссия | Цепочка | Статус | Лидер | Запущена |
|----|--------|---------|--------|-------|----------|
| SW-001 | Swarm Infrastructure Deployment | architect | 🟢 | architect | 2026-05-06 |

## 📋 Стратегический бэклог (для планирования будущих миссий)

### 🚀 High Priority
- [ ] **Load Testing**: Execute k6/locust suite for 200+ concurrent users.
- [ ] **Backup Automation**: Configure scheduled Neon.tech logical backups.
- [ ] **Виртуализация длинных списков**: Внедрить TanStack Virtual для калькуляторов и справочников.

### 🛠️ Features
- [x] **Discord Lab Sync**: Refined mapping between Discord channel IDs and Website categories.
- [x] **Media Resolution**: Configured automatic media downloading/proxying to avoid expired Discord links.
- [x] **Global Search**: Implemented full-text search indexing in PostgreSQL (`tsvector`) and added search UI.
- [x] **Система гильдий**: Backend API (`api/guilds.py`) + Frontend Views (`GuildsView.tsx`, `GuildRosterView.tsx`) + модальные окна заявок/профиля.
- [x] **Калькулятор Билда**: Интерактивный `BuildPlannerView.tsx` с рангами промоута (1-21), навыками и расчётом DPS.

### ✅ Завершено (сессия 10 августа 2026)
- [x] **Удаление Layui CDN**: Полная эрадикация Layui CSS/JS из `index.html`, замена элементов на чистый Tailwind v4.
- [x] **Тёмная тема высокой контрастности**: Обновлены токены `--background`, `--foreground`, `--muted-foreground`, `--primary` в `index.css`.
- [x] **Исправление AdminView**: Убран дублирующийся заголовок в модальном окне логина, обновлён стиль на BlackRose Crimson.
- [x] **Vendor Chunk Splitting**: Конфигурация `manualChunks` в `vite.config.ts` — разделение на `vendor-react`, `vendor-motion`, `vendor-charts`, `vendor-tanstack`.
- [x] **Таргет сборки es2022**: Отключены устаревшие полифиллы, отключены production sourcemaps.
- [x] **useDeferredValue в SearchView**: Мгновенный отклик на ввод текста поиска без блокировки UI.
- [x] **startTransition в BuildPlannerView**: Плавное переключение рангов и навыков без фриза ползунков.
- [x] **Ленивая загрузка изображений**: `loading="lazy"` + `decoding="async"` в `CategoryList.tsx` и `GuildRosterView.tsx`.
- [x] **View Transitions API**: Все навигационные переходы обёрнуты в `document.startViewTransition()` в `navigation.ts`.
- [x] **Scroll Restoration**: Автоматический сброс скролла при смене маршрута в `AppLayout.tsx`.
- [x] **Bento-скелетоны**: Обновлён `ViewLoader` в `AppRouter.tsx` на стилизованный Bento skeleton.
- [x] **Хлебные крошки**: Новый компонент `Breadcrumbs.tsx` интегрирован в `GuideView.tsx`.
- [x] **Пустые состояния**: Новый компонент `EmptyState.tsx` интегрирован в `SearchView`, `FavoritesView`, `HistoryView`.
- [x] **Кнопка «Наверх»**: Новый компонент `ScrollToTopFab.tsx` интегрирован в `GuideView.tsx`.

### 🛡️ Reliability
- [ ] **Error Monitoring**: Backend integration for Honeybadger/Sentry (Frontend is already implemented).

### 💡 Nice to Have
- [ ] Тёмная/светлая тема с переключателем.
- [ ] PWA оффлайн-кэш основных гайдов.
- [ ] Favicon + OG-картинка в актуальном стиле.
- [ ] Лёгкие микроанимации при появлении карточек.
- [ ] Система тегов/категорий с цветовой кодировкой.
