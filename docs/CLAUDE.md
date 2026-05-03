# 🛠️ BlackRose: Project Guidelines & AI Context Management

## 🧠 Context Persistence (CRITICAL)

This project uses a "Snapshot & Handoff" system to ensure continuity between AI sessions.

### 1. Skill Selection (MANDATORY — Read Before Coding)

Before starting ANY task, match it to the table below and **read the SKILL.md file** via `view_file`.
Do NOT name-drop skills. Either read and follow them, or don't mention them.

#### 🔧 Debugging & Troubleshooting

| Trigger | Skill | Path |
| --- | --- | --- |
| Bug, crash, unexpected behavior | `systematic-debugging` | `skills/systematic-debugging/SKILL.md` |
| General debugging approach | `debugger` | `skills/debugger/SKILL.md` |

#### 🐍 Backend (FastAPI / Python)

| Trigger | Skill | Path |
| --- | --- | --- |
| API design decisions | `api-patterns` | `skills/api-patterns/SKILL.md` |
| Backend architecture | `backend-architect` | `skills/backend-architect/SKILL.md` |
| Pydantic models | `pydantic-models-py` | `skills/pydantic-models-py/SKILL.md` |

#### ⚛️ Frontend (React / TypeScript)

| Trigger | Skill | Path |
| --- | --- | --- |
| React hooks, composition, state | `react-patterns` | `skills/react-patterns/SKILL.md` |
| **Named Imports Only** | (Internal Rule) | **Avoid `React.` namespace (use `{ FC, useState }`)** |
| Tailwind CSS v4 patterns | `tailwind-patterns` | `skills/tailwind-patterns/SKILL.md` |
| Component performance issues | `react-component-performance` | `skills/react-component-performance/SKILL.md` |

#### 🗄️ Database (PostgreSQL / SQLAlchemy)

| Trigger | Skill | Path |
| --- | --- | --- |
| Schema design, indexing | `database-design` | `skills/database-design/SKILL.md` |
| SQL, migrations, queries | `database` | `skills/database/SKILL.md` |

#### 🚀 Deployment & DevOps

| Trigger | Skill | Path |
| --- | --- | --- |
| PowerShell scripts (Windows) | `powershell-windows` | `skills/powershell-windows/SKILL.md` |
| Shell scripts (.sh, Docker) | `bash-scripting` | `skills/bash-scripting/SKILL.md` |
| GitHub CLI, PRs, Actions | `github` | `skills/github/SKILL.md` |

#### 📝 Documentation & Planning

| Trigger | Skill | Path |
| --- | --- | --- |
| Writing docs, READMEs | `documentation` | `skills/documentation/SKILL.md` |
| Creating task plans | `concise-planning` | `skills/concise-planning/SKILL.md` |
| Implementation plans | `writing-plans` | `skills/writing-plans/SKILL.md` |

#### 🔒 Security & Code Quality

| Trigger | Skill | Path |
| --- | --- | --- |
| Security review | `security-auditor` | `skills/security-auditor/SKILL.md` |
| AI-generated code audit | `vibe-code-auditor` | `skills/vibe-code-auditor/SKILL.md` |
| Code review before merge | `requesting-code-review` | `skills/requesting-code-review/SKILL.md` |
| Verify work is complete | `verification-before-completion` | `skills/verification-before-completion/SKILL.md` |

#### 🧪 Testing

| Trigger | Skill | Path |
| --- | --- | --- |
| TDD workflow | `tdd-workflow` | `skills/tdd-workflow/SKILL.md` |
| Browser/E2E testing | `webapp-testing` | `skills/webapp-testing/SKILL.md` |

#### ⚡ Default Methodology

- **New features:** Read `writing-plans` → plan first, code second.
- **Bug fixes:** Read `systematic-debugging` → diagnose first, fix second.
- **Refactoring:** Read `vibe-code-auditor` → audit first, refactor second.
- **Before any deploy:** Read `verification-before-completion`.

### 2. Session Entry

- **Read `CLAUDE.md`** first for the current project status and rules.
- **Check `docs/todo.md`** to understand pending tasks.
- **Review the last 2-3 files in `docs/snapshots/`** to understand the "why" behind recent changes.

### 3. Session Exit (MANDATORY)

