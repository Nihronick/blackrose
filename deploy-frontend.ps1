# Скрипт для деплоя фронтенда в GitHub Pages
# Использование: .\deploy-frontend.ps1

Write-Host "🚀 Начинаю сборку и деплой фронтенда на GitHub..." -ForegroundColor Cyan

# 1. Переходим в папку фронтенда
cd frontend

# 2. Устанавливаем зависимости и собираем проект
Write-Host "📦 Установка зависимостей..." -ForegroundColor Gray
npm install

Write-Host "🏗️ Сборка проекта..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при сборке!" -ForegroundColor Red
    exit 1
}

# 3. Деплой через gh-pages (если установлен пакет)
Write-Host "📤 Отправка на GitHub Pages..." -ForegroundColor Green
npx gh-pages -d dist

Write-Host "✅ Фронтенд успешно обновлен!" -ForegroundColor Green
cd ..
