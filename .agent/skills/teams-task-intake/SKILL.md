---
name: teams-task-intake
description: Extract local Beats PM tasks from scoped Microsoft Teams chats or channels using read-only Teams access. Use with /beats-teams when Teams is connected and the user wants Teams-only task/status compilation.
priority: P0
maxTokens: 3000
triggers:
  - "/beats-teams"
version: 1.1.0
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized for read-only MS365 MCP/connector Teams operations in Antigravity, Codex, Claude Code, and compatible runtimes. It must degrade safely to manual copy/export when connector reads are not surfaced.

# Teams Task Intake Skill

> **Role**: Convert scoped Teams context into local Beats PM tasks and status updates without sending messages or mutating Teams state.

## Quick Path

1. Confirm scope: explicit chat/channel/thread/query/person/window, a read-only unread chat list when the connector exposes one, or a configured manifest scope; if none, stop and ask — never broad-scan Teams.
2. If no time window, run `chat_intake_state.py window --platform teams --scope "<SCOPE>"`.
3. Read with read-only MS365 operations only; never send, post, react, or move read cursors; label channel reads as recent snapshots.
4. Convert every candidate into a workstream finding (title of 9 words or fewer, latest outcome, open item, authority tier, commitment type, completion state), dedupe against trackers, and apply the task-manager Priority Gate.
5. Write local outputs only: transcript to `3. Meetings/chat-transcripts/teams/`, tasks to `5. Trackers/`, run report to `3. Meetings/reports/teams-runs/{RUN_ID}.md`.
6. Return the workstream snapshot first, then the compact summary with the safety confirmation.

Go deeper into section 2 for the hard safety boundary and the `teams_bridge.py` fallback, section 4 for classification, and section 5 for the run-report contract.

## 1. Native Interface

- **Inputs**: `/beats-teams` with a chat, channel, team/channel pair, person, thread, search query, time window, or configured Teams intake scope.
- **Allowed Teams operations**: Read-only MS365 MCP/connector profile resolution, chat listing, unread chat listing, chat message reads, recent thread listing, team/channel resolution, channel message reads, and meeting transcript reads when available.
- **Local files**: `SETTINGS.md`, `1. Company/ways-of-working.md`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/tasks/`, optional `4. People/`, optional `2. Products/partners/`, and `3. Meetings/chat-transcripts/teams/`.

---

## 2. Hard Safety Boundary

Teams is intake-only.

- Never send, draft, reply, create chats, create channels, post channel messages, react, edit, delete, upload, create Planner tasks, or otherwise mutate Teams/Microsoft state.
- Preserve unread state. Use MCP/connector reads only when they do not mark items read or move read cursors.
- Unread state is chat-specific. Do not claim channel unread coverage; label channel reads as recent snapshots.
- Do not use Teams UI/browser navigation for unread review.
- Use the repo-local `teams_bridge.py` UI/clipboard fallback only as a less-portable fallback for user-provided copied text or when the user explicitly accepts that it is not unread-preserving.
- If a Teams tool implies state mutation or unread cursor movement, stop and ask the user for a safer scope or exported text.

---

## 3. Scope Protocol

1. **Explicit scope provided**: Process only the named chat, channel, team/channel pair, thread, query, person, and/or time window.
2. **Unread chat triage requested**: Use unread chat signals only if the connector exposes a read-only unread chat list.
3. **No explicit scope, configured Teams intake exists**: Use only manifest/configured Teams scopes surfaced by `python3 system/scripts/critical_commitment_refresh.py plan --mode day --json` or `3. Meetings/chat-transcripts/_manifest.json`. Do not invent tenant-wide Teams coverage.
4. **No configured scope available**: Stop and ask the user for a chat, channel, thread, query, or time window, or ask whether to paste/export Teams text.
5. **No time window provided**: Use `system/scripts/chat_intake_state.py window --platform teams --scope "<SCOPE>"` and apply the returned `effective_start_at`.

Do not broad-scan all Teams, all channels, all chats, or unknown unread surfaces.

---

## 4. Extraction Protocol

For every scoped Teams source:

1. Record source metadata: team, channel, chat, thread, timestamp/link when available, and read-only operation used.
2. Record the effective read window and whether it came from an explicit user window, the 5-business-day default, or manifest state.
3. Extract candidate action items, decisions, blockers, owner mentions, due dates, follow-up requests, and status changes.
4. Convert every candidate into a **workstream finding** before writing tasks:
   - Workstream title or best match, 9 words or fewer.
   - Display title, started date/source, latest progress source, and internal agent refs.
   - Latest outcome or status signal.
   - Explicit completed outcome/checklist signal, if any.
   - Open item with owner, action, due gate, and Teams source.
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
   - **Status tracking update**: useful status signal but no new task.
   - **Workstream update**: latest outcome, open item, recommended next action, or completed outcome for an existing workstream.
   - **Needs confirmation**: unclear owner, scope, priority, source authority, or due date.
   - **Rejected/out of scope**: fails the Priority Gate.
9. Treat explicit Teams completion evidence as eligible to check off local checklist items with completion date/source. Treat implied completion language such as "ready for review" or "should be done" as a confirmation question, not as a checked item.
10. User-facing labels, evidence prose, and owner questions must use readable task/workstream titles and source provenance. Keep Task Master IDs, Jira IDs, Trello IDs, and source IDs only in local links, metadata, or an `Agent refs` line.

---

## 5. Durable Output

Allowed writes are local repo files only:

- Teams chat transcript -> `3. Meetings/chat-transcripts/teams/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`.
- Accepted tasks -> `5. Trackers/TASK_MASTER.md` and `5. Trackers/tasks/{ID}.md` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Workstream updates -> `5. Trackers/WORKSTREAMS.md` and `5. Trackers/workstreams/{slug}.md` when present.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when materially useful.
- Run report -> `3. Meetings/reports/teams-runs/{RUN_ID}.md`.

The run report must include:

- Teams scope processed.
- Read-only operations used.
- Candidate tasks and gate outcomes.
- Workstream matches, latest outcomes, completed outcomes, open items, recommended next 3, authority tier, commitment type, and completion state.
- Chat transcript files written.
- Issues encountered and recommended follow-up.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Teams response by the user.
- Safety note confirming no Teams messages were sent and unread state was not intentionally changed.

---

## 6. Final Output

Return the workstream snapshot first using the `task-manager` title, bullet, and sub-bullet format, then a compact task-focused summary:

- Workstream updates and priority order.
- Chat transcript files saved.
- Files updated.
- Accepted tasks and IDs.
- Existing task or status updates.
- Issues and recommendations.
- Items needing confirmation or manual Teams response.
- Safety confirmation: no Teams send/mutation actions were performed.
