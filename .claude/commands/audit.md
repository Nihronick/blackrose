---
description: Run full project audit across backend, frontend, pipeline, and type systems.
---

Execute comprehensive validation across all layers of the BlackRose codebase:

1. **Backend Tests**: Run `python -m pytest backend/tests/ -v --tb=short`
2. **Pipeline Tests**: Run `python -m pytest pipeline/tests/ -v`
3. **Frontend Lint**: Run `cd frontend && npm run lint`
4. **Frontend Tests**: Run `cd frontend && npm run test`
5. **Frontend Build**: Run `cd frontend && npm run build`
6. Summarize any failing checks, warnings, or performance bottlenecks discovered.
