# 🌹 BlackRose: The Ultimate Slayer Legend Guide Platform

[![Website](https://img.shields.io/badge/Website-blackrosesl.me-blueviolet?style=for-the-badge&logo=react)](https://blackrosesl.me)
[![Backend](https://img.shields.io/badge/Backend-Hugging_Face-orange?style=for-the-badge&logo=fastapi)](https://huggingface.co/spaces/Nihronick/blackrose-backend)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **BlackRose** is a high-performance, community-driven knowledge base for the **Slayer Legend** ecosystem. It bridges the gap between fragmented Discord guides and players by providing a centralized, AI-powered, and mobile-first experience.

---

## 🌟 The Vision

In modern gaming communities, the best guides are often buried in Discord channels, difficult to search, and inaccessible to non-English speakers. **BlackRose** solves this by:
- **Automated Synthesis:** Extracting and structuring raw guide data from Discord "Lab" channels.
- **AI-Powered Localization:** Using LLMs (Gemini/HF) to translate complex game mechanics while preserving context.
- **Extreme Portability:** Designed as a Telegram Mini App for instant access during gameplay.

---

## 🏗️ Technical Architecture

This project demonstrates a **Cloud-Native Hybrid Architecture** designed for high scalability with zero operational costs.

### 🌐 Frontend (The Web Interface)
- **Tech Stack:** React 18, TypeScript, Tailwind CSS 4, Zustand.
- **Optimization:** Vite-powered static build with code-splitting for fast initial loads.
- **Hosting:** Deployed on **GitHub Pages** with a custom domain and automated SSL.

### ⚙️ Backend (The Engine)
- **Tech Stack:** FastAPI (Python 3.11+), SQLAlchemy 2.0 (Async), Pydantic v2.
- **Deployment:** Containerized via **Docker**, hosted on **Hugging Face Spaces**.
- **Security:** JWT-based authentication, hardened CORS policies, and secure Telegram InitData verification.

### 🗄️ Infrastructure & Storage
- **Database:** Serverless PostgreSQL on **Neon.tech**.
- **Media Storage:** Leverages **Hugging Face Datasets** as a cloud-native file system, avoiding costly S3 alternatives while maintaining high-speed delivery.
- **Media Processing:** On-the-fly video compression using **FFmpeg** (asynchronous subprocesses) to ensure mobile compatibility.

---

## 📂 Project Structure

```text
├── frontend/               # React Application (Client-side)
│   ├── src/features/       # Domain-driven feature modules (Admin, Guides, Search)
│   ├── src/components/     # Reusable UI primitives
│   └── public/             # Static assets & CNAME
├── backend/                # FastAPI Application (Server-side)
│   ├── bot/                # Telegram Bot handlers & middleware
│   ├── routers/            # API endpoints (Admin, Public, Auth)
│   ├── services/           # Business logic (Notification, Translation)
│   └── storage.py          # Cloud-native HF Dataset integration
├── scripts/                # Deployment and maintenance automation
└── docs/                   # ADRs, Schema diagrams, and Technical Specs
```

---

## 🚀 Key Technical Features

1. **Intelligent Caching:** Multi-layer cache invalidation strategy for guide content.
2. **Dynamic Media Management:** Automated upload/delete lifecycle synced between the database and HF Datasets.
3. **Glossary-Aware Translation:** A custom translation pipeline that respects game-specific terminology.
4. **Mobile-First UX:** Tailored specifically for the Telegram Mini App environment with native-feeling interactions.

---

## 🛠️ Development & Deployment

The project is designed with a **"GitOps-lite"** workflow:
- All changes are merged into `main`.
- **Backend Deploy:** `.\deploy-backend.ps1` automates Docker builds and pushes to HF.
- **Frontend Deploy:** `.\deploy-frontend.ps1` builds the production bundle and updates GH Pages.

---

## 👤 Author

**Maksim Morozov (Nihronick)**
- **GitHub:** [@Nihronick](https://github.com/Nihronick)
- **Project Goal:** To build the most robust community tool for Slayer Legend fans while mastering modern full-stack patterns.

---

*This project is a testament to building professional-grade software using modern tools and creative infrastructure choices.*
