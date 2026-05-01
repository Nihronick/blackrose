# BlackRose Risk Register & Mitigation Strategy 🛡️

This document outlines potential technical risks and operational "underwater rocks" for the BlackRose platform, along with mitigation strategies.

## 🔴 High Risk

### 1. Hugging Face Spaces Resource Limits
- **Risk:** Ephemeral storage (50GB), CPU/RAM throttling, and frequent restarts on the free tier.
- **Impact:** System downtime, lost in-memory cache, or slow response times under load.
- **Mitigation:**
    - Persistent database is on Neon.tech (external).
    - Redis (Upstash or external) should be used instead of in-memory if restarts become an issue.
    - Keep the Docker image lightweight (already optimized).
    - **Plan B:** Prepare migration manifests for Railway or Fly.io.

### 2. Media Scalability (HF Datasets)
- **Risk:** High latency and bandwidth quotas when serving large volumes of videos/images.
- **Impact:** Slow guide loading, broken media links.
- **Mitigation:**
    - Implement aggressive frontend caching (Service Worker).
    - Use CDN (Cloudflare) in front of HF Dataset raw links if possible.
    - **Plan B:** Migrate media to Cloudflare R2 or Backblaze B2.

## 🟡 Medium Risk

### 3. Rate Limiting Bypass
- **Risk:** Incorrect parsing of `X-Forwarded-For` due to changes in HF infrastructure.
- **Impact:** Ineffective throttling, vulnerability to brute-force/DDoS.
- **Mitigation:**
    - Monitor `X-Forwarded-For` structure in logs.
    - Implement a "Trust Proxy" list if needed.
    - Use Fail2Ban logic or external WAF (Cloudflare).

### 4. Telegram WebApp API Volatility
- **Risk:** Breaking changes in Telegram Bot API or `initData` structure.
- **Impact:** Broken authentication flow for TMA users.
- **Mitigation:**
    - Follow official Telegram Bot News.
    - Maintain a rigorous `verify_telegram_init_data` suite.
    - Use a versioned approach for the auth flow.

### 5. PWA & TMA Lifecycle Conflicts
- **Risk:** Cache collisions or Service Worker issues when switching between Browser and TMA.
- **Impact:** Inconsistent UI state or stale data.
- **Mitigation:**
    - Use clear environment separation in `useAppEnv`.
    - Implement a "Clear Cache" button in Admin/Settings.
    - Ensure unique cache keys for different environments.

## 🟢 Low Risk

### 6. Database Backups
- **Risk:** Data loss during Neon serverless maintenance.
- **Mitigation:**
    - Verify Neon's automated backup frequency.
    - **Task:** Create a script for weekly manual SQL dumps to a secure location.

### 7. Scalability at 1k+ Users
- **Risk:** Performance degradation under simultaneous load.
- **Mitigation:**
    - **Task:** Perform load testing using `k6` or `locust`.
    - Optimize SQL queries (already implemented Full-Text Search).

---
*Last Updated: 2026-05-01 | Status: Monitored*
