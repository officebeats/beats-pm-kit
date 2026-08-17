---
title: Workspace Cleanup
description: Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task cleanup, hierarchical integrity auditing, or explicitly triggers /vacuum or /cleanup.
---

// turbo-all

1. Run the vacuum script. It refreshes the supported context and task indexes,
   keeps unfamiliar root work in place, humanizes legacy task headings and
   ID-only links, and rebuilds `5. Trackers/MARKDOWN_LABELS.md`:

```bash
python system/scripts/vacuum.py
```

Raw evidence, transcripts, chat archives, historical backups, integration IDs,
and filenames remain unchanged. Dependency/build trees are excluded.

2. Confirm the Markdown pass is idempotent:

```bash
python system/scripts/markdown_humanizer.py --json
```

3. Run structure enforcement:

```bash
python system/scripts/enforce_structure.py
```

3b. Prune oversized evidence sections (archives, never deletes). Entries beyond the newest 10 move verbatim to `5. Trackers/archive/evidence/`:

```bash
python3 system/scripts/evidence_prune.py --apply --json
```

4. Run a final health check:

```bash
python system/scripts/context_health.py
```

5. Refresh the local knowledge manifest and verify every compiler-owned page against its raw source hash:

```bash
python3 system/scripts/knowledge_compiler.py manifest
python3 system/scripts/knowledge_compiler.py verify
```

This is the authorized maintenance path for compiled knowledge. Keep raw captures immutable, treat compiled and digest pages as navigation aids, and never add a cloud scheduler. Run compilation only during `/vacuum`, explicit maintenance, or after detected source changes.
