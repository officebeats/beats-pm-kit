---
title: Workspace Cleanup
description: Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task cleanup, hierarchical integrity auditing, or explicitly triggers /vacuum or /cleanup.
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

4. Refresh the local knowledge manifest and verify every compiler-owned page against its raw source hash:

```bash
python3 system/scripts/knowledge_compiler.py manifest
python3 system/scripts/knowledge_compiler.py verify
```

This is the authorized maintenance path for compiled knowledge. Keep raw captures immutable, treat compiled and digest pages as navigation aids, and never add a cloud scheduler. Run compilation only during `/vacuum`, explicit maintenance, or after detected source changes.
