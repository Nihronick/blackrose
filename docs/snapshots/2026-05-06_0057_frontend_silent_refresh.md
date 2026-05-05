# Session Snapshot — Frontend Silent Refresh

## Main Changes
- Implemented silent refresh for web auth in `frontend/src/lib/api.ts`:
  - On `401`, client calls `/api/auth/refresh` with stored `refresh_token`.
  - On success, stores new access token and retries original request once.
  - On refresh failure, clears local auth state.
- Extended auth storage in `frontend/src/lib/auth.ts`:
  - Added `REFRESH_TOKEN_KEY` and helpers:
    - `getStoredRefreshToken()`
    - `setStoredAccessToken()`
  - Updated `setStoredToken()` to optionally persist `refreshToken`.
  - `clearStoredToken()` now removes access token, refresh token, and user payload.
- Updated bootstrap flow in `frontend/src/hooks/useAppInitialization.ts`:
  - Accepts optional `refresh_token` from TMA login response and stores it.

## Verification
- `npm run build` in `frontend/` passed successfully.
- IDE lints for changed frontend files returned no errors.

## Technical Debt / Next Steps
- Add unit tests for:
  - successful refresh + request replay;
  - refresh failure + forced logout state cleanup.
- Consider deduplicating parallel refresh requests with a shared in-flight promise to avoid multiple refresh calls during burst 401 responses.
