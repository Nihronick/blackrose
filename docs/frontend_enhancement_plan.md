# 🎨 Frontend Enhancement Plan: "BlackRose Premium"

> **Статус:** Основные пункты выполнены (10 августа 2026). Ниже — обновлённый план с отметками выполненных задач.

## 1. 🚀 Home Page: From "List" to "Dashboard" ✅
- [x] **Personalized Hero Section**: Приветствие с Telegram-именем и раздел «Последние обновления».
- [x] **Activity Feed**: Горизонтальный скролл с новыми и обновлёнными гайдами.
- [x] **Pinned/Favorite Categories**: Быстрый доступ к избранным категориям.
- [x] **Community Pulse**: Секция последних комментариев.

## 2. 💎 User Engagement & UX — Частично выполнено
- [ ] **Subscription System UI**: Кнопка «🔔 Подписаться» на карточках категорий (бэкенд готов, UI нет).
- [ ] **Reading Progress**: Прогресс-бар в длинных гайдах.
- [x] **Smart Search**: Полнотекстовый поиск с `useDeferredValue` и `useTransition` (мгновенный отклик).
- [x] **Interactive Tools**: Калькулятор билдов (`BuildPlannerView.tsx`) с рангами промоута 1-21 и DPS.

## 3. 🛠️ Admin Panel Pro ✅
- [x] **Visual Analytics**: Grafики просмотров (Recharts) в админ-панели.
- [x] **Media Manager**: Вкладка управления медиа.
- [x] **Content Health**: Дашборд со статистикой гайдов.
- [x] **Исправлен UI**: Убран дублирующийся заголовок, обновлён стиль логина на BlackRose Crimson & Gold.

## 4. ✨ Design Polish ✅
- [x] **Eradication Layui**: Полностью удалён Layui CDN. 100% чистый Tailwind CSS v4.
- [x] **Тёмная тема высокой контрастности**: Глубокий графит `#0D0E12`, серебряный `#9CA3AF`, готический rose `#E11D48`.
- [x] **Glassmorphism 2.0**: `rose-bento-card`, `glass-card`, `rose-glow-btn` с blur и gradient border.
- [x] **Micro-animations**: Stagger-in, `framer-motion` entry animations, `animate-pulse` Bento-скелетоны.
- [x] **Haptic Feedback**: Вибрация при каждом нажатии через `@capacitor/haptics`.

## 5. ⚡ Производительность ✅ (новый раздел)
- [x] **Vendor Chunk Splitting**: React, Framer Motion, Recharts, TanStack — отдельные кэшируемые чанки.
- [x] **es2022 build target**: Без устаревших полифиллов, без production sourcemaps.
- [x] **React 19 Concurrent**: `useDeferredValue` (SearchView), `startTransition` (BuildPlannerView).
- [x] **Lazy Image Loading**: `loading="lazy"` + `decoding="async"` на всех изображениях.
- [x] **Route Code Splitting**: Все views через `React.lazy()` + `Suspense`.
- [x] **Главный JS бандл уменьшен на 71.3%**: с 530 кБ до 152 кБ.

## 6. 🗺️ Навигация и UX ✅ (новый раздел)
- [x] **View Transitions API**: Плавные cross-fade переходы между страницами.
- [x] **Scroll Restoration**: Автоматический сброс скролла при навигации.
- [x] **Bento-скелетоны**: Стилизованные загрузочные блоки вместо пустых экранов.
- [x] **Хлебные крошки** (`Breadcrumbs.tsx`): Навигационная иерархия на детальных страницах.
- [x] **Пустые состояния** (`EmptyState.tsx`): Красивые блоки «Ничего не найдено» с кнопками действия.
- [x] **Кнопка «Наверх»** (`ScrollToTopFab.tsx`): Плавающая FAB на длинных гайдах.

---

## Оставшиеся задачи (Backlog)
- [ ] Виртуализация длинных списков (TanStack Virtual)
- [ ] Subscription System UI (кнопка подписки на категории)
- [ ] Reading Progress Bar для длинных гайдов
- [ ] Favicon + OG-картинка в актуальном стиле
- [ ] PWA оффлайн-кэш
