---
description: Upgrade the Beats PM kit to the latest release from GitHub.
---

# /update — System Sync and Updates

// turbo-all

1. Check current local version:
```bash
cat VERSION
```

2. Check for updates:
```bash
python system/scripts/update_checker.py
```

3. If an update is available, pull latest:
```bash
git stash
git pull origin main
git stash pop
```

4. Install any new dependencies:
```bash
pip install -r system/requirements.txt 2>/dev/null || true
```

5. Verify the update:
```bash
python -m pytest system/tests/test_release_readiness.py -v --tb=short
```

6. Show the new version:
```bash
cat VERSION
```
