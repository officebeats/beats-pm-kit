---
name: slack-task-intake
description: Extract local Beats PM tasks from scoped Slack messages using read-only Slack access. Use with /beats-slack when Slack is connected and the user wants Slack-only task compilation.
priority: P0
maxTokens: 3000
triggers:
  - "/beats-slack"
version: 1.1.0
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized for read-only Slack MCP/connectors in Antigravity, Codex, Claude Code, and compatible runtimes. It must degrade safely when Slack search or unread metadata is unavailable.

# Slack Task Intake Skill

> **Role**: Convert scoped Slack context into local Beats PM tasks without sending messages or mutating Slack state.

## 1. Native Interface

- **Inputs**: `/beats-slack` with a channel, DM, thread, search query, time window, or configured Slack intake scope.
- **Allowed Slack tools**: Read-only Slack MCP/connector channel search, channel history read, thread read, user lookup, canvas read, and read-only message search when available.
- **Local files**: `SETTINGS.md`, `1. Company/ways-of-working.md`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/tasks/`, `3. Meetings/chat-transcripts/slack/`, optional `4. People/`, and optional `2. Products/partners/`.

---

## 2. Hard Safety Boundary

Slack is intake-only.

- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, upload, create canvases/files, or otherwise mutate Slack content or workspace state.
- Preserve unread state. Do not use tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Do not use Slack UI/browser navigation for unread review. Use read-only MCP/connector reads only.
- If a Slack tool implies state mutation or unread cursor movement, stop and ask the user for a safer scope or exported text.
- Do not quote full Slack conversations into local files. Store short evidence snippets and source references only.

---

## 3. Scope Protocol

1. **Explicit scope provided**: Process only the named channel, DM, thread, query, canvas, and/or time window.
2. **No explicit scope, configured Slack intake exists**: Use only manifest/configured Slack scopes surfaced by `python3 system/scripts/critical_commitment_refresh.py plan --mode day --json` or `3. Meetings/chat-transcripts/_manifest.json`. Do not invent workspace-wide coverage.
3. **No configured scope available**: Stop and ask the user for a channel, DM, thread, query, or time window, or ask whether to paste/export Slack text.
4. **No time window provided**: Use `system/scripts/chat_intake_state.py window --platform slack --scope "<SCOPE>"` and apply the returned `effective_start_at`.
5. **Potentially high-volume scope**: Before reading Slack, use `system/scripts/chat_intake_state.py chunks --platform slack --scope "<SCOPE>" --start "<EFFECTIVE_START_AT>" --end "<EFFECTIVE_END_AT>"` for `to:me`, mention/DM intake, multi-day channel history, or any window longer than 5 calendar days. Execute the returned chunks oldest-to-newest instead of attempting one full-window query first.

Do not broad-scan Slack workspaces, all channels, all DMs, or unknown unread surfaces.

Chunking rules:
- Default chunk size is 24 hours.
- Prefer exact `start_epoch` and `end_epoch` filters when the Slack runtime exposes them.
- If only Slack search syntax is available, add each chunk's `slack_query_date_hint` to the scoped query.
- Chunks marked `requires_exact_time_filter` require timestamp-capable tooling. If the runtime only supports date-granular search for that subrange, stop and ask the user for a tighter channel/thread/person scope.
- If a chunk hits `page_limit_exceeded` or an equivalent connector cap, split only that chunk with `--chunk-hours 12`, then retry. Continue narrowing the capped subrange down to 6 hours before asking the user for a tighter scope.
- Merge and deduplicate chunk results before extracting tasks.

---

## 4. Extraction Protocol

For every scoped Slack source:

1. Record source metadata: channel/DM/thread/canvas name, timestamp or link when available, and read-only operation used.
2. Record the effective read window, whether it came from an explicit user window, the 5-business-day default, or manifest state, and the chunk plan used for high-volume scopes.
3. Extract candidate action items, decisions, blockers, owner mentions, due dates, and follow-up requests.
4. Convert every candidate into a **workstream finding** before writing tasks:
   - Workstream title or best match, 9 words or fewer.
   - Display title, started date/source, latest progress source, and internal agent refs.
   - Latest outcome or status signal.
   - Explicit completed outcome/checklist signal, if any.
   - Open item with owner, action, due gate, and Slack source.
   - Recommended next action.
   - Authority tier: direct manager, skip-level, executive, authorized leader, standard.
   - Commitment type: leadership, external customer, partner, end-user deadline, internal deadline, internal.
   - Evidence strength and source reference.
   - Completion state: open, explicit complete, implied complete.
5. Deduplicate against `5. Trackers/WORKSTREAMS.md`, `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, existing task detail files, and previously processed chat transcript source references when available.
6. Apply the `task-manager` Priority Gate using `1. Company/ways-of-working.md`.
7. Rank direct-manager, skip-level, executive, external customer/partner, and dated end-user commitments above ordinary stale work.
8. Classify each item as:
   - **Accepted task**: in scope and ready to route locally.
   - **Existing task update**: belongs in an existing task progress log or stakeholder quote.
   - **Workstream update**: latest outcome, open item, recommended next action, or completed outcome for an existing workstream.
   - **Needs confirmation**: unclear owner, scope, priority, source authority, or due date.
   - **Rejected/out of scope**: fails the Priority Gate.
9. Treat explicit Slack completion evidence as eligible to check off local checklist items with completion date/source. Treat implied completion language such as "ready for review" or "should be done" as a confirmation question, not as a checked item.
10. User-facing labels, evidence prose, and owner questions must use readable task/workstream titles and source provenance. Keep Task Master IDs, Jira IDs, Trello IDs, and source IDs only in local links, metadata, or an `Agent refs` line.

---

## 5. Durable Output

Allowed writes are local repo files only:

- Accepted tasks -> `5. Trackers/TASK_MASTER.md` and `5. Trackers/tasks/{ID}.md` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Workstream updates -> `5. Trackers/WORKSTREAMS.md` and `5. Trackers/workstreams/{slug}.md` when present.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when materially useful.
- Slack chat transcript -> `3. Meetings/chat-transcripts/slack/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`.
- Run report -> `3. Meetings/reports/slack-runs/{RUN_ID}.md`.

The run report must include:

- Slack scope processed.
- Effective read window and chunk plan used, including capped chunk retries or subranges needing user narrowing.
- Read-only operations used.
- Chat transcript files written.
- Candidate tasks and gate outcomes.
- Workstream matches, latest outcomes, completed outcomes, open items, recommended next 3, authority tier, commitment type, and completion state.
- Issues encountered and recommended follow-up.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Slack response by the user.
- Safety note confirming no Slack messages were sent and unread state was not intentionally changed.

---

## 6. Final Output

Return the workstream snapshot first using the `task-manager` title, bullet, and sub-bullet format, then a compact task-focused summary:

- Workstream updates and priority order.
- Files updated.
- Chat transcript files saved.
- Accepted tasks and IDs.
- Existing task updates.
- Issues and recommendations.
- Items needing confirmation or manual Slack response.
- Safety confirmation: no Slack send/mutation actions were performed.
