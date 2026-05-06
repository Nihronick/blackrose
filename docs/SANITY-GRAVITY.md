# 🖥️ Sanity-Gravity Container Protocol (v2)

## 🎯 ОБЗОР
Поскольку локальная Windows-песочница нестабильна для некоторых операций (ошибки 255, ECONNREFUSED), мы используем **Sanity-Gravity Container** как основную среду исполнения.

## 📦 КОНТЕЙНЕР
- **Имя**: `sanity-gravity-ag-xfce-kasm-1`
- **Пользователь**: `moroz`
- **Путь к проекту**: `/home/moroz/workspace/`

## ⌨️ КОМАНДЫ (ЧЕРЕЗ HOST POWERSHELL)
Для выполнения команд используй `docker exec`:

```powershell
docker exec sanity-gravity-ag-xfce-kasm-1 bash -c "cd /home/moroz/workspace && ТВОЯ КОМАНДА"
```

### Примеры:
- `ls -la /home/moroz/workspace/`
- `git status`
- `pytest backend/tests`
- `npm run build` (внутри frontend/)

## 🚫 ЗАПРЕЩЕНО
- Использовать `dir` (используй `ls`)
- Использовать `powershell -Command` для логики внутри проекта
- Использовать `~` (ведет в /root/)

## 📬 SWARM INFRASTRUCTURE
Все коммуникации агентов и логи миссий хранятся в:
`docs/swarm/`

Не перемещать и не скрывать эту папку. Она является runtime-инфраструктурой проекта.
