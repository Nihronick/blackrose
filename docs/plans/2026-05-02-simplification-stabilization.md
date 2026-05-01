# BlackRose Simplification & Stabilization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Упростить бэкенд (удаление компрессии видео) и фронтенд (упрощение анимаций) для повышения стабильности и удобства поддержки.

**Architecture:** Переход от CPU-интенсивной обработки на бэкенде к стратегии "Direct Upload". Упрощение UI-слоя через удаление сложных Layout-анимаций.

**Tech Stack:** Python (FastAPI), React (Vite), Docker.

---

### Task 1: Backend — Удаление видео-компрессии

**Files:**
- Modify: `backend/storage.py`
- Modify: `backend/Dockerfile`
- Test: `backend/test.py` (или создание нового теста загрузки)

**Step 1: Удалить функцию `_compress_video_bytes` и упростить `upload_file`**
- Удалить импорты `tempfile`, `subprocess`.
- Удалить вызов `_compress_video_bytes`.
- Оставить `_optimize_image_bytes` (WebP полезен).

**Step 2: Очистить Dockerfile от зависимостей ffmpeg**
- Удалить `apt-get install ffmpeg libsm6 libxext6`.

**Step 3: Проверить локальный запуск бэкенда**
- Запустить `uvicorn main:app` и убедиться в отсутствии ошибок импорта.

### Task 2: Frontend — Упрощение анимаций

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/layout/Layout.tsx` (и аналогичные)

**Step 1: Замена сложных переходов на простые**
- Удалить `layoutId` у `motion` компонентов.
- Заменить сложные анимации на `initial={{ opacity: 0 }} animate={{ opacity: 1 }}`.

### Task 3: Валидация и Деплой

**Step 1: Проверка загрузки видео**
- Загрузить файл > 50МБ через админку и убедиться, что он попадает в HF Dataset без обработки.

**Step 2: Запуск деплой-скрипта**
- Выполнить `.\deploy-backend.ps1`.
