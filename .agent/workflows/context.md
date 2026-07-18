---
description: Query local Beats PM files and return the smallest useful context packet for a topic.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.

# /context - Local Context Packet

Use this workflow when the user asks where context lives, asks for a local source packet, or needs task/product/meeting context before doing PM work.

## Contract

- Read local kit files only.
- Do not read Slack, Teams, Outlook, Calendar, Jira, or Confluence unless the user provides an explicit named read-only source window and invokes the relevant communication workflow.
- Treat `TASK_MASTER.md`, task detail files, transcripts, reports, and local docs as source of truth. Context indexes are acceleration layers only.
- Return source paths, confidence, missing scopes, and suggested next commands.

## Steps

1. Query the local context router:

```bash
python3 system/scripts/context_router.py query "<topic>" --json
```

2. Read only the top relevant source files needed to answer the user's question.
3. If the packet reports missing source windows, ask for the named read-only source window or continue from local files only.
4. Keep the response compact and cite local paths.

## Maintenance

Refresh the index when it is stale:

```bash
python3 system/scripts/context_router.py build --json
```
