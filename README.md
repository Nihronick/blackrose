# 🌹 BlackRose: The Ultimate Slayer Legend Guide Platform

![BlackRose Banner](https://huggingface.co/datasets/Nihronick/blackrose-media/resolve/main/icons/promotion/Ether.png)

BlackRose is a high-performance, AI-powered knowledge base for **Slayer Legend** players. It features automated guide synthesis from Discord, multi-language support, and a sleek, mobile-first design.

---

## 🏗️ Hybrid Architecture

This project is distributed across multiple cloud services to ensure zero-cost hosting and high reliability:

- **Frontend:** [React 18 + Tailwind 4] Hosted on **GitHub Pages**.
- **Backend:** [FastAPI + Docker] Hosted on **Hugging Face Spaces**.
- **Database:** [PostgreSQL] Serverless on **Neon**.
- **Media Storage:** [HF Datasets] Persistent storage for icons, images, and videos.
- **AI Engine:** [Google Gemini] Automates guide translation and synthesis.

---

## 📂 Repository Structure

- `/frontend` - React source code and web assets.
- `/backend` - FastAPI server, Telegram bot, and database models.
- `/scripts` - Automation tools for maintenance and migration.
- `/docs` - Project documentation, specifications, and architecture plans.

---

## 🚀 Development & Deployment

### Local Setup

1. **Frontend:** `cd frontend && npm install && npm run dev`
2. **Backend:** `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`

### Deployment

We use a separate deployment pipeline for each component:
- **Backend:** Use `.\deploy-backend.ps1` to push to Hugging Face Spaces.
- **Frontend:** Use `.\deploy-frontend.ps1` to update GitHub Pages.

---

## 🛡️ Security

All sensitive data (tokens, DB strings) is managed via **Environment Secrets** on Hugging Face. Local `.env` files are ignored by Git to prevent leaks.

## 🤝 Community & Support

Developed for the Slayer Legend community. For updates and support, follow our Telegram Bot integration.

---

*Created by [Nihronick](https://github.com/Nihronick)*
