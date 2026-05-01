# BlackRose Testing Protocol: Hybrid Core Validation

This document outlines the mandatory testing procedures to ensure the BlackRose application maintains its production-grade quality across all platforms (Telegram Mini App, Web, PWA).

---

## 1. Environment Detection & Adaptive UI

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 1.1 | Open in Telegram Mini App | `isTMA` flag in `useAppEnv` | `true`, Expand to full height, Haptic feedback active. |
| 1.2 | Open in Browser (Desktop/Mobile) | Layout responsiveness | Desktop: Fixed sidebar/Header; Mobile: Bottom Nav/FAB. |
| 1.3 | PWA Installation | Manifest & Service Worker | Install prompt shows on mobile browsers; Splash screen works. |
| 1.4 | Theme Switching | `Telegram.WebApp.themeParams` | UI shifts instantly between Light/Dark/Game modes. |

## 2. Authentication Flow (Critical)

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 2.1 | TMA Login | `initData` validation | Backend validates HMAC; Returns JWT with `source: tma`. |
| 2.2 | Web Login | Email/Password | Returns JWT with `source: web`. |
| 2.3 | TMA → Web Handoff | Token persistence | Clicking "Open in Browser" should keep user session via URL param/Storage. |
| 2.4 | Logout (TMA) | `WebApp.close()` | App closes in Telegram; Token is wiped from local storage. |
| 2.5 | Token Refresh | Refresh Token strategy | Seamless re-auth for long-running web sessions. |

## 3. Performance & Predictivity

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 3.1 | Rapid Hover/Scroll | Prefetch Debounce | Network tab: Only 1 request after 150ms hover; No spamming. |
| 3.2 | Navigation Transitions | `AnimatePresence` | Smooth 300ms transitions between Guide/Category views. |
| 3.3 | Back Navigation | Native vs Browser | TMA uses native Telegram Back button; Web uses browser history. |

## 4. Media & Content Delivery

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 4.1 | Guide Loading | Skeletons & Shimmer | Content areas show shimmer pulse until data arrives. |
| 4.2 | Video Playback | `VideoBlock` integration | Video starts with shimmer overlay; Custom controls match app style. |
| 4.3 | Image Optimization | Lazy Loading | Images outside viewport do not load until visible. |
| 4.4 | Scrollbars | Platform awareness | Hidden on Mobile (TMA); Slim/Custom on Desktop. |

## 5. Error Resilience

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 5.1 | Fake `initData` | 401 Unauthorized | Backend rejects; Frontend shows login error with retry. |
| 5.2 | Backend Down (5xx) | Telegram Alerting | Developer gets bot notification; User sees "Under Maintenance". |
| 5.3 | Rate Limiting | 429 Too Many Requests | User sees "Slow down" toast instead of a crash. |
| 5.4 | Offline Mode | PWA Offline state | App remains interactive with cached data (TanStack Query). |

## 6. Accessibility

| ID | Scenario | Checkpoint | Expected Result |
|:---|:---|:---|:---|
| 6.1 | Reduced Motion (System) | `prefers-reduced-motion` | High-CPU animations and mesh-bg disabled automatically. |
| 6.2 | Haptic Feedback | Interaction buzz | Vibration felt on primary actions (Settings, Subscriptions). |

---

## Final Release Checklist
- [ ] Verify `DATABASE_URL` is production-ready.
- [ ] Check `REDIS_URL` connection stability.
- [ ] Ensure `HONEYBADGER_API_KEY` or Sentry is active.
- [ ] Validate Telegram Bot Token permissions.
- [ ] Run `npm run build` and check bundle size (< 250kb Gzipped).
