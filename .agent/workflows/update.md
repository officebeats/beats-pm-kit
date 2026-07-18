---
title: Safe Kit Update
description: Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes.
---

// turbo-all

This workflow updates the kit software and structure. It is not the communication context refresh path.

If the user asks to update or refresh working context from Slack, Teams, Outlook, or Calendar, route to `/beats-comms` with explicit named read-only source windows instead of running this workflow. Communication context refresh must remain read-only, preserve unread state, save transcripts through `chat-transcript-archive`, and write durable outputs under `3. Meetings/chat-transcripts/` and `3. Meetings/reports/`.

1. Run the read-only compatibility and error check. Stop on blockers or required title migrations:

```bash
python system/scripts/upgrade_compat.py --json
```

2. If the report contains only safe title updates, create the backup and apply them before the update:

```bash
python system/scripts/upgrade_compat.py --apply
```

This preserves filenames and links, writes atomically, and records rollback data under `.beats/backups/`. Never rename a legacy task or workstream file as part of this automatic migration.

3. Run the update script:

```bash
python system/scripts/update.py
```

4. Verify the update was successful by checking the version:

```bash
python system/scripts/context_health.py
```
