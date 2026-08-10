# 🚨 MANDATORY STOP — НЕ ПРОПУСКАТЬ

Ты находишься в проекте BlackRose. Ты не имеешь права импровизировать.

1. Прочитай `docs/swarm/task_plan.md` — узнай текущую миссию
2. Прочитай `docs/swarm/findings.md` — узнай контекст
3. Следуй роли согласно Trigger Table в этом файле
4. Примени навыки из `skills/` согласно своей роли
5. Пройди Quality Gate перед тем, как сказать "готово"

Если ты проигнорируешь эти шаги, твоя работа будет немедленно отменена.

# 🛠️ BlackRose: Project Guidelines & AI Context Management

## 🧠 Context Persistence (CRITICAL)

This project uses a "Snapshot & Handoff" system to ensure continuity between AI sessions.

### 1. Skill Selection (MANDATORY — Read Before Coding)

Before starting ANY task, match it to the table below and **read the SKILL.md file** via `view_file`.
Do NOT name-drop skills. Either read and follow them, or don't mention them.

## 🤖 BlackRose Swarm Protocol (Multi-Agent Consilium)

### 🎭 Таблица триггеров ролей (Trigger Table)

При получении задачи агент-диспетчер ОБЯЗАН сопоставить запрос с таблицей и разложить его на роли. Триггеры работают по принципу ИЛИ — срабатывание любого слова активирует роль.

| Роль | Триггеры (ключевые слова) | Обязательные навыки |
|------|---------------------------|---------------------|
| **architect** | спроектировать, api, эндпоинты, архитектура, схема, модель данных, контракт | `backend-architect`, `api-patterns`, `database-design` |
| **developer** | написать, реализовать, код, функция, endpoint, имплементировать | `pydantic-models-py`, `database`, `systematic-debugging` |
| **auditor** | безопасность, уязвимость, audit, проверка, OWASP, секреты, утечка | `security-auditor`, `vibe-code-auditor` |
| **frontend** | компонент, UI, интерфейс, вёрстка, React, стили, Tailwind, анимация | `react-patterns`, `tailwind-patterns`, `react-component-performance` |
| **tester** | тест, покрытие, TDD, проверить, валидация, pytest, e2e | `tdd-workflow`, `webapp-testing`, `verification-before-completion` |

### 🧠 KAG Protocol (Knowledge-Augmented Generation)

Перед началом любой задачи агент-диспетчер ОБЯЗАН:
1. Прочитать `skills/swarm-knowledge/SKILL.md`.
2. Подтянуть README из репозиториев, соответствующих активным ролям миссии (через `read_url_content` для GitHub raw).
3. Синтезировать полученные знания с контекстом проекта и закэшировать ключевые паттерны в `docs/swarm/mailboxes/{role}/inbox/cache.json`.
4. Это гарантирует использование актуальных отраслевых стандартов (FastAPI, React 18, OWASP) вместо устаревших паттернов.

