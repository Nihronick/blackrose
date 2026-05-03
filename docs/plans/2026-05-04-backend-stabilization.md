# Backend Stabilization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Finalize the stabilization of the BlackRose backend on Hugging Face Spaces by ensuring Inngest integration is fully operational, workers are stable, and all architectural technical debt is documented.

**Architecture:** We use a flat backend structure with absolute imports. Background jobs are handled via Inngest (for immediate/triggered tasks) and ARQ (for periodic/worker-based tasks). Supervisord manages process lifecycles.

**Tech Stack:** FastAPI, Inngest Python SDK, SQLAlchemy (async), Supervisord, ARQ.

---

### Task 1: Verify Production Runtime
**Files:**
- Modify: `backend/main.py:1-100`
- Test: `backend/tests/test_health.py`

**Step 1: Create a simple health check test**
```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_api_health():
    async with httpx.AsyncClient(base_url="http://localhost:7860") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
```

**Step 2: Run test locally (if possible) or verify via logs**
Run: `pytest backend/tests/test_health.py`
Expected: PASS

**Step 3: Commit**
```bash
git add backend/tests/test_health.py
git commit -m "test: add basic health check verification"
```

### Task 2: Final Inngest Configuration Review
**Files:**
- Modify: `backend/core/inngest_client.py:1-20`
- Modify: `backend/main.py:70-80`

**Step 1: Ensure absolute imports for all Inngest functions**
In `main.py`, ensure we are importing `discord_import_guide` using absolute path if needed.
Currently: `from functions.discord_import import discord_import_guide` (This is absolute relative to /app).

**Step 2: Implement a test Inngest function to verify connectivity**
Create `backend/functions/test_job.py`:
```python
import inngest
from core.inngest_client import inngest_client

@inngest_client.create_function(
    fn_id="test_job",
    trigger=inngest.TriggerEvent(event="app/test.job"),
)
async def test_job(ctx: inngest.Context, step: inngest.Step):
    return {"message": "Success"}
```

**Step 3: Register test function in main.py**
```python
from functions.test_job import test_job
# ...
inngest.fast_api.serve(
    app,
    inngest_client,
    [discord_import_guide, test_job],
    serve_path="/api/inngest"
)
```

**Step 4: Commit**
```bash
git add backend/functions/test_job.py backend/main.py
git commit -m "feat: add test inngest job for verification"
```

### Task 3: Worker Lifecycle Hardening
**Files:**
- Modify: `backend/workers/gc_storage.py:1-200`
- Modify: `backend/supervisord.conf`

**Step 1: Add robust signal handling to workers**
Ensure `gc_storage.py` and `notify.py` handle SIGTERM gracefully.

**Step 2: Update Supervisord config for better restart policies**
In `supervisord.conf`:
```ini
[program:api]
autorestart=true
startretries=10

[program:worker]
autorestart=true
startretries=10
```

**Step 3: Commit**
```bash
git add backend/supervisord.conf backend/workers/gc_storage.py
git commit -m "ops: improve worker reliability and signal handling"
```
