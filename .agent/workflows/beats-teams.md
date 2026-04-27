---
description: Process scoped Microsoft Teams chats or channels into local Beats PM tasks and searchable chat transcripts without sending or mutating Teams.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same read-only Teams intake and durable output contract.

# Workflow: `/beats-teams`

## 1. Resolve Teams Scope

Use the remainder of the user's `/beats-teams` command as the Teams scope. Valid scopes include:
- Chat name, participant, or ID.
- Team and channel.
- Thread link or timestamp.
- Teams search query.
- Time window.
- `unread chats` when the connector exposes read-only unread chat listing.

If no explicit scope is provided, ask the user for a chat, channel, thread, query, or time window before reading Teams. The default scope policy is `require_scope`.

Do not broad-scan all Teams, all channels, all chats, or unknown unread surfaces.

If the scope omits a time window, compute the effective read window before reading Teams:

```bash
python3 system/scripts/chat_intake_state.py window --platform teams --scope "<SCOPE>"
```

Use `effective_start_at` from the helper output. It defaults to 5 business days back, unless `3. Meetings/chat-transcripts/_manifest.json` has a newer `last_successful_processed_at` for the same normalized Teams scope.

## 2. Bind Safety Rules

Before reading Teams, apply the user safety boundary from `SETTINGS.md`:
- Teams is intake-only.
- Use only read-only Teams connector operations when available: profile resolution, chat listing, unread chat listing, chat message reads, recent thread listing, team/channel resolution, and channel message reads.
- Never send, draft, reply, create chats, create channels, post channel messages, react, edit, delete, upload, create Planner tasks, or otherwise mutate Teams/Microsoft state.
- Preserve unread state. Do not call any tool or endpoint that marks messages read/unread, sets a read cursor, acknowledges notifications, or clears unread indicators.
- Unread state is chat-specific. Do not claim channel unread coverage; label channel reads as recent snapshots.
- Do not use Teams UI/browser navigation to inspect unread content.
- Use `system/scripts/teams_bridge.py` only for user-provided copied text or when the user explicitly accepts that UI/clipboard capture is not unread-preserving.
- If a Teams tool implies state mutation, stop and ask the user for a safer scope or exported text.

## 3. Read Minimum Local Context

Read:
- `.agent/skills/teams-task-intake/SKILL.md`
- `.agent/skills/chat-transcript-archive/SKILL.md`
- `.agent/skills/atlassian-context-archive/SKILL.md`
- `.agent/skills/task-manager/SKILL.md`
- `system/scripts/chat_intake_state.py`
- `system/scripts/atlassian_context_state.py`
- `SETTINGS.md`
- `1. Company/ways-of-working.md`
- `5. Trackers/TASK_MASTER.md`

Read optional files only when needed and when they exist:
- `4. People/`
- `2. Products/partners/`
- `5. Trackers/tasks/`
- `3. Meetings/chat-transcripts/_manifest.json`
- `3. Meetings/chat-transcripts/teams/`
- `3. Meetings/context-artifacts/atlassian/_manifest.json`
- `3. Meetings/context-artifacts/atlassian/jira/`
- `3. Meetings/context-artifacts/atlassian/confluence/`

## 4. Collect Teams Evidence

Use only the scoped Teams source from Step 1.

For each read-only Teams result, capture:
- Source team/channel/chat/thread.
- Effective start timestamp from `chat_intake_state.py` or the explicit user-provided time window.
- Timestamp or link when available.
- Requester or source participant.
- Short evidence snippet.
- Candidate owner and due date when stated.
- Whether the source was an unread chat signal or recent channel snapshot.
- Jira and Confluence references mentioned in the scoped evidence.

Do not store full unbounded Teams message dumps in local files.

## 5. Save Searchable Chat Transcript

Execute `.agent/skills/chat-transcript-archive/SKILL.md`.

Write a Teams chat transcript to:

```text
3. Meetings/chat-transcripts/teams/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md
```

The transcript must include source metadata, read-only operations used, evidence snippets, Atlassian references found, candidate tasks/status changes, routed updates, manual follow-ups, and safety confirmation.

## 6. Capture Referenced Atlassian Context

Execute `.agent/skills/atlassian-context-archive/SKILL.md` after the Teams transcript is written.

Scan only the saved transcript:

```bash
python3 system/scripts/atlassian_context_state.py scan --transcript-path "<TRANSCRIPT_PATH>"
```

For each Jira or Confluence reference returned, use only read-only Atlassian connector operations to fetch source context:
- Jira issue keys and Jira URLs -> resolve/fetch the referenced Jira issue.
- Confluence URLs -> fetch the referenced Confluence page.

Never create, edit, transition, comment, assign, add worklogs, update pages, delete, or otherwise mutate Jira or Confluence.

Write fetched artifacts through the helper:

```bash
python3 system/scripts/atlassian_context_state.py record --reference-type jira|confluence --reference-id "<REFERENCE_ID>" --source-url "<FULL_ATLASSIAN_URL>" --run-id <RUN_ID> --platform teams --transcript-path "<TRANSCRIPT_PATH>"
```

Every successful artifact must include `source_url` in frontmatter and a visible `Source: <full Atlassian URL>` link near the top. If the full URL cannot be resolved, skip artifact creation and report the issue.

## 7. Extract And Route Tasks

Execute `.agent/skills/teams-task-intake/SKILL.md` with `task-manager` Priority Gate rules:
- New action items -> `5. Trackers/TASK_MASTER.md` and task detail files in `5. Trackers/tasks/` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Status tracking updates -> relevant task detail progress logs or final response only.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when useful and bounded.
- Out-of-scope or unclear items -> final response only, with no Teams response sent.

All Teams-derived updates must be labeled as Teams evidence and include only short snippets plus source references. If an Atlassian artifact materially supports a task or status update, include the local artifact path and full Atlassian source URL in the evidence.

## 8. Write Teams Run Report

Write a run report to:

```text
3. Meetings/reports/teams-runs/{RUN_ID}.md
```

The report must include:
- Teams scope processed.
- Effective read window and whether it came from the 5-business-day default or the manifest.
- Read-only Teams operations used.
- Chat transcript files written.
- Atlassian references found, artifacts written, unchanged artifacts skipped, and unresolved references.
- Candidate tasks and gate outcomes.
- Issues encountered: connector unavailable or missing read-only operation, read-state uncertainty, scope too broad/missing, Atlassian connector unavailable or unauthorized, Atlassian source URL unresolved, duplicate/previously processed content skipped, reference cap exceeded, or task routing conflicts requiring manual review.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Teams response by the user.
- Safety note confirming no Teams messages were sent, unread state was not intentionally changed, and Jira/Confluence were not mutated.

After the transcript and run report are written successfully, update processed-state tracking:

```bash
python3 system/scripts/chat_intake_state.py record --platform teams --scope "<SCOPE>" --run-id <RUN_ID> --latest-source-timestamp <LATEST_SOURCE_TIMESTAMP> --transcript-path "<TRANSCRIPT_PATH>" --run-report-path "<RUN_REPORT_PATH>"
```

If Teams results do not expose a reliable latest source timestamp, omit `--latest-source-timestamp`; the helper will record run completion time and flag that issue in the manifest.

## 9. Final Output

Return a compact summary with:
- Chat transcript files saved.
- Atlassian artifacts saved or skipped.
- Files updated.
- Accepted tasks and IDs.
- Existing task or status updates.
- Issues and recommended follow-ups.
- Items needing confirmation or manual Teams response.
- Safety confirmation, including no Jira/Confluence mutations.
