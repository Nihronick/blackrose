# Changelog

## [4.1.0] - 2026-05-10
### 🚀 Gaming Glossary & AI Quality
- **Centralized Glossary**: Created `backend/core/glossary.json` with Slayer Legend terminology.
- **Term-Aware Translation**: Integrated glossary into Gemini/HF prompts to ensure professional RU gaming terms.
- **No-Translate Rules**: Added protection for skill/spirit names to prevent literal translations.
- **Enhanced Synthesis**: Discord Lab now uses abbreviations map for better guide structure.

## [4.0.0] - 2026-05-03
### "Modernization & Automation"

This major update introduces professional background job orchestration and advanced AI-driven content synthesis, paving the way for fully automated content ingestion.

### 🤖 Automation & AI
- **Background Processing**: `Inngest` for durable tasks (Discord import, media sync).
- **AI Synthesis**: `Gemini 1.5 Flash` for content generation and professional translation.
- **Glossary System**: Centralized `backend/core/glossary.json` for gaming terminology consistency.
- **Icon Syntax**: Standardized `{{icon_name}}` or `{{icon_id}}` mapping.
- **Discord Lab Evolution**: Exposed AI-powered synthesis endpoints for automated content generation from raw logs.

### 🏗️ Infrastructure & Security
- **JWT Standardization**: Replaced custom HMAC logic with standard `PyJWT` for industry-standard session management.
- **Full-Text Search (FTS)**: Implemented high-performance search using PostgreSQL `TSVECTOR` and `GIN` indexes with relevance ranking.
- **Connection Pooling**: Global `aiohttp` session management for optimized external API calls and resource efficiency.
- **Event Loop Optimization**: Integrated `uvloop` for enhanced asynchronous performance on Linux environments.

### 📊 Monitoring & DX
- **Advanced Diagnostics**: Enhanced health check system with network latency measurements and granular service-level status.
- **Architecture Documentation (v2.0)**: Consolidated and synchronized all engineering documentation into the `docs/` folder.
- **CI/CD Automation**: Added GitHub Actions for automated linting (Ruff/Biome) and testing (Pytest/Vitest).


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
