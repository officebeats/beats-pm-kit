---
description: Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes.
---

// turbo-all

This workflow updates the kit software and structure. It is not the communication context refresh path.

If the user asks to update or refresh working context from Slack, Teams, Outlook, or Calendar, route to `/beats-comms` with explicit bounded scopes instead of running this workflow. Communication context refresh must remain read-only, preserve unread state, save transcripts through `chat-transcript-archive`, and write durable outputs under `3. Meetings/chat-transcripts/` and `3. Meetings/reports/`.

1. Run the update script:

```bash
python system/scripts/update.py
```

2. Verify the update was successful by checking the version:

```bash
python system/scripts/context_health.py
```
