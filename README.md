# BlackRose

[![Backend](https://img.shields.io/badge/Backend-Hugging_Face-orange?style=for-the-badge&logo=fastapi)](https://huggingface.co/spaces/Nihronick/blackrose-backend)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

BlackRose is a knowledge platform for Slayer Legend guides with a React frontend, FastAPI backend, Telegram integration, and AI-assisted guide import pipeline.

## Architecture at a glance

- **Frontend:** React + Vite + TypeScript (GitHub Pages)
- **Backend:** FastAPI (Hugging Face Spaces, Docker)
- **Database:** Neon PostgreSQL
- **Media:** Hugging Face Datasets + imgproxy
- **Jobs:** Inngest-driven async import flow

Detailed architecture: `docs/ARCHITECTURE.md`  
Engineering rules and handoff protocol: `docs/CLAUDE.md`  
Current backlog: `docs/todo.md`

## Local development

### Prerequisites

- Docker and Docker Compose
- Node.js 18+

### 1. Configure environment

```bash
cp .env.example .env
```

Fill required values in `.env` (at least DB, bot, and auth settings).

### 2. Start backend stack

```bash
docker-compose up --build
```

Backend API will be available at `http://localhost:8000`.

### 3. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`.

## Deployment

Deployment scripts are centralized in `tools/`:

- `powershell -File tools\deploy-backend.ps1` - deploy backend to HF Spaces
- `powershell -File tools\deploy-frontend.ps1` - build and deploy frontend to GitHub Pages

## Core stack

- **Backend:** FastAPI, SQLAlchemy 2.0 async, Pydantic v2, aiogram, Inngest
- **Frontend:** React 18, Vite, TanStack Query, Zustand
- **Infra:** Neon PostgreSQL, Hugging Face Spaces/Datasets, Docker

## Author

**Maksim Morozov (Nihronick)**  
GitHub: [@Nihronick](https://github.com/Nihronick)
