---
description: Process scoped Slack messages into local Beats PM workstreams and tasks without sending or mutating Slack.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.

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

Use `effective_start_at` from the helper output. It defaults to 5 business days back, unless `3. Meetings/chat-transcripts/_manifest.json` or `3. Meetings/reports/command-runs/_manifest.json` has a newer successful checkpoint for the same normalized Slack source window.

## 1A. Plan Page-Cap-Safe Reads

Before the first Slack read, build a chunk plan for any Slack search/query/window that could return many matches, including `to:me`, mention/DM intake, channel history over multiple days, and any explicit window longer than 5 calendar days.

```bash
python3 system/scripts/chat_intake_state.py chunks --platform slack --scope "<SCOPE>" --start "<EFFECTIVE_START_AT>" --end "<EFFECTIVE_END_AT>"
```

Default Slack chunks are 24 hours and must be executed oldest-to-newest. Do not issue one full-window Slack query first for broad scopes; run the chunked searches from the helper and merge/deduplicate results afterward.

For each chunk, prefer exact runtime/API timestamp filters using `start_epoch` and `end_epoch` when available. If the runtime exposes only Slack search syntax, add the chunk's `slack_query_date_hint` to the original query. Chunks marked `requires_exact_time_filter` need timestamp-capable tooling; if the runtime cannot filter that tightly, stop that subrange and ask the user for a narrower channel/thread/person scope. Record the chunk plan in the transcript and run report.

If a chunk still hits a connector `page_limit_exceeded` or equivalent cap, split only that chunk with a smaller chunk size before continuing:

```bash
python3 system/scripts/chat_intake_state.py chunks --platform slack --scope "<SCOPE>" --start "<CHUNK_START_AT>" --end "<CHUNK_END_AT>" --chunk-hours 12
```

Repeat with narrower chunks as needed. If a 6-hour chunk still caps, stop that subrange, record the partial-read issue, and ask the user for a narrower channel/thread/person scope instead of silently treating the run as complete.

## 2. Bind Safety Rules

Before reading Slack, apply the user safety boundary from `SETTINGS.md`:
- Slack is intake-only.
- Use only read-only Slack MCP/connector operations: channel search, channel history read, thread read, user lookup, canvas read, and read-only message search when available.
- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, upload, create canvases/files, or otherwise mutate Slack content or workspace state.
- Preserve unread state. Do not call any tool or endpoint that marks messages read/unread, sets a read cursor, acknowledges notifications, or clears unread indicators.
- Do not use Slack UI/browser navigation to inspect unread content. Use read-only MCP/connector reads only.
- If a Slack tool implies state mutation, stop and ask the user for a safer scope or exported text.

## 3. Read Minimum Local Context

Read:
- `.agent/skills/slack-task-intake/SKILL.md`
- `.agent/skills/chat-transcript-archive/SKILL.md`
- `.agent/skills/atlassian-context-archive/SKILL.md`
- `.agent/skills/task-manager/SKILL.md`
- `.agent/rules/MCP_COMMUNICATION_INTAKE.md`
- `system/scripts/chat_intake_state.py`
- `system/scripts/atlassian_context_state.py`
- `SETTINGS.md`
- `1. Company/ways-of-working.md`
- `5. Trackers/TASK_MASTER.md`

Read optional files only when needed and when they exist:
- `4. People/`
- `2. Products/partners/`
- `5. Trackers/WORKSTREAMS.md`
- `5. Trackers/workstreams/`
- `5. Trackers/tasks/`
- `3. Meetings/chat-transcripts/_manifest.json`
- `3. Meetings/chat-transcripts/slack/`
- `3. Meetings/context-artifacts/atlassian/_manifest.json`
- `3. Meetings/context-artifacts/atlassian/jira/`
- `3. Meetings/context-artifacts/atlassian/confluence/`

## 4. Collect Slack Evidence

Use only the scoped Slack source from Step 1.

Execute Slack reads by the chunk plan from Step 1A when the scope qualifies. Merge chunk results by source URL/timestamp/message ID where available, then route the deduplicated evidence set. This prevents broad mention/DM searches from losing recent results behind connector page limits.

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
- Workstream deltas -> `5. Trackers/WORKSTREAMS.md` and matching `5. Trackers/workstreams/{slug}.md` when present.
- New action items -> `5. Trackers/TASK_MASTER.md` and task detail files in `5. Trackers/tasks/` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md` when useful and covered by the named read-only source window.
- Out-of-scope or unclear items -> final response only, with no Slack response sent.

All Slack-derived updates must be labeled as Slack evidence and include only short snippets plus source references. If an Atlassian artifact materially supports a task or status update, include the local artifact path and full Atlassian source URL in the evidence.

Before creating a new visible workstream, triangulate Slack evidence against the current workstream list. Workstream titles, task labels, evidence prose, and owner questions must be plain English and free of internal Task Master, Trello, Jira, or source IDs. Render source evidence from display provenance: readable title, started date/source, and latest progress source. Keep hard IDs only in local links, metadata, or an `Agent refs` line. Check off completed items only when Slack evidence or the user explicitly confirms completion, and preserve completion date/source.

## 8. Write Slack Run Report

Write a run report to:

```text
3. Meetings/reports/slack-runs/{RUN_ID}.md
```

The report must include:
- Slack scope processed.
- Effective read window and whether it came from the 5-business-day default, the chat manifest, or the command-run manifest.
- Chunk plan used, chunk count, any capped chunk retries, and any subrange that required user narrowing.
- Read-only Slack operations used.
- Chat transcript files written.
- Atlassian references found, artifacts written, unchanged artifacts skipped, and unresolved references.
- Candidate tasks and gate outcomes.
- Workstream outcomes, completed outcomes, open items, and recommended next 3 updates.
- Display provenance for touched tasks/workstreams plus internal refs kept out of user-facing labels.
- Issues encountered: connector unavailable or missing read-only operation, read-state uncertainty, scope too broad/missing, Atlassian connector unavailable or unauthorized, Atlassian source URL unresolved, duplicate/previously processed content skipped, reference cap exceeded, or task routing conflicts requiring manual review.
- Routed Updates listing exact local files changed or `No durable update required`.
- Items needing manual Slack response by the user.
- Safety note confirming no Slack messages were sent, unread state was not intentionally changed, and Jira/Confluence were not mutated.

After the transcript and run report are written successfully, update processed-state tracking:

```bash
python3 system/scripts/chat_intake_state.py record --platform slack --scope "<SCOPE>" --run-id <RUN_ID> --latest-source-timestamp <LATEST_SOURCE_TIMESTAMP> --transcript-path "<TRANSCRIPT_PATH>" --run-report-path "<RUN_REPORT_PATH>"
```

If Slack results do not expose a reliable latest source timestamp, omit `--latest-source-timestamp`; the helper will record run completion time and flag that issue in the manifest.

When Slack intake is invoked by `/day`, `/week`, `/boss`, or another recurring task command, also record the source result in `3. Meetings/reports/command-runs/_manifest.json` after transcript/report writes succeed.

## 9. Final Output

Return a compact summary with:
- Chat transcript files saved.
- Atlassian artifacts saved or skipped.
- Files updated.
- Accepted workstreams, tasks, and internal refs.
- Existing task updates.
- Issues and recommended follow-ups.
- Items needing confirmation or manual Slack response.
- Safety confirmation, including no Jira/Confluence mutations.
