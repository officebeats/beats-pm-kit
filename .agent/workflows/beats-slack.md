---
description: Process scoped Slack messages into local Beats PM tasks without sending or mutating Slack.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same read-only Slack intake and durable output contract.

# Workflow: `/beats-slack`

## 1. Resolve Slack Scope

Use the remainder of the user's `/beats-slack` command as the Slack scope. Valid scopes include:
- Channel name or ID.
- DM participant.
- Thread link or timestamp.
- Slack search query.
- Canvas ID.
- Time window.

If no explicit scope is provided, ask the user for a channel, DM, thread, query, or time window before reading Slack. The default scope policy is `require_scope`.

Do not broad-scan Slack workspaces, all channels, all DMs, or unknown unread surfaces.

If the scope omits a time window, compute the effective read window before reading Slack:

```bash
python3 system/scripts/chat_intake_state.py window --platform slack --scope "<SCOPE>"
```

Use `effective_start_at` from the helper output. It defaults to 5 business days back, unless `3. Meetings/chat-transcripts/_manifest.json` has a newer `last_successful_processed_at` for the same normalized Slack scope.

## 2. Bind Safety Rules

Before reading Slack, apply the user safety boundary from `SETTINGS.md`:
- Slack is intake-only.
- Use only read-only Slack connector operations: channel search, channel history read, thread read, user lookup, canvas read, and read-only message search when available.
- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, upload, create canvases/files, or otherwise mutate Slack content or workspace state.
- Preserve unread state. Do not call any tool or endpoint that marks messages read/unread, sets a read cursor, acknowledges notifications, or clears unread indicators.
- Do not use Slack UI/browser navigation to inspect unread content. Use read-only connector reads only.
- If a Slack tool implies state mutation, stop and ask the user for a safer scope or exported text.

## 3. Read Minimum Local Context

Read:
- `.agent/skills/slack-task-intake/SKILL.md`
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
- `3. Meetings/chat-transcripts/slack/`
- `3. Meetings/context-artifacts/atlassian/_manifest.json`
- `3. Meetings/context-artifacts/atlassian/jira/`
- `3. Meetings/context-artifacts/atlassian/confluence/`

## 4. Collect Slack Evidence

Use only the scoped Slack source from Step 1.

For each read-only Slack result, capture:
- Source channel/DM/thread/canvas.
- Effective start timestamp from `chat_intake_state.py` or the explicit user-provided time window.
- Timestamp or link when available.
- Requester or source participant.
- Short evidence snippet.
- Candidate owner and due date when stated.
- Jira and Confluence references mentioned in the scoped evidence.

Do not store full unbounded Slack message dumps in local files.

## 5. Save Searchable Chat Transcript

Execute `.agent/skills/chat-transcript-archive/SKILL.md`.

Write a Slack chat transcript to:

```text
3. Meetings/chat-transcripts/slack/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md
```

The transcript must include source metadata, read-only operations used, evidence snippets, Atlassian references found, candidate tasks/status changes, routed updates, manual follow-ups, and safety confirmation.

## 6. Capture Referenced Atlassian Context

Execute `.agent/skills/atlassian-context-archive/SKILL.md` after the Slack transcript is written.

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
python3 system/scripts/atlassian_context_state.py record --reference-type jira|confluence --reference-id "<REFERENCE_ID>" --source-url "<FULL_ATLASSIAN_URL>" --run-id <RUN_ID> --platform slack --transcript-path "<TRANSCRIPT_PATH>"
```

Every successful artifact must include `source_url` in frontmatter and a visible `Source: <full Atlassian URL>` link near the top. If the full URL cannot be resolved, skip artifact creation and report the issue.

## 7. Extract And Route Tasks

Execute `.agent/skills/slack-task-intake/SKILL.md` with `task-manager` Priority Gate rules:
- New action items -> `5. Trackers/TASK_MASTER.md` and task detail files in `5. Trackers/tasks/` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when useful and bounded.
- Out-of-scope or unclear items -> final response only, with no Slack response sent.

All Slack-derived updates must be labeled as Slack evidence and include only short snippets plus source references. If an Atlassian artifact materially supports a task or status update, include the local artifact path and full Atlassian source URL in the evidence.

## 8. Write Slack Run Report

Write a run report to:

```text
3. Meetings/reports/slack-runs/{RUN_ID}.md
```

The report must include:
- Slack scope processed.
- Effective read window and whether it came from the 5-business-day default or the manifest.
- Read-only Slack operations used.
- Chat transcript files written.
- Atlassian references found, artifacts written, unchanged artifacts skipped, and unresolved references.
- Candidate tasks and gate outcomes.
- Issues encountered: connector unavailable or missing read-only operation, read-state uncertainty, scope too broad/missing, Atlassian connector unavailable or unauthorized, Atlassian source URL unresolved, duplicate/previously processed content skipped, reference cap exceeded, or task routing conflicts requiring manual review.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Slack response by the user.
- Safety note confirming no Slack messages were sent, unread state was not intentionally changed, and Jira/Confluence were not mutated.

After the transcript and run report are written successfully, update processed-state tracking:

```bash
python3 system/scripts/chat_intake_state.py record --platform slack --scope "<SCOPE>" --run-id <RUN_ID> --latest-source-timestamp <LATEST_SOURCE_TIMESTAMP> --transcript-path "<TRANSCRIPT_PATH>" --run-report-path "<RUN_REPORT_PATH>"
```

If Slack results do not expose a reliable latest source timestamp, omit `--latest-source-timestamp`; the helper will record run completion time and flag that issue in the manifest.

## 9. Final Output

Return a compact summary with:
- Chat transcript files saved.
- Atlassian artifacts saved or skipped.
- Files updated.
- Accepted tasks and IDs.
- Existing task updates.
- Issues and recommended follow-ups.
- Items needing confirmation or manual Slack response.
- Safety confirmation, including no Jira/Confluence mutations.