### 🛠️ Environment & Infrastructure
- **Sandbox**: VS Code DevContainers (`.devcontainer/devcontainer.json`) + Docker Compose (`docker-compose.dev.yml`).
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:5173`
- **Workflow**: Open the project in DevContainers. No host-level `venv` or Python installation is required.

### 🔌 Initialization & Skill Injection (The Combine)

При старте сессии или новой миссии агент ОБЯЗАН:
1. Прочитать `ag.yaml` для понимания доступных ролей и ворклоув.
2. Прочитай `docs/swarm/task_plan.md` и `docs/swarm/findings.md`.
3. Активировать нужные навыки через `skills/catalog-map/SKILL.md`.

### 📜 Swarm Roles (The Combine)
Агенты работают в цепочке: `architect → developer → auditor → tester → Quality Validator`.
4. Если навык из каталога критически важен — имитировать его поведение, опираясь на триггеры и описание.
5. Использовать `local_skills` из папки `skills/` как мастер-инструкции.

### 📬 Mailbox System (Почтовые ящики агентов)

Агенты общаются через файловую систему, чтобы не мешать друг другу при редактировании кода.

**Структура:** `docs/swarm/mailboxes/{роль}/inbox/` — непрочитанные сообщения, `processed/` — архив.

**Формат сообщения (JSON):**
```json
{
  "sender": "architect",
  "receiver": "developer",
  "timestamp": "2026-05-06T14:30:00Z",
  "type": "task | question | review | block | approve",
  "body": "Спроектировал API. Эндпоинты в docs/swarm/findings.md. Приступай к реализации.",
  "attachments": ["docs/swarm/findings.md#эндпоинты"]
}
```

**Правила:**
1. Агент проверяет свой inbox каждые 10 итераций.
2. Прочитанные сообщения перемещаются в `processed/`.
3. Если агент получает `type: block`, он ОСТАНАВЛИВАЕТ работу и ждёт дальнейших инструкций от диспетчера.

### 📋 Manus Protocol (Три бортовых журнала)

**task_plan.md** — чеклист задач. Создаётся в начале миссии, обновляется при завершении этапов.

**findings.md** — доска находок. Сюда пишут ВСЕ агенты, когда находят что-то важное (ошибки, решения, ссылки). Формат:
```markdown
### [Роль агента] [Тема]
**Что:** [Находка]
**Влияние:** [На что это влияет]
```

**progress.md** — автоматический лог. Каждый агент при завершении этапа добавляет строку в таблицу.

## 🛡️ Quality Gate (ПРОВЕРКА ПЕРЕД КАЖДЫМ ОТВЕТОМ)

Перед тем, как сказать "готово", агент обязан пройти этот чек-лист:

- [ ] Я прочитал `CLAUDE.md` при входе в сессию?
- [ ] Я проверил `task_plan.md` и знаю текущую миссию?
- [ ] Я применил навыки, соответствующие моей роли (Trigger Table + `ag.yaml`)?
- [ ] Я не нарушил ни одного Антипаттерна из `CLAUDE.md`?
- [ ] Я обновил `progress.md` и `findings.md`?
- [ ] Я создал snapshot в `docs/snapshots/` (если задача завершена)?

Если хоть один пункт не выполнен — агент не говорит "готово", а возвращается к исправлению.

## ⏸️ MANDATORY CHECKPOINT
Каждые 10 действий агент обязан остановиться и ответить на вопрос: "Следую ли я инструкциям из docs/?" Ответ должен быть со ссылкой на конкретный пункт из `CLAUDE.md`.

## 🚫 Правило трёх ошибок
Если Quality Gate трижды подряд находит нарушение одних и тех же инструкций из `docs/`, агент обязан прекратить работу и передать задачу человеку с пометкой [MANUAL_REVIEW_REQUIRED].

### 📝 Synthesis Protocol (Session Wrap-up)
ОБЯЗАТЕЛЬНЫЙ отчет в конце сессии:
1. **Mission Status**: Текущий статус из `task_plan.md`.
2. **Key Findings**: Кратко из `findings.md`.
3. **Agent Contributions**: Какие роли были задействованы и что сделали.
4. **Validation Gate Result**: Подтверждение прохождения чек-листа.
5. **Next Step**: Что должен сделать следующий агент.

### 🔄 Конфликт-менеджмент (если агенты не согласны)

1. **По безопасности:** Приоритет `auditor`.
2. **По архитектуре:** Приоритет `architect`.
3. **По реализации:** Открытый спор в `findings.md` → решение принимает диспетчер.
4. Финальное решение всегда записывается с пометкой `[RESOLVED]` и подписью принявшего решение агента.

### 📦 Дефолтные цепочки (Quick Launch)

**Фича «под ключ» (feature-fullstack):**
`architect → [developer + frontend] → auditor → tester → gate`

**Багфикс (bugfix):**
`developer → tester → gate`

**Рефакторинг (refactor):**
`auditor → developer → tester → gate`

**Аудит безопасности (security-audit):**
`auditor → [опционально: developer для исправлений] → auditor → gate`

---

### 🧰 Categorized Skill Inventory (Swarm Expert Pool)

#### 🎨 Frontend (UI/UX & Experience)
| Role | Skill | Trigger Phrases |
|------|-------|-----------------|
| **UI Builder** | `react-patterns` | React components, hooks, lifecycle |
| **Styler** | `tailwind-patterns` | CSS, Tailwind, Glassmorphism, Premium UI |
| **A11y Auditor** | `ui-a11y` | Accessibility, WCAG, screen readers |
| **Perf Optimizer** | `react-component-performance` | Slow UI, re-renders, hydration |

#### ⚙️ Backend (API & Architecture)
| Role | Skill | Trigger Phrases |
|------|-------|-----------------|
| **API Designer** | `api-patterns` | REST, JSON, Endpoints, Contracts |
| **DB Manager** | `database-design` | PostgreSQL, Schema, Migrations, Neon |
| **Auth Handler** | `auth-implementation` | JWT, TMA, HMAC, Security |
| **Cache Architect** | `database` | Redis, Upstash, Background jobs |

#### 🧪 Testing & Audit (QA)
| Role | Skill | Trigger Phrases |
|------|-------|-----------------|
| **Unit Tester** | `tdd-workflow` | Tests, pytest, coverage, logic |
| **E2E Tester** | `webapp-testing` | Playwright, browser tests, flows |
| **Security Scanner** | `security-auditor` | Vulnerabilities, audit, secrets |
| **Code Auditor** | `vibe-code-auditor` | Anti-patterns, code quality |

#### 🏗️ DevOps (Infrastructure)
| Role | Skill | Trigger Phrases |
|------|-------|-----------------|
| **Docker Specialist** | `bash-scripting` | Dockerfile, Linux, Sandbox, Environment |
| **CI/CD Builder** | `github` | GitHub Actions, Workflows, Pipelines |
| **Windows Engineer** | `powershell-windows` | PS1 scripts, Windows host tasks |
| **Deployer** | `vercel-deployment` | Production deploy, Vercel, HF Spaces |

---

### 📝 Synthesis Protocol (Session Wrap-up)

В конце каждой сессии агент-диспетчер ОБЯЗАН предоставить отчет в формате Synthesis:

1. **Mission Status**: Итоговый статус из `task_plan.md`.
2. **Key Findings**: 2-3 самых важных инсайта из `findings.md`.
3. **Agent Contributions**: Что сделал каждый эксперт (architect, developer и т.д.).
4. **Validation Gate Result**: Результат проверки Quality Gate.
5. **Next Step**: Одна четкая задача для следующего захода.

---

### 5. 🧠 Project Brain: Principal-Level Architecture

#### 💎 Principal-Level Technical Insights

**Core Auth Logic (Edge-to-Core)**

```python
# Backend Verification (Python)
hash = hmac.new(b"WebAppData", token, sha256).digest()
signature = hmac.new(hash, msg, sha256).hexdigest()
is_valid = signature == telegram_provided_hash
```

```typescript
// Frontend Initialization (TS)
const initData = window.Telegram.WebApp.initData;
const user = window.Telegram.WebApp.initDataUnsafe.user;
```

**Tradeoff: HF Datasets vs Cloudflare R2**
- **R2**: Pro: Native S3 API. Con: Minimum monthly fee, egress complexity.
- **HF Datasets**: Pro: Free unlimited storage, Global CDN, unified auth via `HF_TOKEN`. Con: Eventual consistency (1-2s delay) for public resolves.

#### 🗺️ Zero-to-Hero Learning Path
1. **Foundation**: Learn `FastAPI` (Python) and `Vite/React` (TS).
2. **Setup**: Review deployment scripts in `tools\deploy-backend.ps1` and `tools\deploy-frontend.ps1`.
3. **Architecture**: Review `backend/core/db.py` (Neon DB) and `frontend/src/store/` (Zustand).
4. **Contribution**: Pick a task from `docs/todo.md`, follow the **Atomic Commit** rule, and verify via the **Pre-Flight Checklist**.

| Document | Purpose | Reading Order |
|---|---|---|
| `CLAUDE.md` | Rules, architecture, and current state | 1 (MANDATORY) |
| `docs/todo.md` | Active roadmap and technical debt | 2 |
| `docs/snapshots/` | Tactical session history | 3 |
| `docs/TESTING.md` | Verification and QA protocols | 4 |
| `docs/RISKS.md` | Known constraints and failure modes | 5 |

---

## 🏗️ Hybrid Infrastructure

| Component | Hosting | Technology | Purpose |
|---|---|---|---|
| **Frontend** | GitHub Pages | React 18, Vite, Tailwind 4, TypeScript | Client UI & Content Rendering |
| **Backend** | HF Spaces | FastAPI, SQLAlchemy Async, Docker | API, Telegram Bot, ARQ Worker |
| **Database** | Neon | PostgreSQL (Serverless, Pooled) | Guides, Categories, Users, History |
| **Media** | HF Datasets | `huggingface_hub` API | Icons, Images, Videos (Storage) |
| **Media Proxy** | HF Spaces | `imgproxy` (Docker) | On-the-fly image optimization |
| **Wiki Backup** | GitHub API | `GitSyncService` | Automatic .md backups to Git |
| **Cache** | Upstash | Redis (Optional) | Response caching |
| **Monitoring** | Honeybadger | Error tracking (Optional) | Production error alerts |

---

## 🏗️ Hybrid Architecture Overview

```mermaid
graph TD
    Client[Frontend: React/Vite] -->|HTTPS/WSS| API[Backend: FastAPI/Uvicorn]
    API -->|AsyncPG| DB[(PostgreSQL: Neon)]
    API -->|Webhook| TG[Telegram Bot: aiogram]
    API -->|SDK| HF[Media: HF Datasets]
    API -->|ARQ| Worker[Background Worker]
    Worker -->|Redis| Upstash[Cache/Queue: Upstash]
