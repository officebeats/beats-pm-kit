---
name: chat-transcript-archive
description: Persist scoped Slack and Teams chat reads as searchable local chat transcripts with metadata, evidence snippets, and task-routing results.
priority: P0
maxTokens: 2500
triggers:
  - "/beats-slack"
  - "/beats-teams"
  - "/beats-comms"
version: 1.0.0
author: Beats PM Brain
---

# Chat Transcript Archive Skill

> **Role**: Save communication intake into the kit as searchable local evidence without mutating the source system.

## 1. Archive Paths

Write chat transcripts under:

```text
3. Meetings/chat-transcripts/{platform}/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md
```

Valid platform values are:
- `slack`
- `teams`

Write combined run reports under:

```text
3. Meetings/reports/chat-runs/{RUN_ID}.md
```

Platform-specific workflows may also write:
- `3. Meetings/reports/slack-runs/{RUN_ID}.md`
- `3. Meetings/reports/teams-runs/{RUN_ID}.md`

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

Every saved chat transcript must include:

- Platform.
- Scope processed.
- Time window or bounded read size.
- Effective read window source: explicit user window, 5-business-day default, or manifest-shortened window.
- Read-only operations used.
- Source references such as channel, chat, thread, timestamp, or link when available.
- Jira and Confluence references found in the scoped evidence.
- Participants or requester when available.
- Message evidence as short snippets, not full unbounded dumps.
- Candidate tasks, decisions, blockers, owners, and due dates.
- Routed Updates listing exact local files changed or `No durable update required`.
- Safety note confirming no send/mutation actions were performed and unread state was not intentionally changed.
- Issues and recommendations for connector gaps, read-state uncertainty, duplicates skipped, or task routing conflicts.
- Atlassian artifact paths written or skipped when referenced context capture runs.

Use this Markdown shape:

```md
# Chat Transcript — <platform> — <scope>

**Date Captured**: <YYYY-MM-DD HH:MM local>
**Run ID**: <RUN_ID>
**Platform**: <Slack|Teams>
**Scope**: <channel/chat/thread/query/window>
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
- No source-system messages were sent.
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
- If a connector returns only partial or redacted content, state that limitation in the transcript.

---

## 4. Final Output

When this skill is used, report:

- Chat transcript file path.
- Run report path, if written.
- Local task files updated.
- Manual follow-ups still owned by the user.