Before ending the session, every AI agent MUST:

1. **Update the "Current Status"** section at the bottom of this file.
2. **Update `docs/todo.md`** (mark finished tasks, add new ones).
3. **Create a Snapshot:** Save a summary to `docs/snapshots/YYYY-MM-DD_HHMM_summary.md`. Include:
   - Main changes made.
   - Technical debt or bugs discovered.
   - Specific instructions for the next agent.

### 4. 🧠 Project Brain: Principal-Level Architecture

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
2. **Setup**: Run `.\deploy-backend.ps1` (backend) and `.\deploy-frontend.ps1` (frontend) locally to understand the build chain.
3. **Architecture**: Review `backend/database.py` (Neon DB) and `frontend/src/store/` (Zustand).
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
├── trash/               — Deprecated files
└── Dockerfile           — Development & Production Container
```
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
- **Persistence (`database.py`, `db_models.py`)**: Async SQLAlchemy 2.0 with Neon.tech (PostgreSQL). Uses `selectinload` for relationship hydration to prevent N+1.
- **Media Engine (`storage.py`)**: Abstracted interface to Hugging Face Datasets. Handles multi-part uploads and CDN resolution.
- **Security (`dependencies.py`)**: 
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

### Rule #1: Isolation

**NEVER** use `git add .` in the project root for deployments.
All deployments use isolated `.deploy_temp_*` directories.

### Backend → Hugging Face Spaces

- **Script:** `.\deploy-backend.ps1`
- **What happens:** Creates `.deploy_temp_backend/`, copies `backend/*` into it, `git init`, force pushes to HF.
- **Target:** `https://huggingface.co/spaces/Nihronick/blackrose-backend`

### Frontend → GitHub Pages

- **Script:** `.\deploy-frontend.ps1`
- **What happens:** Runs `npm install && npm run build` in `frontend/`, copies `dist/*` to `.deploy_temp_frontend/`, force pushes to `gh-pages`.
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
                    │  scripts/   ← automation │
                    └────────┬────────┬────────┘
                             │        │
                    deploy-  │        │  deploy-
                    backend  │        │  frontend
                    .ps1     │        │  .ps1
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

**Правило:** Весь код коммитится в `main`. Деплой-скрипты **сами** извлекают нужную часть и пушат в целевой репозиторий. Никогда не пушить `main` напрямую в HF или `gh-pages`.

### What Gets Committed to `main`

- ✅ Source code changes (`backend/`, `frontend/src/`)
- ✅ Config changes (`.gitignore`, `docs/CLAUDE.md`, `docs/`)
- ✅ Deploy script updates
- ✅ Root configs (`pyproject.toml`, `pyrightconfig.json`, `.gitattributes`)
- ❌ **Never:** `node_modules/`, `.env`, `__pycache__/`, `.deploy_temp_*/`

### What Goes to HF Space (via `deploy-backend.ps1`)

- ✅ Everything inside `backend/` — Python code, Dockerfile, requirements.txt, supervisord.conf
- ❌ **Not:** `frontend/`, `docs/`, `scripts/`, root configs

### What Goes to `gh-pages` (via `deploy-frontend.ps1`)

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
| 2 | Agent deployed broken code to HF without testing | Never run `deploy-backend.ps1` without local verification |
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
| 13 | Using `SELECT *` in production code | Explicitly specify columns to avoid memory overhead and accidental data leakage. |
| 14 | Missing indexes on filtered columns | Always index columns used in `WHERE`, `JOIN`, or `ORDER BY`. |

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
# Backend Dev (Local)
cd backend && uvicorn main:app --reload --port 8000

# Backend Dev (Docker — Recommended for Windows)
docker-compose up --build

# Управление файлами через Docker (если нужно удалить заблокированные файлы)
docker exec -it blackrose-backend-1 rm -rf trash/Header.test.tsx

# Frontend Dev
cd frontend && npm run dev
```

---

## 📝 Current Status (Last Updated: 2026-05-03, Session 4)

### 💎 Senior Infrastructure & Discovery (Session 4)
- ✅ Discovery Layer: Added horizontal "Categories" scroll to HomeDashboard.
- ✅ Admin Core: Implemented `AdminAuthService` for local credentials.
- ✅ Inngest Flow: Integrated `discord_lab_service` with background workers.

