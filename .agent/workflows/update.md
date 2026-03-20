---
description: Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes.
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
