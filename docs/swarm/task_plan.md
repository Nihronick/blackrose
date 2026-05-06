# 🗺️ План выполнения миссии SW-007

> Миссия: SW-007: Пред-деплойная проверка и Релиз (Pre-flight & Deployment)
> Запущена: 2026-05-06
> Лидер миссии: architect
> Статус: ✅ ЗАВЕРШЕНА (Код готов, ожидается действие оператора)

## Этапы
- [x] Этап 1: Аудит `backend/Dockerfile` и `supervisord.conf` (HF Spaces).
  - Конфигурация подтверждена: использует `python:3.11-slim`, запускает `entrypoint.sh` -> `supervisord` (Uvicorn + ARQ Worker).
- [x] Этап 2: Аудит скриптов деплоя.
  - Подтверждено: `tools/deploy-backend.ps1` собирает чистый бэкенд и пушит на HF Spaces.
  - Подтверждено: `tools/deploy-frontend.ps1` собирает Vite/React и пушит на GitHub Pages (gh-pages).
- [x] Этап 3: Подготовка коммита основного репозитория.

## 🚀 Инструкция по деплою (Для Оператора)
Поскольку контейнерная песочница не позволяет мне (AI-агенту) напрямую выполнять PowerShell скрипты на хост-машине Windows, выполни следующие шаги в терминале проекта:

1. **Сохранение всех архитектурных улучшений в основной репозиторий:**
   ```powershell
   git add .
   git commit -m "chore: final architectural audit and environment mappings"
   git push origin main
   ```

2. **Деплой Бэкенда (Hugging Face Spaces):**
   ```powershell
   .\tools\deploy-backend.ps1
   ```

3. **Деплой Фронтенда (GitHub Pages):**
   ```powershell
   .\tools\deploy-frontend.ps1
   ```
