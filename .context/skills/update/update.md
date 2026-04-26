---
description: Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes.
source_tool: antigravity
source_path: .agents\workflows\update.md
imported_at: 2026-04-25T21:29:42.825Z
ai_context_version: 0.9.2
---

// turbo-all

1. Run the update script:

```bash
python system/scripts/update.py
```

2. Verify the update was successful by checking the version:

```bash
python system/scripts/context_health.py
```
