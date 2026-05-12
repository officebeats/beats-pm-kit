---
name: chat-transcript-archive
description: Persist scoped Slack, Teams, Outlook, and Calendar reads as searchable local communication transcripts with metadata, evidence snippets, and task-routing results.
priority: P0
maxTokens: 2500
triggers:
  - "/beats-slack"
  - "/beats-teams"
  - "/beats-comms"
version: 1.1.0
author: Beats PM Brain
---

# Chat Transcript Archive Skill

> **Role**: Save communication intake into the kit as searchable local evidence without mutating the source system.

## 1. Archive Paths

Write communication transcripts under:

```text
3. Meetings/chat-transcripts/{platform}/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md
```

Valid platform values are:
- `slack`
- `teams`
- `outlook`
- `calendar`

Write combined run reports under:

```text
3. Meetings/reports/chat-runs/{RUN_ID}.md
```

Platform-specific workflows may also write:
- `3. Meetings/reports/slack-runs/{RUN_ID}.md`
- `3. Meetings/reports/teams-runs/{RUN_ID}.md`
- `3. Meetings/reports/outlook-runs/{RUN_ID}.md`
- `3. Meetings/reports/calendar-runs/{RUN_ID}.md`

Referenced Jira and Confluence context may be archived under:

```text
3. Meetings/context-artifacts/atlassian/{jira|confluence}/
3. Meetings/context-artifacts/atlassian/_manifest.json
```

Track processed state in:

```text
3. Meetings/chat-transcripts/_manifest.json
```

---

## 2. Transcript Contract

Every saved communication transcript must include:

- Platform.
- Scope processed.
- Time window or bounded read size.
- Effective read window source: explicit user window, 5-business-day default, 14-day calendar lookahead, or manifest-shortened window.
- Read-only operations used.
- Source references such as channel, chat, thread, mail subject, mailbox folder, calendar title, timestamp, or link when available.
- Jira and Confluence references found in the scoped evidence.
- Participants or requester when available.
- Message/event evidence as short snippets, not full unbounded dumps.
- Candidate tasks, decisions, blockers, owners, and due dates.
- Routed Updates listing exact local files changed or `No durable update required`.
- Safety note confirming no send/mutation actions were performed and unread state was not intentionally changed.
- Issues and recommendations for MCP/connector gaps, read-state uncertainty, fallback bridge usage, duplicates skipped, or task routing conflicts.
- Atlassian artifact paths written or skipped when referenced context capture runs.

For user-provided screenshots, pasted email/chat snippets, or short exports, mark the read source as `user-provided evidence` and keep the same transcript sections. It is acceptable for `Source References` to contain screenshot-visible metadata instead of connector URLs. Do not run source-system window calculation or connector reads just to satisfy this contract.

Use this Markdown shape:

```md
# Communication Transcript — <platform> — <scope>

**Date Captured**: <YYYY-MM-DD HH:MM local>
**Run ID**: <RUN_ID>
**Platform**: <Slack|Teams|Outlook|Calendar>
**Scope**: <channel/chat/thread/mail query/calendar query/window>
**Effective Window**: <start/end or bounded size>
**Read Policy**: Read-only; no send or mutation actions.
**Unread Policy**: No intentional read/unread mutation.

## Source References
- ...

## Atlassian References
- Jira/Confluence references found, artifacts written, or unresolved references.

## Evidence Snippets
- ...

## Candidate Tasks
| Status | Owner | Due | Task | Evidence |
| --- | --- | --- | --- | --- |

## Decisions / Status Changes
- ...

## Routed Updates
- ...

## Issues And Recommendations
- ...

## Manual Follow-Ups
- ...

## Safety Confirmation
- No source-system messages, emails, or calendar invites were sent.
- No source-system mutation tools were used.
- Unread state was not intentionally changed.
```

---

## 3. Privacy And Searchability

