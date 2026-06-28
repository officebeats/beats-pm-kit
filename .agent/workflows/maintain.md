---
description: Refresh local indexes, validate adapters, run local task triage, and report kit health without mutating source systems.
---

> **Compatibility Directive**: Antigravity is canonical. Codex and other CLIs should run the same local maintenance checks and keep generated outputs local-only.

# /maintain - Local Kit Maintenance

Use this workflow when the user asks to refresh, validate, optimize, or maintain the local Beats PM kit.

## Contract

- Local-only by default.
- Do not read or mutate Slack, Teams, Outlook, Calendar, Jira, Confluence, Trello, or email unless the user provides a named read-only source window and explicitly asks for that source.
- Generated cache/wiki outputs stay under ignored local paths.
- Report what changed, what stayed local, and which follow-up commands are useful.

## Steps

1. Refresh the deterministic context index and optional Markdown wiki:

```bash
python3 system/scripts/context_router.py build --write-wiki --json
```

2. Regenerate derived runtime adapters, then validate command and adapter integrity:

```bash
python3 system/scripts/sync_cli_adapters.py
```

```bash
python3 system/scripts/command_integrity.py --require-generated
```

3. Run local task triage:

```bash
python3 system/scripts/task_master_triage.py --apply
```

4. Run context health:

```bash
python3 system/scripts/context_health.py
```

5. Summarize:
   - context index status and file count
   - command integrity status
   - task triage report path and top questions
   - health warnings
   - any skipped live-source reads
