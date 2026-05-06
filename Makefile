# BlackRose Automation Makefile

# Переменные
COMPOSE_DEV = docker-compose

BACKEND_EXEC = $(COMPOSE_DEV) exec backend
FRONTEND_EXEC = $(COMPOSE_DEV) exec frontend

.PHONY: help up down build restart logs test lint format migrate seed clean check-env

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Запустить все сервисы в фоне
	$(COMPOSE_DEV) up -d

dev: up ## Запустить разработку (Backend + Frontend)
	@echo "[INFO] Backend at http://localhost:8000"
	@echo "[INFO] Frontend at http://localhost:5173"
	$(COMPOSE_DEV) logs -f


build: ## Собрать или пересобрать образы
	$(COMPOSE_DEV) build

down: ## Остановить и удалить контейнеры
	$(COMPOSE_DEV) down

restart: ## Перезапустить все сервисы
	$(COMPOSE_DEV) restart

logs: ## Показать логи всех сервисов
	$(COMPOSE_DEV) logs -f

# --- Тестирование и Качество кода ---

test: test-backend test-e2e ## Запустить все тесты

test-backend: ## Запустить тесты бэкенда через pytest
	$(BACKEND_EXEC) pytest tests -v

test-e2e: ## Запустить E2E тесты через Playwright
	$(FRONTEND_EXEC) npm run test:e2e

lint: ## Проверить код линтером ruff
	$(BACKEND_EXEC) ruff check .

format: ## Отформатировать код через black и ruff
	$(BACKEND_EXEC) black .
	$(BACKEND_EXEC) ruff check . --fix

# --- База данных ---

migrate: ## Применить миграции alembic
	$(BACKEND_EXEC) alembic upgrade head

seed: ## Заполнить базу начальными данными (админ и категории)
	$(BACKEND_EXEC) python -m services.common.setup

db-shell: ## Войти в консоль postgres
	$(COMPOSE_DEV) exec db psql -U user -d blackrose

# --- Инструменты ---

shell-backend: ## Войти в терминал бэкенда
	$(BACKEND_EXEC) zsh

shell-frontend: ## Войти в терминал фронтенда
	$(FRONTEND_EXEC) bash

clean: ## Удалить временные файлы, кэши и __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +

check-env: ## Проверить наличие .env файлов
	@if [ ! -f .env ]; then echo "\033[31m[!] .env file missing\033[0m"; fi
	@if [ ! -f backend/.env ]; then echo "\033[31m[!] backend/.env file missing\033[0m"; fi
