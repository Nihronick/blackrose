# 🛠️ BlackRose: Project Guidelines & AI Context Management

## 🧠 Context Persistence (CRITICAL)

This project uses a "Snapshot & Handoff" system to ensure continuity between AI sessions.

### 1. Skill Selection (MANDATORY — Read Before Coding)

Before starting ANY task, match it to the table below and **read the SKILL.md file** via `view_file`.
Do NOT name-drop skills. Either read and follow them, or don't mention them.

#### 🔧 Debugging & Troubleshooting

| Trigger | Skill | Path |
|---|---|---|
| Bug, crash, unexpected behavior | `systematic-debugging` | `skills/systematic-debugging/SKILL.md` |
| General debugging approach | `debugger` | `skills/debugger/SKILL.md` |

#### 🐍 Backend (FastAPI / Python)

| Trigger | Skill | Path |
|---|---|---|
| API design decisions | `api-patterns` | `skills/api-patterns/SKILL.md` |
| Backend architecture | `backend-architect` | `skills/backend-architect/SKILL.md` |
| Pydantic models | `pydantic-models-py` | `skills/pydantic-models-py/SKILL.md` |

#### ⚛️ Frontend (React / TypeScript)

| Trigger | Skill | Path |
|---|---|---|
| React hooks, composition, state | `react-patterns` | `skills/react-patterns/SKILL.md` |
| Tailwind CSS v4 patterns | `tailwind-patterns` | `skills/tailwind-patterns/SKILL.md` |
| Component performance issues | `react-component-performance` | `skills/react-component-performance/SKILL.md` |

#### 🗄️ Database (PostgreSQL / SQLAlchemy)

| Trigger | Skill | Path |
|---|---|---|
| Schema design, indexing | `database-design` | `skills/database-design/SKILL.md` |
| SQL, migrations, queries | `database` | `skills/database/SKILL.md` |

#### 🚀 Deployment & DevOps

| Trigger | Skill | Path |
|---|---|---|
| PowerShell scripts (Windows) | `powershell-windows` | `skills/powershell-windows/SKILL.md` |
| Shell scripts (.sh, Docker) | `bash-scripting` | `skills/bash-scripting/SKILL.md` |
| GitHub CLI, PRs, Actions | `github` | `skills/github/SKILL.md` |

#### 📝 Documentation & Planning

| Trigger | Skill | Path |
|---|---|---|
| Writing docs, READMEs | `documentation` | `skills/documentation/SKILL.md` |
| Creating task plans | `concise-planning` | `skills/concise-planning/SKILL.md` |
| Implementation plans | `writing-plans` | `skills/writing-plans/SKILL.md` |

#### 🔒 Security & Code Quality

| Trigger | Skill | Path |
|---|---|---|
| Security review | `security-auditor` | `skills/security-auditor/SKILL.md` |
| AI-generated code audit | `vibe-code-auditor` | `skills/vibe-code-auditor/SKILL.md` |
| Code review before merge | `requesting-code-review` | `skills/requesting-code-review/SKILL.md` |
| Verify work is complete | `verification-before-completion` | `skills/verification-before-completion/SKILL.md` |

#### 🧪 Testing

| Trigger | Skill | Path |
|---|---|---|
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

### 4. Project Brain (Memory Map)

| Document | Purpose |
|---|---|
| `CLAUDE.md` | Rules, state, architecture — **read first** |
| `docs/todo.md` | Pending tasks |
| `docs/snapshots/` | Session history and handoff notes |
| `docs/plans/` | Migration/feature plans |

---

## 🏗️ Hybrid Infrastructure

| Component | Hosting | Technology | Purpose |
|---|---|---|---|
| **Frontend** | GitHub Pages | React 18, Vite, Tailwind 4, TypeScript | Client UI & Content Rendering |
| **Backend** | HF Spaces | FastAPI, SQLAlchemy Async, Docker | API, Telegram Bot, ARQ Worker |
| **Database** | Neon | PostgreSQL (Serverless, Pooled) | Guides, Categories, Users, History |
| **Media** | HF Datasets | `huggingface_hub` API | Icons, Images, Videos |
| **Cache** | Upstash | Redis (Optional) | Response caching |
| **Monitoring** | Honeybadger | Error tracking (Optional) | Production error alerts |

---

## 📂 File Map (What Does What)

### Backend (`backend/`) → Deploys to **Hugging Face Spaces**

