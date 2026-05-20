# Находки и инсайты (Swarm Findings)

## [Auditor] Миссия SW-006: Проверка легаси-решений
При детальной проверке (через AST/чтение файлов) решений из сессии `095ea820...` (Architectural Audit And Cleanup) обнаружено, что **все архитектурные исправления успешно сохранены** в текущей кодовой базе:
1. `backend/services/cache/redis_cache.py` — присутствует метод `invalidate_guide` (строка 105).
2. `backend/models/schemas.py` — в `LabImportIn` присутствуют поля `category_key`, `title`, `guide_key` (строки 103-109).
3. `backend/api/admin.py` — присутствует логика безопасной обработки `icon_url or ""` (строка 34) и вызов `category_service.delete(key)` (строка 109).

**Вывод:** Кодовая база находится в консистентном состоянии. Инструмент `grep_search` ранее дал ложноотрицательный результат (вероятно, из-за особенностей кодировки или переносов строк в Windows), но прямое чтение файлов подтвердило наличие всего кода. Регрессии нет.

## [Tester] Миссия SW-008: Падение CI/CD Pipeline
**Что:** Упали Frontend CI и Backend CI на коммите `deaddde`. Из-за блокировки песочницы на хосте Windows (`run_command` disabled) и таймаута GitHub API (зависание `read_url_content`), агент `tester` физически не может самостоятельно извлечь логи CI.
**Влияние:** Агенту требуются логи Ruff и Biome от оператора для применения протокола SC-MANDATORY и Systematic Debugging. Работа приостановлена (Блок).

**Обновление от Tester (Анализ рантайм-логов):**
Выявлены и исправлены две критические ошибки времени выполнения (Runtime), которые приводили к 500 Server Error и сбоям кэша:
1. **Баг библиотеки Honeybadger (`KeyError: 'key'`):** При дубликатах HTTP заголовков (например, от Cloud-балансировщиков) `honeybadger-python` падал внутри ASGI-адаптера. Применен Monkey-patch в `backend/core/middleware.py`.
2. **Баг сериализации кэша Redis (`datetime is not JSON serializable`):** Объекты с датами возвращались FastAPI, но `json.dumps` в `redis_cache.py` не мог их обработать. Внедрен `jsonable_encoder` в декоратор `backend/core/cache.py`.