### 🧹 Code Cleanup & Refactoring (Session 5 - Current)
- ✅ **Dead Code Removal**: Soft-deleted legacy experimental scripts in `trash/`, `experiments/`, and redundant glossaries.
- ✅ **Scripts Audit**: Deprecated 30+ legacy migration scripts in `scripts/` folder.
- ✅ **Architecture Fixes**:
    - Fixed missing `os` import in `backend/core/config.py`.
    - Cleaned up unused imports in `backend/api/admin.py`.
    - Implemented `CategoryService.delete` logic in service layer.
    - Updated admin route to use proper service-layer deletion and cache invalidation.
- ✅ **Frontend Organization**: Relocated test files from `components/` to dedicated `test/` directory.
- ✅ **Consistency**: Synchronized Discord emoji mapping logic across all services.
- ✅ **Premium Sharing**: Upgraded `ShareButton` with native Web Share API support.
- ✅ **Senior Docs Upgrade**: Applied `wiki-architect` & `senior-architect` standards to `CLAUDE.md`.

### Recent Changes (Session 3)

- ✅ **JWT Exchange Strategy**: Implemented TMA-to-JWT conversion for stable cross-platform sessions.
- ✅ **Extended Environment Metadata**: Added platform, version, and colorScheme to global store.
- ✅ **Hybrid Core Architecture**: Robust separation and lifecycle management via `AppEnvProvider`.
- ✅ **Instant Theme Sync**: Automatic UI reaction to Telegram theme changes.
- ✅ **Adaptive UI Layer**: Context-aware headers, buttons, and ErrorBoundaries.
- ✅ **Bulletproof Navigation**: Native BackButton logic with reliable fallback.
- ✅ **Redis Optimization**: Increased ARQ worker `poll_delay` to 10.0s.
- ✅ **Adaptive UI Layer**: Context-aware headers, buttons, and ErrorBoundaries.
- ✅ **Process Consolidation**: Integrated Telegram Bot (aiogram) into FastAPI lifespan.
- ✅ **Stable Webhooks**: Configured automated webhook setup with secret token validation for HF Spaces.
- ✅ **Unified Requirements**: Merged backend and bot dependencies for cleaner Docker builds.

### Code Audit Fixes (2026-05-01, Session 1)

