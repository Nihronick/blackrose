---
description: Trigger AI Code Review on modified and unstaged files.
---

Review all recent modifications in BlackRose:

1. Run `git diff HEAD` (or against main) to view current changes.
2. Verify:
   - No `any` or `@ts-nocheck` in TypeScript.
   - All imports at the top in Python.
   - Pydantic models in `models/schemas.py`.
   - Error and Empty state handling present for all new UI components.
   - No hardcoded secrets or raw SQL injections.
3. Group findings by Critical, Warning, and Suggestion.
