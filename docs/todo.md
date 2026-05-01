# 📋 Project TODO

## 🚀 Priority: High
- [x] Verify Admin Panel stability (fixed stats/analytics and missing view_logs table).
- [x] Implement Backend Proxy for Discord Media (bypass CORS policy).
- [x] Implement/Fix Guide deletion logic.

## 🛠️ Features & Improvements
- [x] Clean up redundant Graphify files (Verified removed).

## ✅ Completed
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

### 🧪 Experiments & Integration
- [ ] Test Discord Lab with raw JSON from Slayerpedia forum threads.
- [ ] Refine the mapping between Discord channel IDs and Website categories.