```text
backend/
├── main.py              — FastAPI app, lifespan, CORS, routers
├── database.py          — SQLAlchemy engine, init_db(), all DB queries
├── db_models.py         — ORM models (Guide, Category, Member, etc.)
├── models.py            — Pydantic request/response schemas
├── dependencies.py      — Auth (require_admin, JWT, Telegram validation)
├── storage.py           — HF Dataset media upload/download (replaces R2)
├── cache.py             — Redis cache layer (optional)
├── utils.py             — Telegram notifications, icon syntax helpers
├── icons.py             — Game icon mappings (Slayer Legend assets)
├── limiter.py           — Rate limiting config (SlowAPI)
├── logging_config.py    — Structured logging setup
│
├── routers/
│   ├── public.py        — Public API: guides, categories, search, comments
│   └── admin.py         — Admin API: CRUD, upload, translate, stats, media
│
├── services/
│   └── notification_service.py — Guide notification queue (ARQ/Redis)
│
├── workers/
│   └── notify.py        — ARQ background worker for notifications
│
├── bot/                 — Telegram Bot (aiogram 3)
│   ├── main.py          — Bot startup (webhook/polling)
│   ├── config.py        — Bot environment config
│   ├── handlers/
│   │   ├── miniapp.py   — /start, inline keyboards, mini-app launch
│   │   ├── admin.py     — /add_user, /add_admin, /members
│   │   └── errors.py    — Global error handler
│   ├── lib/
│   │   └── api_client.py — HTTP client for internal API calls
│   └── middleware/
│       └── admin.py     — Admin-only message filter
│
├── migrations/          — Alembic (async, PostgreSQL)
│   ├── env.py           — Migration runner (uses DATABASE_URL)
│   └── versions/        — 0001..0004 schema migrations
│
├── experiments/         — Experimental features (discord_sync)
│
├── Dockerfile           — Production container (API + Bot + Worker)
├── entrypoint.sh        — Startup: migrations → supervisord
├── supervisord.conf     — Process manager: api, bot, worker
├── alembic.ini          — Alembic config (script_location = migrations)
├── requirements.txt     — Python dependencies
└── README.md            — HF Space metadata (YAML frontmatter)
```

### Frontend (`frontend/`) → Deploys to **GitHub Pages**

```text
frontend/
├── src/
│   ├── App.tsx          — Root component, routing, theme
│   ├── main.tsx         — React entry point
│   ├── views/           — Page-level components (Admin, Guide, Categories...)
│   ├── features/        — Feature modules (admin/, categories/)
│   ├── components/      — Shared UI components
│   ├── hooks/           — Custom React hooks
│   ├── store/           — State management
│   ├── lib/             — API client, utilities
│   └── index.css        — Global styles
├── .env                 — Local env (VITE_API_URL, VITE_BOT_NAME)
├── vite.config.ts       — Vite build config
└── package.json         — Dependencies
```

### Root (repo management — NOT deployed)

```text
./
├── docs/
│   ├── CLAUDE.md        — THIS FILE. AI context and rules.
│   ├── todo.md          — Task tracking
│   ├── plans/           — Migration/feature plans
│   ├── snapshots/       — Session handoff summaries
│   └── specs/           — Feature specifications
├── README.md            — Public project description
├── deploy-backend.ps1   — Isolated backend deploy script
├── deploy-frontend.ps1  — Isolated frontend deploy script
├── scripts/             — Local-only automation (import, cleanup, sync)
└── pyrightconfig.json   — IDE type checking config
```

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
| `GEMINI_API_KEY` | ❌ | Google Gemini for AI translation |
| `PORT` | auto | Set by HF to `7860` |

### Frontend `.env` (Local / Build Time)

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://nihronick-blackrose-backend.hf.space` |
| `VITE_BOT_NAME` | `blackrosesl1_bot` |

---

## 🔗 URLs & Access (Production)

| Service | URL |
|---|---|
| **Frontend (live)** | `https://nihronick.github.io/blackrose/` |
| **Backend API** | `https://nihronick-blackrose-backend.hf.space` |
| **HF Space Settings** | `https://huggingface.co/spaces/Nihronick/blackrose-backend/settings` |
| **HF Space Logs** | `https://huggingface.co/spaces/Nihronick/blackrose-backend` → Factory Logs |
| **GitHub Repo** | `https://github.com/Nihronick/blackrose` |
| **Neon Console** | `https://console.neon.tech/` |
| **HF Media Dataset** | `https://huggingface.co/datasets/Nihronick/blackrose-media` |

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
# Backend Dev
cd backend && uvicorn main:app --reload --port 8000

# Frontend Dev
cd frontend && npm run dev

# Run Alembic migration locally
cd backend && alembic upgrade head

# Check what would be deployed
git diff HEAD

# Deploy
.\deploy-backend.ps1
.\deploy-frontend.ps1
```

---

## 📝 Current Status (Last Updated: 2026-05-01)

### Recent Changes
- Migrated from Render to Hugging Face Spaces (Docker).
- Media storage moved to HF Datasets (cloud-native, no local files).
- Deploy scripts rewritten with isolated temp directories.
- Modular `.gitignore` structure (per-directory).
- Admin media management uses HF API instead of local filesystem.
- CLAUDE.md fully rebuilt: file map, env vars, skills, anti-patterns, ADR.

### Code Audit Fixes (2026-05-01)
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
- ✅ Hardened CORS regex: `*.github.io` → `nihronick.github.io` only.

### Known Issues
- `password_hash` column is `String(128)` — should be `String(256)` or `Text` (needs migration).
- `storage.py` uses blocking `subprocess.run()` for ffmpeg — should use `asyncio.create_subprocess_exec`.
- `reorder_categories/guides` — N+1 UPDATE queries (low priority, small data).

### Next Steps
1. Verify DATABASE_URL secret format in HF Space settings.
2. Redeploy backend and confirm "Database connection verified" in logs.
3. Create Alembic migration for `password_hash` column width.
4. Convert `subprocess.run()` to async in `storage.py`.

---

<!-- Last agent: Claude Opus 4.6 | Session: 2026-05-01 -->
