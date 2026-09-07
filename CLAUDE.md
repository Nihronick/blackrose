# 🌹 BlackRose — AI Agent Guidelines & Architecture

Knowledge Hub & Community Platform for Slayer Legend.
Frontend: React 18 + Vite 6 + TypeScript + Tailwind CSS v4 + Telegram Mini App SDK.
Backend: FastAPI + SQLAlchemy 2.0 Async + Neon.tech PostgreSQL + Upstash Redis.
Pipeline: 8-stage ETL with AI Translation (Discord -> Web/TMA).

---

## ⚡ Quick Facts & Commands

### Frontend (`frontend/`)
```bash
cd frontend
npm run dev          # Start local dev server (port 3000 / 5173)
npm run test         # Run unit tests with Vitest (139+ tests)
npm run lint         # Biome check src/
npm run lint:fix     # Biome check & auto-fix src/
npm run build        # Production Vite build + PWA service worker
npx tsc --noEmit     # TypeScript type-checking
```

### Backend (`backend/`)
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
python -m pytest tests/ -v                       # Run backend test suite (106+ tests)
ruff check .                                    # Lint backend
ruff format .                                   # Format backend
alembic upgrade head                            # Run DB migrations
```

### Pipeline (`pipeline/`)
```bash
python -m pytest pipeline/tests/ -v              # Run ETL unit tests
python -m pipeline.run                          # Run full 8-stage ETL pipeline
```

### E2E Testing (`e2e/`)
```bash
cd e2e
npx playwright test                             # Run Playwright E2E tests
```

---

## 🏗️ Key Architecture & Directory Structure

```
blackrose/
├── CLAUDE.md                 # Root AI memory & quick standards
├── docs/                     # Comprehensive architecture, guides & swarm docs
│   └── CLAUDE.md             # Deep-dive 700+ line swarm protocol & guidelines
├── .claude/                  # Claude Code / Agent infrastructure
│   ├── settings.json         # Tool hooks, auto-formatting & branch protections
│   ├── agents/               # Specialized AI agents (code-reviewer, guide-auditor)
│   ├── commands/             # Custom slash commands (/audit, /review)
│   └── skills/               # Domain skills (slayer-glossary, blackrose-standards, testing-patterns)
├── backend/                  # FastAPI asynchronous microservice
│   ├── api/                  # Routers (public, admin, guilds, discord_sync, webhook_ingest)
│   ├── core/                 # Auth (HMAC/JWT), DB engine, Config, Logging (structlog), Cache
│   ├── models/               # db_models.py (SQLAlchemy 2.0), schemas.py (Pydantic v2)
│   └── services/             # Domain services (guides, guilds, media, storage, notifications)
├── frontend/                 # React 18 SPA / Telegram Mini App
│   ├── src/
│   │   ├── app/              # AppProvider, AppRouter, AppLayout
│   │   ├── components/       # Shared UI components (ReadingProgressBar, Breadcrumbs, etc.)
│   │   ├── features/         # Modular features (admin, categories, guide)
│   │   ├── hooks/            # TanStack Query & custom hooks (useFavorites, useSubscriptions)
│   │   ├── lib/              # API clients, navigation, icons, utils
│   │   ├── store/            # Zustand global state (theme, language, user, cats)
│   │   └── views/            # Screen views (Home, Guide, Categories, Search, Profile)
├── pipeline/                 # 8-stage ETL pipeline from Discord to PostgreSQL
└── e2e/                      # Playwright E2E tests & k6 load scenarios
```

---

## 🚨 Critical Engineering Rules (2026 Standards)

1. **Strict TypeScript:**
   - NEVER use `// @ts-nocheck` or `// @ts-ignore`. Fix the underlying types.
   - NEVER use `any`. Use `unknown` with type guards or create explicit interfaces.
   - Use named imports from `'react'` (e.g. `import { useState, type FC, type RefObject } from 'react'`). NEVER use `React.FC` or `React.RefObject`.
2. **Backend Code Quality:**
   - ALL imports must be at the TOP of the file. No mid-file imports inside functions (unless flagged with `# deferred import: circular dependency`).
   - ALL Pydantic models belong in `models/schemas.py`. Router files must import from `models.schemas`.
   - Logging MUST use `structlog` (`structlog.get_logger(__name__)`). Never use `loguru` or raw `print()`.
   - Use `hmac.compare_digest()` for constant-time comparisons of secrets, tokens, and hashes.
   - Use non-blocking async operations (`scan_iter` for Redis, `httpx` for HTTP requests).
3. **State Management & UI States:**
   - State order for components: **Error -> Loading (no data) -> Empty -> Success**.
   - Always provide empty states (`EmptyState` component) and error states.
   - Keep theme tokens synchronized with `index.css` (OKLCH color system).