- ✅ Fixed `select(1)` → `text("SELECT 1")` in `database.py` (Anti-Pattern #1).
- ✅ Fixed `entrypoint.sh` CRLF → LF line endings (Anti-Pattern #7).
- ✅ Created `.gitattributes` with `*.sh text eol=lf`.
- ✅ Fixed JWT `_jwt_encode` empty key vulnerability in `dependencies.py`.
- ✅ Added `ffmpeg` to Dockerfile for video compression.
- ✅ Replaced `print()` with `logger.error()` in `admin.py` (Anti-Pattern #8).
- ✅ Replaced `traceback.print_exc()` with `logger.error(..., exc_info=True)`.
- ✅ Moved `ImportMediaIn` from mid-file to `models.py` (Anti-Pattern #9).
- ✅ Updated `.env.example` — removed R2/Cloudflare, added HF_TOKEN/HF_DATASET_REPO.
- ✅ Removed unused deps: `aioboto3`, `psycopg2-binary`, `sqlalchemy-utils`.
- ✅ Hardened CORS regex: `nihronick.github.io` only.
- ✅ Fixed token leakage in `storage.py` and `admin.py` error logs.
- ✅ Added config diagnostics for `HF_DATASET_REPO` (token detection).
- ✅ Improved `deploy-backend.ps1` with `HF_TOKEN` auth support.
- ✅ Implemented comprehensive Guide & Media deletion logic (cleanup in HF Dataset).
- ✅ Added manual media deletion to Admin Library UI.
- ✅ Migrated `storage.py` to async `ffmpeg` execution.

### 2026-05-01 (Session 2): Backend Premium Evolution

- **Database Performance**: Added indexes to `sort_order`, `views`, and `updated_at` for high-speed sorting.
- **Query Optimization**: Refactored `admin_stats` to use a single query instead of 5 separate ones.
- **Service Architecture**: Created `TranslationService` to modularize multi-provider (HF/Gemini/Google) translation logic.
- **Reliability**: Implemented robust temp file cleanup using `finally` blocks in media import.
- **UX**: Relaxed `nh3` sanitization to allow basic formatting (`<b>`, `<i>`, `<code>`) in comments.
- **Fixes**: Resolved missing `Request` and `JSONResponse` imports in the global exception handler.

### 2026-05-01 (Session 3): Validation & Accessibility Hardening

- **Documentation**: Created `docs/TESTING.md` with a comprehensive 6-point validation protocol.
- **Accessibility**: Integrated `MotionConfig` to globally respect `prefers-reduced-motion` for all animations.
- **API Resilience**: Enhanced `apiFetch` error handling to correctly parse and display FastAPI validation detail lists.
- **UI Consistency**: Verified end-to-end markdown-to-video hydration for premium media playback.

### Ultimate Hybrid Core Hardening (2026-05-01, Session 2) — DONE 💎

- ✅ **Security**: Implemented HMAC-SHA256 TMA validation & Security Headers middleware.
- ✅ **Auth**: Added JWT Refresh tokens and environment-aware logout logic.
- ✅ **Reliability**: Integrated Telegram Error Alerts and structured JSON logging (X-Forwarded-For support).
- ✅ **Performance**: Added CSS/HTML Skeletons and SEO Open Graph meta tags.
- ✅ **Observability**: Upgraded `/health` with deep DB/Redis checks and added Pytest suite.
- ✅ **Documentation**: Created `docs/RISKS.md`, `CHANGELOG.md`, and upgraded `README.md`.

### 2026-05-02 (Session 1): Premium Frontend Evolution 💎

- ✅ **Named Imports Migration**: Systemic refactor of all components to remove `React.` namespace dependencies.
- ✅ **Build Stability**: Resolved Vite 6 production build failures and chunking issues.
- ✅ **UI WOW Factor**: Implemented staggered animations (`stagger-in`) and premium skeleton shimmer.
- ✅ **Interactive Content**: Added interactive spoiler reveals and lightbox support for all in-text images.
- ✅ **Typography & Aesthetics**: Modernized guide content with premium quotes, headers, and code styles.
- ✅ **API Reliability**: Fixed cache clearing logic by migrating from GET to POST for sensitive admin actions.

### Known Issues

- `reorder_categories/guides` — N+1 UPDATE queries (low priority).
- Discord CDN links expire quickly — user should import within 5-10 mins of "Prepare".
- Hugging Face Spaces free-tier resource limits (see `docs/RISKS.md`).

### Status: PREMIUM EVOLUTION 💎 (10/10)

- **Architecture:** Enterprise-grade named imports and environment-aware modules.
- **Backend:** Stable webhook integration, optimized DB indexes, and robust media handling.
- **Frontend:** State-of-the-art animations, interactive markdown content, and pixel-perfect aesthetics.

---

<!-- Last agent: Antigravity | Session: 2026-05-03 14:10 | Status: Inngest & Gemini AI Synthesis Integrated -->

### 💎 Modernization & Automation (Session 5)
- ✅ **Inngest Integration**: Added background job orchestration for complex workflows.
- ✅ **Gemini 1.5 Flash**: Integrated AI synthesis for automated Discord guide imports.
- ✅ **Glossary System**: Centralized `backend/core/glossary.json` for terminology consistency (EN/RU).
- ✅ **Observability**: Optimized logging for HF Spaces with Rotating File support.
- ✅ **Infrastructure Hardening**: Switched to standard PyJWT, implemented full-text search (FTS), and aiohttp session pooling.
- ✅ **Documentation Sync**: Consolidated architectural updates into `docs/` folder.

### 💎 Production Hardening (Session 6 - Current)
- ✅ **Media Optimization**: Integrated `imgproxy` for on-the-fly resizing and WebP conversion.
- ✅ **Wiki Git-Sync**: Implemented `GitSyncService` for automated .md backups to GitHub.
- ✅ **Architectural Purge**: Moved all deployment scripts to `/tools/` and cleaned root directory.
- ✅ **Content Strategy**: Prepared architecture for `Directus` headless CMS integration.
- ✅ **Resilience**: Added non-blocking background tasks for secondary services (Git-Sync).
