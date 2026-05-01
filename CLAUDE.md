# 🛠️ BLACKROSE: Elite AI Operating System & Project Map

## 🧠 AI Workflow & Cognitive Stack (nerdzao-elite style)

Every task MUST follow this elite sequence:
1. **Planning (@concise-planning):** Spec/Plan files in `docs/`.
2. **Architecture:** Verify cross-service impact (HF/GitHub/Neon).
3. **Execution:** Clean, modular code with integrated error handling.
4. **Validation:** Technical & UX check before completion.
5. **Snapshot:** Mandatory handoff update in `docs/snapshots/`.

---

## 🗺️ Project Logic & Service Topology

### 🛰️ The Hybrid Cloud Map

| Layer | Service | Endpoint | Push/Sync Target |
| :--- | :--- | :--- | :--- |
| **Client UI** | GitHub Pages | `nihronick.github.io/blackrose/` | Branch: `gh-pages` |
| **API / Logic** | HF Spaces | `blackrose-backend.hf.space` | Remote: `hf_deploy/main` |
| **Data Layer** | Neon DB | `*.neon.tech` | SQL Migrations (Alembic) |
| **Media CDN** | HF Datasets | `blackrose-media` dataset | `storage.py` (HF Hub API) |
| **AI Layer** | Google Gemini | API | Server-side synthesis |

### 🔄 Data Flow Logic

1. **Guide Synthesis:** Discord -> Backend (HF) -> Gemini (Translation) -> Database (Neon).
2. **Media Path:** Discord Attachment -> Backend -> HF Dataset -> Return CDN URL.
3. **User Access:** Browser -> GitHub Pages -> API Call to HF Space -> Response.

---

## 🚀 Deployment & Branching Matrix

### 1. GitHub `main` (Source of Truth)

- **Content:** All source code (`frontend/`, `backend/`), `scripts/`, `docs/`.
- **Target:** `git push origin main`
- **Rule:** The master repository for collaboration and local development.

### 2. GitHub `gh-pages` (Production Web)

- **Content:** Compiled React build (`dist/`).
- **Target:** `.\deploy-frontend.ps1`
- **Rule:** Automated overwrite. Never edit manually.

### 3. Hugging Face `main` (Production API)

- **Content:** `backend/` folder ONLY + root configs.
- **Target:** `.\deploy-backend.ps1`
- **Rule:** Lean deployment via orphan branch to save space.

---

## 📂 Directory Topology

- `backend/` - FastAPI, Routers, Models. **Self-contained.** `.gitignore` inside.
- `frontend/` - React, Vite, Tailwind. **Self-contained.** `.gitignore` inside.
- `scripts/` - Maintenance scripts. **Local only.** `.gitignore` inside.
- `docs/` - Specs, Plans, Snapshots. **Obsidian-ready.**
- `.agents/` - AI Skills & configurations. **DO NOT COMMIT.**

---

## 📝 Current Snapshot (Last Update: 2026-05-01)

- **Status:** Architecture migration and total cleanup COMPLETED.
- **Security:** Secret scanning verified. No tokens in Git history.
- **Next Goal:** Integration test for new Discord Lab media pipeline.

---

## 🤖 Elite AI Rules (STRICT)

1. **Local Gitignores:** Respect folder-level rules. Do not move them to root.
2. **Media Storage:** NEVER use local filesystem for guides. Use `storage.py`.
3. **API Config:** Frontend MUST use `VITE_API_URL` pointing to HF Space.
4. **Cleanliness:** Delete any temp or unused files immediately after task.
5. **Integrity:** Preserve this `CLAUDE.md` structure in all future updates.

---

*Operational Protocol: nerdzao-elite | Project: BlackRose Hybrid*