```

---

## 📂 Subsystem Deep-Dive & File Reference

### 🗺️ Principal File Map
<details>
<summary><b>Backend: API, Bot & Logic (`backend/`)</b></summary>

```text
backend/
├── main.py              — FastAPI entry point (Lifespan, Webhooks, CORS, Inngest)
├── core/                — Infrastructure (db.py, auth.py, config.py, inngest_client.py)
├── api/                 — API Routers (admin.py, public.py)
├── models/              — Data Models (db_models.py, schemas.py)
├── services/            — Business Logic (guides/, discord_lab/, storage/)
├── functions/           — Background Workflows (Inngest tasks)
├── bot/                 — aiogram 3.x Telegram Bot logic
├── workers/             — Standalone worker scripts (notify.py, gc_storage.py)
└── Dockerfile           — Production Container (Flat Structure)
```
> [!IMPORTANT]
> **Package Markers**: All directories in `backend/` MUST contain an `__init__.py` file for correct import resolution in CI and Docker environments.
</details>

<details>
<summary><b>Frontend: Client & UI (`frontend/`)</b></summary>

```text
frontend/
├── src/
│   ├── App.tsx          — Router & Context Providers
│   ├── components/      — Atomic UI primitives
│   ├── features/        — High-level page modules
│   ├── store/           — Zustand (User, Navigation, Theme)
│   └── lib/             — API Fetch & Haptic Engine
```
</details>

---

### 🏗️ Backend: The Service Layer (`backend/`)
*Deployed to Hugging Face Spaces (Docker/Supervisord)*

- **API Entry (`main.py`)**: Lifespan-managed FastAPI app. Handles CORS, global exceptions, and integrates the Telegram Bot webhook.
- **Persistence (`core/db.py`, `db_models.py`)**: Async SQLAlchemy 2.0 with Neon.tech (PostgreSQL). Uses `selectinload` for relationship hydration to prevent N+1.
- **Media Engine (`services/storage/hf_storage.py`)**: Abstracted interface to Hugging Face Datasets. Handles multi-part uploads and CDN resolution.
- **Security (`core/auth.py`)**: 
    - `TMA Validation`: HMAC-SHA256 verification of Telegram initData.
    - `JWT Layer`: HS256 tokens with role-based claims (Admin vs Member).
- **Background Worker (`workers/`, `services/`)**: ARQ-powered task queue for non-blocking operations (notifications, heavy processing).

### 🎨 Frontend: The Experience Layer (`frontend/`)
*Deployed to GitHub Pages (Vite/React)*

- **State Sync (`store/`)**: Zustand stores for user session, theme context, and category state.
- **Data Fetching (`lib/api.ts`)**: React Query (TanStack) for caching, prefetching, and optimistic updates.
- **Design System (`components/`, `index.css`)**: 
    - **Glassmorphism**: Tailwind-based glass-cards with backdrop-blur.
    - **Motion**: Staggered `framer-motion` animations for "Premium" feel.
- **Routing (`App.tsx`)**: React Router with protected routes and smooth TMA-native transitions.

### 🤖 Telegram Bot (`backend/bot/`)
*Integrated aiogram 3.x instance*

- **Miniapp Bridge**: Handlers for `/start` and inline buttons to launch the TMA with specific payloads (deep-linking).
- **Admin Tools**: Bot commands for user management and real-time status alerts.

---

## 🔐 Environment Variables Reference

### HF Space Secrets (Backend Production)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Neon pooled connection: `postgresql://user:pass@ep-xxx-pooler...neon.tech/db?sslmode=require` |
| `DIRECT_URL` | ⚠️ | Neon direct connection (for migrations): `postgresql://user:pass@ep-xxx...neon.tech/db?sslmode=require` |
| `BOT_TOKEN` | ✅ | Telegram Bot API token |
| `JWT_SECRET` | ✅ | Secret for admin JWT tokens |
| `ADMIN_USERS` | ✅ | Telegram user_ids (comma-separated) |
| `ADMIN_PASSWORD` | ✅ | Initial admin `username:password` |
| `FRONTEND_URL` | ✅ | `https://nihronick.github.io/blackrose` (for CORS) |
| `MINIAPP_URL` | ✅ | Same as FRONTEND_URL |
| `HF_TOKEN` | ⚠️ | HF token for media dataset access |
| `HF_DATASET_REPO` | ⚠️ | e.g. `Nihronick/blackrose-media` |
| `REDIS_URL` | ❌ | Upstash Redis (optional, for cache/ARQ) |
| `HONEYBADGER_API_KEY` | ❌ | Error monitoring (optional) |
| `GEMINI_API_KEY` | ❌ | Google Gemini for AI synthesis |
| `IMGPROXY_URL` | ✅ | URL of your blackrose-image Space |
| `IMGPROXY_KEY` | ✅ | Hex key for image signing |
| `IMGPROXY_SALT` | ✅ | Hex salt for image signing |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token |
| `GITHUB_REPO` | ✅ | Repository for wiki backups |
| `GITHUB_BRANCH` | ⚠️ | Default branch for backups (main) |
| `PORT` | auto | Set by HF to `7860` |

