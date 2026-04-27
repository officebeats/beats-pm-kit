---
name: slack-task-intake
description: Extract local Beats PM tasks from scoped Slack messages using read-only Slack access. Use with /beats-slack when Slack is connected and the user wants Slack-only task compilation.
priority: P0
maxTokens: 3000
triggers:
  - "/beats-slack"
version: 1.0.0
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized for read-only Slack connectors in Codex and Antigravity-compatible runtimes. It must degrade safely when Slack search or unread metadata is unavailable.

# Slack Task Intake Skill

> **Role**: Convert scoped Slack context into local Beats PM tasks without sending messages or mutating Slack state.

## 1. Native Interface

- **Inputs**: `/beats-slack` with a channel, DM, thread, search query, time window, or configured Slack intake scope.
- **Allowed Slack tools**: Read-only channel search, channel history read, thread read, user lookup, canvas read, and read-only message search when available.
- **Local files**: `SETTINGS.md`, `1. Company/ways-of-working.md`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/tasks/`, `3. Meetings/chat-transcripts/slack/`, optional `4. People/`, and optional `2. Products/partners/`.

---

## 2. Hard Safety Boundary

Slack is intake-only.

- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, upload, create canvases/files, or otherwise mutate Slack content or workspace state.
- Preserve unread state. Do not use tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Do not use Slack UI/browser navigation for unread review. Use read-only connector reads only.
- If a Slack tool implies state mutation or unread cursor movement, stop and ask the user for a safer scope or exported text.
- Do not quote full Slack conversations into local files. Store short evidence snippets and source references only.

---

## 3. Scope Protocol

1. **Explicit scope provided**: Process only the named channel, DM, thread, query, canvas, and/or time window.
2. **No scope available**: Ask the user for a channel, DM, thread, query, or time window before reading Slack.
3. **No time window provided**: Use `system/scripts/chat_intake_state.py window --platform slack --scope "<SCOPE>"` and apply the returned `effective_start_at`.

Do not broad-scan Slack workspaces, all channels, all DMs, or unknown unread surfaces.

---

## 4. Extraction Protocol

For every scoped Slack source:

1. Record source metadata: channel/DM/thread/canvas name, timestamp or link when available, and read-only operation used.
2. Record the effective read window and whether it came from an explicit user window, the 5-business-day default, or manifest state.
3. Extract candidate action items, decisions, blockers, owner mentions, due dates, and follow-up requests.
4. Deduplicate against `5. Trackers/TASK_MASTER.md`, existing task detail files, and previously processed chat transcript source references when available.
5. Apply the `task-manager` Priority Gate using `1. Company/ways-of-working.md`.
6. Classify each item as:
   - **Accepted task**: in scope and ready to route locally.
   - **Existing task update**: belongs in an existing task progress log or stakeholder quote.
   - **Needs confirmation**: unclear owner, scope, priority, source authority, or due date.
   - **Rejected/out of scope**: fails the Priority Gate.

---

## 5. Durable Output

Allowed writes are local repo files only:

- Accepted tasks -> `5. Trackers/TASK_MASTER.md` and `5. Trackers/tasks/{ID}.md` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when materially useful.
- Slack chat transcript -> `3. Meetings/chat-transcripts/slack/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`.
- Run report -> `3. Meetings/reports/slack-runs/{RUN_ID}.md`.

The run report must include:

- Slack scope processed.
- Read-only operations used.
- Chat transcript files written.
- Candidate tasks and gate outcomes.
- Issues encountered and recommended follow-up.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Slack response by the user.
- Safety note confirming no Slack messages were sent and unread state was not intentionally changed.

---

## 6. Final Output

Return a compact task-focused summary:

- Files updated.
- Chat transcript files saved.
- Accepted tasks and IDs.
- Existing task updates.
- Issues and recommendations.
- Items needing confirmation or manual Slack response.
- Safety confirmation: no Slack send/mutation actions were performed.
