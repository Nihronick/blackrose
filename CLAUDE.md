# 🛠️ BLACKROSE: Elite AI Operating System & Project Map

## 🧠 Elite AI Workflow (nerdzao-elite)

1. **Isolation:** NEVER use `git add .` in the root for deployments.
2. **Modular Architecture:**
   - **Frontend:** React source in `frontend/`. Build/Deploy ONLY to GitHub Pages.
   - **Backend:** FastAPI source in `backend/`. Build/Deploy ONLY to Hugging Face Spaces.
3. **Execution:** All deployment tasks MUST use `.deploy_temp_*` isolated folders.

---

## 🗺️ Service Topology

### 🛰️ The Hybrid Cloud Map
| Layer | Service | Deployment Logic |
| :--- | :--- | :--- |
| **Frontend** | GitHub Pages | `frontend/` -> Isolated Build -> `gh-pages` branch |
| **Backend** | HF Spaces | `backend/` -> Isolated Flattening -> `hf_deploy/main` |
| **Media** | HF Datasets | Cloud-native access via `storage.py` (No local files) |
| **Database** | Neon DB | Persistent PostgreSQL (Serverless) |

---

## 🚀 Deployment Protocol

### 1. Backend (Hugging Face)
- **Script:** `.\deploy-backend.ps1`
- **Action:** Creates `.deploy_temp_backend`, copies `backend/*`, injects HF Metadata, force pushes to HF.

### 2. Frontend (GitHub Pages)
- **Script:** `.\deploy-frontend.ps1`
- **Action:** Builds `frontend/dist`, creates `.deploy_temp_frontend`, force pushes to `gh-pages`.

---

## 📂 Directory Topology
- `backend/` - The Brain. All logic, DB, and Bot code.
- `frontend/` - The Face. React UI and assets.
- `scripts/` - Local automation & maintenance.
- `docs/` - Documentation & Snapshots.

---

## 📝 Status & Snapshots
- **2026-05-01:** Structural restoration complete. Root directory cleaned.
- **2026-05-01:** Isolated deployment scripts implemented.
- **Next:** Verify HF Space reaches `Running` state.

---
*Operational Protocol: nerdzao-elite | Project: BlackRose Hybrid*
