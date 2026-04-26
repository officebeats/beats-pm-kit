---
description: Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task archiving, hierarchical integrity auditing, or explicitly triggers /vacuum, /archive, or /cleanup.
source_tool: antigravity
source_path: .agents\workflows\vacuum.md
imported_at: 2026-04-25T21:29:42.829Z
ai_context_version: 0.9.2
---

// turbo-all

1. Run the vacuum script:

```bash
python system/scripts/vacuum.py
```

2. Run structure enforcement:

```bash
python system/scripts/enforce_structure.py
```

3. Run a final health check:

```bash
python system/scripts/context_health.py
```
