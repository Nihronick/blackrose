# Project Instructions

- Use the maintenance playbook in [ops/guide-maintenance/README.md](../ops/guide-maintenance/README.md) as the source of truth for guide translation, import, media handling, and cleanup.
- Keep guide media deployment-safe: prefer `frontend/public/assets/...` or a public CDN path for anything referenced from published guides.
- Before suggesting or committing changes, run the secret check script in [scripts/check_secrets.py](../scripts/check_secrets.py).
- Do not introduce temporary export artifacts, cache files, or generated media into commits unless the task explicitly requires it.
- When editing guides, preserve the existing structure, update meta-links, and avoid touching unrelated files.