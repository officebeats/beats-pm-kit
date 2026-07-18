---
title: Find Past Product Evidence
description: Search past meetings, transcripts, chats, decisions, tasks, and product documents by full text.
---

# Find Past Product Evidence

Use `/find <query>` whenever the user asks what was previously discussed, decided, promised, blocked, or completed.

## Steps

1. Run `python3 system/scripts/context_router.py find "<query>" --json`.
2. Present the smallest useful evidence packet: readable title, date/type, excerpt, exact file and line, and confidence.
3. Read only the top source files needed to answer the question.
4. Show conflicting decisions or status claims together unless one explicitly supersedes another.
5. When creating or updating product work, attach the selected evidence paths to the resulting task, decision, plan, or brief.

The local SQLite FTS5 index is disposable acceleration. Markdown remains canonical, and the router falls back to bounded metadata/file search when the index is unavailable.