- Keep transcripts local to the repo.
- Prefer source links and short snippets over full conversation dumps.
- Do not include secrets, tokens, credentials, or private unrelated chatter.
- Use stable filenames with date, scope slug, and run ID so repo search can find the source later.
- Use `system/scripts/chat_intake_state.py record` only after transcript and report writes succeed.
- If an MCP/connector returns only partial or redacted content, state that limitation in the transcript.

---

## 4. Context Refresh Integration

Use this skill as the durable memory step whenever a communication intake run should refresh the kit's working context before synthesis.

Eligible callers include:
- `/beats-slack`, `/beats-teams`, and `/beats-comms`.
- Daily, weekly, status, prep, create, or other context-consuming workflows when the user explicitly asks for current chat context and provides a bounded platform scope.

This skill does not initiate source-system reads by itself. A caller must first resolve the platform scope and read only that bounded source through the platform intake workflow.

Required refresh order:

1. Resolve an explicit or configured scope for Slack, Teams, Outlook, Calendar, or a bounded combination.
2. If the scope has no time window, run `system/scripts/chat_intake_state.py window` and use the returned `effective_start_at`.
3. For Slack scopes likely to return many results, run `system/scripts/chat_intake_state.py chunks` and execute the returned chunks before merging/deduplicating evidence.
4. Read source messages/events only with read-only MCP/connector operations allowed by the platform workflow.
5. Save the communication transcript using this contract.
6. Scan the saved transcript for referenced Jira and Confluence context, then archive only referenced artifacts when read-only Atlassian access is available.
7. Route accepted local task updates through the task manager rules.
8. Write the platform run report and record the successful run in `3. Meetings/chat-transcripts/_manifest.json`.
9. Hand the new transcript path, run report path, routed update paths, and unresolved follow-ups back to the caller so they are included in the context synthesis.

If a context-consuming workflow asks for fresh Slack, Teams, Outlook, or Calendar context but no bounded scope is available, do not read the source system. Ask for a channel, chat, DM, thread, mail query, calendar lookahead, or time window, or continue using existing local transcripts.

Cross-runtime Slack MCP/connector mapping:
- Allowed read-only operations when surfaced: channel search, channel history read, thread read, canvas read, user lookup, and read-only message search.
- Prohibited operations: send, schedule, draft, reply, react, edit, delete, pin, bookmark, upload, create canvases/files, or any operation that changes read/unread state.
- High-volume searches must be pre-chunked with `chat_intake_state.py chunks` so connector page caps do not hide later results.

Cross-runtime Teams MCP/connector mapping:
- Allowed read-only operations when surfaced: chat/channel search, bounded message reads, thread/reply reads, user or team/channel lookup, meeting transcript reads, and file/context reads needed to interpret the scoped messages.
- Prohibited operations: send, draft, reply, react, edit, delete, create chats/channels/meetings/Planner tasks, upload files, or any operation that changes read/unread state.
- If read-only Teams retrieval is not surfaced in the current runtime, process only user-provided Teams exports, pasted chat text, or saved local notes, and record the connector gap in the transcript and run report.

Cross-runtime Outlook/Calendar MCP/connector mapping:
- Allowed read-only operations when surfaced: bounded mail search/list/get, folder metadata, attachment metadata, calendar event list/get, schedule view, meeting metadata, and meeting transcript reads when explicitly scoped.
- Prohibited operations: send, draft, reply, forward, delete, move, mark read/unread, create/update/cancel events, create meeting invites, update reminders, create Planner/Todo items, or any operation that changes mailbox/calendar state.
- If MS365 MCP/connector retrieval is unavailable, use `outlook_bridge.py` only as a less-portable macOS AppleScript fallback and record that limitation in the transcript and run report.

The manifest is the dedupe gate for context refresh. A successful run may shorten future windows for the same normalized platform scope, but it must not suppress a user-requested explicit time window.

---

## 5. Final Output

When this skill is used, report:

- Communication transcript file path.
- Run report path, if written.
- Local task files updated.
- Manual follow-ups still owned by the user.
