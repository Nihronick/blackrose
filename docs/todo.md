# 📋 Project TODO

## 🚀 Priority: High
- [x] Verify Admin Panel stability (fixed stats/analytics and missing view_logs table).
- [x] Implement Backend Proxy for Discord Media (bypass CORS policy).
- [x] Implement/Fix Guide deletion logic.
- [x] Simplify Backend Storage (Remove CPU-heavy video compression).
- [x] Optimize Frontend (Remove complex animations and universal transitions).
- [x] **Stabilize TMA Navigation** (Fixed Back button, double header, and redundant FAB).
- [x] **Premium UI Evolution**: Staggered animations, interactive spoilers, and lightbox.
- [x] **Architecture Hardening**: Named imports refactor and environment-aware modules.
- [x] **SEO & Discovery**: Implement `/api/sitemap.xml` for discovery.
- [x] **Search UX**: Local search history persistence.
- [x] **Featured Content**: Horizontal category scroll on HomeDashboard.
- [x] **Premium Video Player** (Custom UI, PiP, Looping, Hydration).
- [x] **Fix Frontend Rendering** (Height calculation & Card import error).

## 🛠️ Features & Improvements
- [x] Clean up redundant Graphify files (Verified removed).
- [x] Add `/health` endpoint to FastAPI for monitoring.
- [x] Implement automated icon downloader for Discord Lab.
- [x] **Consolidate Processes**: Merged Telegram Bot into FastAPI (Webhooks) for HF stability.
- [x] **Code Cleanup & Refactoring**: Removed 50+ dead files and scripts, implemented service-layer deletion, and synchronized icon logic.

## 🛡️ Reliability & Maintenance (Based on RISKS.md)
- [ ] **Load Testing**: Execute k6/locust suite for 200+ concurrent users.
- [ ] **Redis Migration**: Move from local/internal Redis to Upstash for persistence.
- [ ] **Backup Automation**: Configure scheduled Neon.tech logical backups.
- [ ] **Media Offloading**: Research Cloudflare R2 / Backblaze B2 as a backup for HF Datasets if latency increases.
- [ ] **Logging Audit**: Review structured logs for `X-Forwarded-For` parsing accuracy after 1 week of production.
- [x] Implement **Home Dashboard** (Hero section, Horizontal scrolls, Activity feed).
- [x] Add **Subscription UI** (Notifications toggle on category cards).
- [x] Implement **Reading Progress** & **Table of Contents** for guides.
- [x] Add **Visual Analytics** charts in Admin Panel.
- [x] Organize **Media Library** tab in Admin Panel.
- [x] Fix Guide Editor crash on `text/content` field mismatch.
- [x] Add `try-catch` to `apiFetch` in `GuidesTab`.
- [x] Configure explicit CORS headers in `main.py`.
- [x] Fix critical syntax error in `textarea.tsx` (missing curly braces for spread props).
- [x] Update GitHub Actions workflow to use Node.js 22 (fixes `EBADENGINE` warnings).
- [x] Set up Session Handoff system (CLAUDE.md + Snapshots).
- [x] Implement "Media Proxy" to re-host ephemeral Discord CDN links and inline media tags.
- [x] Automate ffmpeg video compression for uploads > 48MB.
- [x] Connect Gemini AI for automated translation of synthesized guides.
- [x] Implement Multi-Provider Translation (Qwen 2.5 + Gemini + Google fallback).
- [x] Optimize backend memory for media imports (streaming + GC).
- [x] Stabilize Discord Lab: Fully async proxy with metadata support (Content-Length).
- [x] Selective proxying (speed up emojis/icons) and raw URL parsing in frontend.
- [x] Fixed ReferenceError and 404 absolute URL issues on GitHub Pages.
- [x] **Migrated Backend to Hugging Face Spaces (Docker).**
- [x] **Migrated Media & Icons to Hugging Face Datasets.**
- [x] **Performed deep repository cleanup (removed 5GB of legacy history/assets).**
- [x] **Established separate deployment pipelines (PowerShell scripts).**
- [x] **Implemented Hybrid Core Architecture (Environment separation).**

### 💎 Final Backend Stabilization (Production Hardening)
- [x] **Zero-Lint State**: Resolved 70+ Ruff violations (E402, E701, F841).
- [x] **Logic Restoration**: Recovered full icon normalization and formatting logic in `utils.py`.
- [x] **Test Overhaul**: Rewrote `test_api_endpoints.py` and `test_formatting.py` for modern service layers.
- [x] **Performance**: Fixed N+1 query issue in `GuideService.get_all` via `selectinload`.
- [x] **Architecture**: Unified icon mapping across `utils.py` and `lab_synthesizer.py`.

### 🧪 Experiments & Integration
- [ ] Test Discord Lab with raw JSON from Slayerpedia forum threads.
- [ ] Refine the mapping between Discord channel IDs and Website categories.
