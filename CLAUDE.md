# 🛠️ Project Guidelines & AI Context Management

## 🧠 Context Persistence (CRITICAL)
This project uses a "Snapshot & Handoff" system to ensure continuity between AI sessions.

### 1. Autonomous Skill Selection
- **Mandatory First Step:** For every user request, the agent MUST independently determine if a specialized skill is needed.
- **Library Check:** Scan `.agents/skills/` for local skills.
- **Methodology:** Default to `gsd` (Spec-driven development) for features and complex tasks.
- **Self-Installation:** Authorized to use `skill-orchestrator` to install needed skills.

### 2. Session Exit (MANDATORY)
Before ending the session, every AI agent MUST:
1. Update **Current Status** in this `CLAUDE.md`.
2. Update `docs/todo.md`.
3. Create a **Snapshot** in `docs/snapshots/YYYY-MM-DD_HHMM_summary.md`.

---

## 🏗️ Hybrid Infrastructure (BlackRose)
BlackRose is a modern, high-performance platform for Slayer Legend.

| Component | Hosting | Technology | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend** | GitHub Pages | React 18, Vite, Tailwind 4 | Client UI & Content Rendering |
| **Backend** | HF Spaces | FastAPI (Docker) | API, Discord Lab, Telegram Bot |
| **Database** | Neon | PostgreSQL | Guides, Categories, Users |
| **Media** | HF Datasets | Cloud Storage | Icons, Images, Videos |

### 🚀 Deployment Rules
1. **Backend (HF):** Use `deploy-backend.ps1`. Push ONLY `backend/`, `README.md`, `CLAUDE.md`. NEVER push frontend/docs/scripts/assets.
2. **Frontend (GitHub):** Use `deploy-frontend.ps1`. Deploy only the `dist/` folder to `gh-pages`.
3. **Media:** All production assets must be in `blackrose-media` dataset.

---

## 📂 Project Structure
- `backend/` - API & Bot source. (HF Deploy)
- `frontend/` - React source. (GitHub Deploy)
- `scripts/` - Local automation & cleanup.
- `docs/` - Specs, Plans, Snapshots (Obsidian-ready).
- `.agents/` - Local AI skills.

---

## 📝 Current Status (Last Updated: 2026-05-01)
- **Migration:** Completed from Render to Hugging Face Spaces.
- **Storage:** Icons and legacy media migrated to HF Datasets.
- **Cleanup:** Unused assets removed, system folders excluded from Git.
- **Automation:** Created `deploy-backend.ps1` and `deploy-frontend.ps1`.

---

## 🛠️ Common Commands
- **Backend Dev:** `cd backend && uvicorn main:app --reload --port 8000`
- **Frontend Dev:** `cd frontend && npm run dev`
- **Asset Cleanup:** `python scripts/cleanup_unused_assets.py`