### Frontend `.env` (Local / Build Time)

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://nihronick-blackrose-backend.hf.space` |
| `VITE_BOT_NAME` | `blackrosesl1_bot` |

---

## 🔐 Security & Access Control

### Authentication Flow
1. **Edge Auth**: TMA sends `initData` (HMAC-SHA256 signed by Telegram).
2. **Validation**: Backend verifies signature using `BOT_TOKEN`.
3. **Session Upgrade**: If valid, backend issues a short-lived `JWT` (15m) and a secure `Refresh Token`.
4. **Role Check**: Middleware ensures only IDs in `ADMIN_USERS` can access `/api/admin/*`.

| Resource | Protocol | Key Provider |
|---|---|---|
| **API Traffic** | TLS 1.3 | HF Spaces (Let's Encrypt) |
| **DB Access** | SSL Required | Neon.tech |
| **Media Auth** | Bearer Token | HF Dataset (HF_TOKEN) |
| **Bot Webhook** | Secret Token | Header: `X-Telegram-Bot-Api-Secret-Token` |

---

## 🔗 URLs & Access (Production Reference)

### 📜 Project Documents

| Doc | Purpose |
|---|---|
| [CLAUDE.md](file:///c:/Users/moroz/Desktop/blackrose-free/docs/CLAUDE.md) | Engineering Standards & AI Protocol |
| [ARCHITECTURE.md](file:///c:/Users/moroz/Desktop/blackrose-free/docs/ARCHITECTURE.md) | Logical Mapping (FE <-> BE) |
| [todo.md](file:///c:/Users/moroz/Desktop/blackrose-free/docs/todo.md) | Active Backlog |

| Service | Public URL | Purpose |
|---|---|---|
| **Frontend** | `https://nihronick.github.io/blackrose/` | Main User UI |
| **Backend API** | `https://nihronick-blackrose-backend.hf.space` | RESTful interface |
| **Media CDN** | `https://huggingface.co/datasets/Nihronick/blackrose-media` | Asset storage |
| **Neon SQL** | `https://console.neon.tech/` | Managed Database |
| **GitHub** | `https://github.com/Nihronick/blackrose` | Source Control |

---

## 🚀 Deployment Protocol

Deployment is fully automated via **GitHub Actions**. Manual deployment scripts (`tools/deploy-*.ps1`) are deprecated.

### Backend → Hugging Face Spaces
- **Trigger:** Push to `main` modifying `backend/` or `Dockerfile`.
- **Workflow:** `.github/workflows/deploy-backend.yml` force pushes to `Nihronick/blackrose-backend` Space.
- **Target:** `https://huggingface.co/spaces/Nihronick/blackrose-backend`

### Frontend → GitHub Pages
- **Trigger:** Push to `main` modifying `frontend/`.
- **Workflow:** `.github/workflows/deploy-frontend.yml` builds with Vite and pushes to the `gh-pages` branch.
- **Target:** `https://nihronick.github.io/blackrose/`

### Pre-Deploy Checklist

Before running any deploy script:

- [ ] **Test locally** — does `uvicorn main:app` start without errors?
- [ ] **Check imports** — no missing `from sqlalchemy import text` etc.
- [ ] **Verify secrets** — are all required env vars set in HF Space Settings?
- [ ] **Review diff** — `git diff` shows only intentional changes?
- [ ] **Line endings** — `.sh` files must be LF, not CRLF (critical for Docker)
- [ ] **No hardcoded secrets** — grep for passwords, tokens, keys

---

## 📝 Git & Commit Rules

### Branch Strategy

- `main` — stable source code (frontend + backend together)
- `gh-pages` — auto-generated, frontend build only (never edit manually)
- HF Space has its own detached repo (force-pushed from deploy script)

### Commit Flow (What Goes Where)

```text
                    ┌─────────────────────────┐
                    │     main branch          │
                    │  (единый source of truth)│
                    │                          │
                    │  backend/   ← Python     │
                    │  frontend/  ← React/TS   │
                    │  docs/      ← CLAUDE.md  │
                    └────────┬────────┬────────┘
                             │        │
                     GitHub  │        │  GitHub
                     Action  │        │  Action
                             ▼        ▼
              ┌──────────────┐  ┌─────────────────┐
              │ HF Space     │  │ gh-pages branch  │
              │ (detached    │  │ (auto-generated) │
              │  git repo)   │  │                  │
              │              │  │ dist/ only       │
              │ backend/*    │  │ (npm run build)  │
              │ only         │  │                  │
              └──────────────┘  └─────────────────┘
              nihronick-       nihronick.github.io
              blackrose-       /blackrose/
              backend.hf.space
```

**Правило:** Весь код коммитится в `main`. GitHub Actions **сами** извлекают нужную часть и пушат в целевой репозиторий. Никогда не пушить напрямую в HF или `gh-pages`.

### What Gets Committed to `main`

- ✅ Source code changes (`backend/`, `frontend/src/`)
- ✅ Config changes (`.gitignore`, `docs/CLAUDE.md`, `docs/`)
- ✅ Deploy script updates
- ✅ Root configs (`pyproject.toml`, `pyrightconfig.json`, `.gitattributes`)
- ❌ **Never:** `node_modules/`, `.env`, `__pycache__/`, `.deploy_temp_*/`

### What Goes to HF Space (via GitHub Actions)

- ✅ Everything inside `backend/` — Python code, requirements.txt, supervisord.conf, plus root `Dockerfile`.
- ❌ **Not:** `frontend/`, `docs/`, root configs

### What Goes to `gh-pages` (via GitHub Actions)

- ✅ Only `frontend/dist/` after `npm run build`
- ❌ **Not:** source code, backend, docs — only the production build

### Commit Message Format

```text
<type>: <short description>

Types: Fix, Feature, Refactor, Docs, Deploy, Chore
```

### When to Commit

- After a logical unit of work is **tested and verified**
- Never commit broken code to `main`
- Never make 2 commits in 1 minute to "fix the fix"

---

## ⚠️ Code Quality Rules

1. **No deploy without local test.** Run `uvicorn main:app` or at minimum check imports before deploying.
2. **No blind fixes.** If you don't know the root cause, investigate first (check logs, check env vars, check HF settings). Don't guess.
3. **No `print()` in production code.** Use `logger.info/warning/error`.
4. **Imports at the top.** No `from pydantic import BaseModel` in the middle of a file.
5. **CRLF matters.** Shell scripts (`.sh`) must have LF line endings. Use `git config core.autocrlf` or `.gitattributes`.
6. **`select(1)` is invalid in SQLAlchemy 2.0.** Use `text("SELECT 1")` with `from sqlalchemy import text`.
7. **Named React Imports.** Always use `import { FC, useState } from 'react'`. Never use `React.FC`.
8. **UI Animations.** Use `.stagger-in` class for lists and `.skeleton` for loading states.
9. **Interactive Markdown.** Guide content supports `.guide-spoiler` (click to reveal) and `.guide-img` (lightbox).

---

## 🚫 Anti-Patterns (Lessons From This Project)

These mistakes have already been made. **Do NOT repeat them.**

| # | What Happened | Rule |
|---|---|---|
| 1 | Agent used `select(1)` in SQLAlchemy 2.0 — broke init_db() | Always verify API compatibility with the library version in `requirements.txt` |
| 2 | Agent deployed broken code to HF without testing | Never run `tools/deploy-backend.ps1` without local verification |
| 3 | Agent rewrote CLAUDE.md and deleted Session Entry/Exit rules | Never remove existing rules from CLAUDE.md — only add or amend |
| 4 | Agent made 2 commits in 1 minute to fix own mistakes | Test before committing. One commit = one verified change |
| 5 | Agent wrote "nerdzao-elite" everywhere without reading the skill | Do not name-drop skills. Read the SKILL.md or don't mention it |
| 6 | Agent fixed DATABASE_URL parsing without checking HF secrets | Before changing code for an env-var issue, check the actual value first |
| 7 | `entrypoint.sh` saved with CRLF (Windows line endings) | Shell scripts for Linux/Docker MUST use LF. Add `.gitattributes` rule |
| 8 | `print(error_msg)` used in `admin.py` instead of logger | Production code uses `logger`, never `print()` |
| 9 | `from pydantic import BaseModel` placed mid-file (line 60 of admin.py) | All imports go at the top of the file |
| 10 | Leaving heavy video compression on free-tier backend | Do not process heavy media on the API server. Use direct upload or offload. |
| 11 | Using `React.` namespace (Vite 6/React 18 build errors) | Always use named imports (`{ FC, useState }`) to prevent ReferenceErrors in production builds. |
| 12 | Referencing non-existent local fonts in CSS | Use Google Fonts (Outfit) via CDN in `index.html`. Avoid local `@font-face` without files. |
| 13 | Missing indexes on filtered columns | Always index columns used in `WHERE`, `JOIN`, or `ORDER BY`. |
| 14 | Using `backend.` prefix in imports | Use absolute imports relative to `/app` (e.g., `from api import ...`) |
| 15 | Missing `__init__.py` in packages | Always include `__init__.py` in all backend subdirectories |
| 16 | `import inngest.fastapi` | Correct import is `import inngest.fast_api` (with underscore) |
| 17 | `api_path` in Inngest `serve` | Use `serve_path` instead of `api_path` for Inngest FastAPI integration |
| 18 | Missing `INNGEST_SIGNING_KEY` | Set `is_production=False` in `Inngest` client if no key is available on HF |
| 19 | Forgetting `MINIAPP_URL` in Settings | Ensure all Telegram-related env vars are present in `Settings` class |
| 20 | Adding Layui/Bootstrap CDN alongside Tailwind v4 | Global CSS selectors from Layui broke Tailwind cascades, fonts, and button/input styling. **Never add third-party CSS frameworks.** |
| 21 | Not using `startViewTransition()` for navigation | All `navigate()` calls must go through `safeNavigate()` wrapper in `navigation.ts` |

---

## 🛠️ Senior Engineering Standards & Instruction Set

### 1. 🧪 TDD Protocol (MANDATORY)
*Logic-heavy features and bug fixes MUST follow the Three Laws of TDD:*
1. **Law 1**: Write production code ONLY to make a failing test pass.
2. **Law 2**: Write only enough test to demonstrate failure (compile errors = failure).
3. **Law 3**: Write only enough production code to make the test pass.

**The Cycle**:
- **🔴 RED**: Create a test in `backend/tests/` or `frontend/src/__tests__/`. Verify it fails.
- **🟢 GREEN**: Implement the **simplest** solution (YAGNI). No optimization.
- **🔵 REFACTOR**: Improve code quality (naming, duplication, structure). All tests must stay green.

### 2. ⚛️ Frontend Mastery (React/Vite)

1. **Atomic Components**: Components must do ONE thing. Extract complex logic into custom hooks.
2. **Stable Hooks**: Never call hooks inside loops, conditions, or nested functions.
3. **Functional Programming**: Use `fp-ts` for API handling. Treat errors as values (`TaskEither`).
4. **State Management**: 
    - `Server`: React Query (TanStack) for all caching/syncing.
    - `Global`: Zustand (Theme, Auth, Navigation) for app-wide state.
5. **Performance**: Use `React.memo` and `useMemo` sparingly but correctly for heavy subtrees.
6. **Styling**: Vanilla CSS with Design Tokens. No inline styles except for dynamic animations.
- **Accessibility**: All interactive elements must support `keyboard-nav` and respect `prefers-reduced-motion`.

### 3. 🐍 Backend Excellence (FastAPI)

1. **Architecture Integrity**: Endpoints must be lean; all business logic belongs to `services/`.
2. **Strict Typing**: Use Pydantic V2 models for ALL request/response bodies. No raw dicts.
3. **Resilience**: Implement `Retry` with exponential backoff for all external calls (Gemini, HF).
4. **Consistency**: API must return consistent envelopes. Error messages must be user-friendly in `detail`.
5. **Database**: Use SQLAlchemy 2.0 async. Always use `selectinload` for relationships. No N+1 queries.
6. **Observability**: Use structured logging. Include `request_id` in logs for correlation.
    - **Strict Validation**: All incoming data must be sanitized via `nh3` (for HTML) or Pydantic.

### 4. 🛡️ Security & Secret Management
- **Zero-Trust Auth**: 
    - Verify `HMAC` for all TMA requests.
    - Issue short-lived `JWT` (HS256) + `Refresh Token`.
    - Always validate `sub` and `role` claims in middleware.
- **Vulnerability Mitigation**:
    - **No SELECT ***: Always specify columns to reduce memory and prevent leakage.
    - **SQLi**: Use SQLAlchemy's `bindparams` or `text()` with parameters. Never use f-strings for SQL.
    - **Sanitization**: All user HTML must pass through `nh3` with a strict allowlist.
- **Secrets**: NEVER log tokens, passwords, or the `SECRET_KEY`. Use `logging_config.py` filters if necessary.

### 5. 📊 Database Performance
- **Indexing Strategy**: 
    - Create indexes for all columns used in `WHERE`, `JOIN`, and `ORDER BY`.
    - Use `Composite Indexes` for multi-column filters (e.g., `(category_id, updated_at)`).
- **Audit**: Use `EXPLAIN ANALYZE` for any query taking > 100ms.
- **Pagination**: Use `cursor-based` pagination for large lists to ensure stable performance.

---

---

## 🤖 AI Self-Correction Protocol (SC-MANDATORY)

If a task fails or a bug is introduced:
1. **Analyze (AAA)**:
    - **Arrange**: Gather logs, error messages, and current state.
    - **Act**: Identify the single point of failure (Env vs Code vs Infrastructure).
    - **Assert**: Define the fix and the test case that would have caught it.
2. **Systematic Debugging**: Follow the `systematic-debugging` skill. No random trial-and-error.
3. **Sanity Check**: Run `npm run build` or `pytest` before declaring a fix "complete".
4. **Institutional Memory**: If a mistake is recurring, add it to the **🚫 Anti-Patterns** list above.

---

---

## 📐 Architecture Decisions (ADR)

### Why Hugging Face Spaces instead of Render?

- Render free tier has 512MB RAM limit — OOM kills on ffmpeg compression
- HF Spaces provides free Docker hosting with more resources
- HF token is already available for media dataset access
- Single ecosystem: code (HF Spaces) + media (HF Datasets)

### Why HF Datasets instead of Cloudflare R2?

- R2 requires credit card for setup
- HF Datasets is free and integrates with `huggingface_hub` Python SDK
- Public URLs available via `huggingface.co/datasets/.../resolve/main/...`

### Why Supervisord in Docker?

- Single container runs 3 processes: FastAPI API, Telegram Bot, ARQ Worker
- HF Spaces only allows one container per Space
- Supervisord is lightweight and well-proven for multi-process containers

### Why Neon instead of Supabase/PlanetScale?

- Free tier with generous limits
- Native PostgreSQL (no proprietary extensions)
- Connection pooling built-in (important for serverless)

---

## 🛠️ Common Commands

```bash
# Backend Dev (DevContainers — MANDATORY)
# Open project in VS Code DevContainers, then:
make dev-backend    # API на localhost:8000

# Frontend Dev (in a separate terminal inside DevContainer)
cd frontend && npm run dev
```

---

## 📝 Current Status (Last Updated: 2026-08-10)

### Stable baseline
- Auth flow uses short-lived JWT + refresh endpoint (`/api/auth/refresh`) with frontend silent refresh.
- Import pipeline uses Inngest + Gemini and persists guides/media through service layer.
- Deployment is fully automated via GitHub Actions.
- **Docker Architecture**: Root Dockerfiles (dev/prod) fixed to support `backend/` directory structure.
- **Performance**: N+1 issues in `reorder` operations fixed via SQLAlchemy executemany.

### Frontend Stack (August 2026)
- **React 19** + **Vite 6.4** + **TypeScript** + **Tailwind CSS v4** (чистый, без Layui/Bootstrap).
- **Build target**: `es2022`, без production sourcemaps.
- **Vendor chunking**: `vendor-react` (283 кБ), `vendor-motion` (126 кБ), `vendor-charts` (333 кБ), `vendor-tanstack` (36 кБ).
- **Главный JS бандл**: уменьшен с 530 кБ до **152 кБ** (−71.3%).
- **Время сборки**: ~8 секунд (3158 модулей).

### Работы выполненные 10 августа 2026

#### Фаза 1: Удаление Layui и восстановление CSS (`commit ada473e`)
- Удалены Layui CSS/JS CDN из `index.html`.
- Удалён `layui-components` import из `main.tsx` и W3C declarations из `globals.d.ts`.
- Заменены legacy-элементы (`layui-button`, `layui-badge`) на Tailwind в `CyberlinkPopup.tsx` и `DocBlock.tsx`.
- Обновлены CSS-токены тёмной темы: `--background: #0D0E12`, `--foreground: #F9FAFB`, `--muted-foreground: #9CA3AF`, `--primary: #E11D48`.
- Исправлен дублирующийся заголовок в `AdminView.tsx` / `LocalAdminLogin.tsx`.

#### Фаза 2: Оптимизация производительности (`commit 2fd44be`)
- `vite.config.ts`: настроен `manualChunks` для vendor splitting, таргет `es2022`, отключены sourcemaps.
- `SearchView.tsx`: внедрён `useDeferredValue` + `useTransition` для мгновенного отклика поиска.
- `BuildPlannerView.tsx`: внедрён `startTransition` для плавного переключения рангов и навыков.
- `CategoryList.tsx`, `GuildRosterView.tsx`: добавлены `loading="lazy"` + `decoding="async"` на изображения.

#### Фаза 3: Плавная навигация (`commit 37ed8bb`)
- `navigation.ts`: все переходы обёрнуты в `document.startViewTransition()` (View Transitions API).
- `AppLayout.tsx`: добавлен Scroll Restoration — автоматический сброс скролла при смене маршрута.
- `AppRouter.tsx`: обновлён `ViewLoader` на стилизованный Bento-скелетон с `rose-bento-card`.

#### Фаза 4: Полировка UI (`commit a945a5b`)
- Создан `Breadcrumbs.tsx` — навигационные хлебные крошки, интегрирован в `GuideView.tsx`.
- Создан `EmptyState.tsx` — универсальные пустые состояния с кнопками действия, интегрирован в `SearchView`, `FavoritesView`, `HistoryView`.
- Создан `ScrollToTopFab.tsx` — плавающая кнопка «Наверх», интегрирована в `GuideView.tsx`.

### Operational constraints (must be considered in every change)
- HF Spaces free tier has limited CPU/RAM and may degrade under heavy media workflows (do not overload the worker).
- Discord CDN URLs are short-lived; import UX must remain fast and explicit.
- HF Dataset public resolve is eventually consistent (short delay before new media is visible).
- **Никогда не подключать сторонние CSS-фреймворки** (Layui, Bootstrap, etc.) — только чистый Tailwind CSS v4.

### Current technical debt
- Виртуализация длинных списков (TanStack Virtual) — пока не внедрена.
- Subscription System UI (кнопка подписки на категории) — бэкенд готов, фронтенд нет.
- Favicon и OG-картинка — не обновлены под текущий стиль.

### Source of truth for next tasks
- `docs/todo.md` — active backlog and priorities.
- `docs/frontend_enhancement_plan.md` — подробный план с отметками выполненных задач.

---

