---
description: "Continue the BlackRose repo cleanup: remove remaining noise, validate guide links/media, and re-run secret checks"
---

You are the follow-up agent for the BlackRose Guides repository.

Goal:
- Finish the public-facing cleanup without disturbing useful workflow files.
- Remove only clearly obsolete or noisy content.
- Keep deployment-safe media paths and internal link structure intact.

Work in this order:
1. Review the current unstaged changes and identify any remaining noisy guide files, duplicate notes, or obsolete handoff text.
2. Keep the maintenance playbook concise, but do not delete workflow details that are still needed for imports, media handling, or secret checks.
3. Validate guide links, meta-links, and public media paths in the Russian guides.
4. Avoid editing unrelated user changes or touching the app code unless the cleanup requires it.
5. Run `python scripts/check_secrets.py` before finishing.
6. Report any remaining broken links, noisy files, or follow-up items that still need manual review.

Output:
- concise summary of what you changed
- any blockers or residual risks
- whether the secret scan found anything