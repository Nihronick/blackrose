# Скрипт для деплоя бэкенда в Hugging Face Spaces
# Использование: .\deploy-backend.ps1

Write-Host "🚀 Начинаю деплой бэкенда в Hugging Face..." -ForegroundColor Cyan

# 1. Сохраняем текущее состояние
$currentBranch = (git branch --show-current)
Write-Host "📍 Текущая ветка: $currentBranch"

# 2. Создаем чистую ветку для деплоя
Write-Host "🧹 Очистка временных веток..." -ForegroundColor Gray
git branch -D hf-deploy-tmp 2>$null

Write-Host "📦 Подготовка чистого бэкенда..." -ForegroundColor Yellow
git checkout --orphan hf-deploy-tmp
git rm -rf --cached .

# 3. Копируем только то, что нужно для HF
git checkout main -- backend/ README.md CLAUDE.md

# 4. Коммит и Пуш
git commit -m "Production deployment to HF Spaces"
Write-Host "📤 Отправка в Hugging Face..." -ForegroundColor Green
git push hf_deploy hf-deploy-tmp:main --force

# 5. Возвращаемся назад
Write-Host "🏠 Возвращаюсь в ветку $currentBranch" -ForegroundColor Gray
git checkout $currentBranch
git branch -D hf-deploy-tmp

Write-Host "✅ Деплой завершен успешно!" -ForegroundColor Green
