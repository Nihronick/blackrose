# Changelog

## [3.3.0] - 2026-05-01
### "Ultimate Hybrid Core Hardening"

This release transforms BlackRose from a stable MVP into a production-hardened hybrid platform, focusing on security, performance, and cross-platform reliability.

### 🛡️ Security
- **Cryptographic Validation**: Implemented strict HMAC-SHA256 verification for Telegram `initData`.
- **Hybrid Auth Flow**: Integrated Refresh Token support and environment-aware JWT logic.
- **Rate Limiting**: Added proxy-aware (Hugging Face/Cloudflare) rate limiting via `X-Forwarded-For`.
- **Global Exception Handling**: Integrated Telegram alerts for critical backend failures.
- **CORS Hardening**: Enforced strict origin policies for web and production environments.

### 🚀 Performance & UX
- **Skeleton Screens**: Added global shimmering skeletons for initial loading states and rendered images.
- **Structured Logging**: Migrated to JSON-based logging with Request-ID and User-ID traceability.
- **Haptic Enhancements**: Refined Taptic Engine feedback for a more native TMA feel.
- **SEO & Metadata**: Injected comprehensive Open Graph and Twitter tags for rich link previews.

### ⚙️ Reliability
- **Deep Health Monitoring**: Upgraded `/health` to check real-time connectivity for PostgreSQL and Redis.
- **Graceful Logout**: Environment-aware logout logic that correctly closes the Telegram Mini App session.
- **A11y Refinement**: Improved accessibility labels for navigation and header components.

### 🛠️ Developer Experience
- **Architecture Documentation**: Rewrote README with Mermaid diagrams and technical specs.
- **CI/CD Foundation**: Added core API tests and standardized `.env.example`.
- **CLAUDE.md**: Restored and updated the source-of-truth project manual.

---
*Developed with 🌹 by Nihronick & Antigravity AI*
