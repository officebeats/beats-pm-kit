---
description: Process all Quill meetings from the last 10 business days.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same repo-local pipeline and durable output contract.

# Workflow: `/transcript`

## 1. Prepare Deterministic Intake

Run the canonical pipeline before any model synthesis:

```bash
python3 system/scripts/transcript_pipeline.py prepare --business-days 10 --json
```

This step must:
- Import recent Quill transcripts when available.
- Normalize date-stamped files from `0. Incoming/` into `3. Meetings/transcripts/`.
- Collect Outlook inbox/calendar context.
- Attempt Teams context capture without failing the run when Teams access is unavailable.
- Update `3. Meetings/transcripts/_manifest.json`.
- Create synthesis packets in `3. Meetings/reports/packets/`.
- Write a run report in `3. Meetings/reports/transcript-runs/`.

If using the universal gateway, prefer:

```bash
python3 system/scripts/beats.py transcript -- --json
```

## 1A. Optional Slack Task Intake (Read-Only)

Only include Slack when the user explicitly asks `/transcript` to process Slack or provides a Slack scope such as a channel, DM, thread, search term, or time window.

Slack is an intake-only source for task compilation:
- Use only read-only Slack connector operations: channel search, channel history read, thread read, user lookup, canvas read, and read-only message search when available.
- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, create canvases/files, or otherwise mutate Slack content or workspace state.
- Preserve unread state. Do not call any tool or endpoint that marks messages read/unread, sets a read cursor, acknowledges notifications, or clears unread indicators. If a Slack tool implies state mutation, stop and ask the user.
- Do not use Slack UI/browser navigation to inspect unread content. Use read-only connector reads so unread Slack items remain under the user's manual control.

For scoped Slack sources, extract candidate tasks with:
- Source channel/DM/thread, timestamp or link when available, requester, owner, due date, and a short evidence snippet.
- Priority Gate outcome from `task-manager`.
- Routing decision: accepted task, existing-task update, or candidate requiring user confirmation.

Accepted Slack-derived tasks may update local repo trackers only. They must not trigger Slack follow-up messages; uncertain items should be listed in the final response for the user to handle manually.

## 2. Process Only Packets

Use only packet files listed in the prepare output. Do **not** broad-scan `3. Meetings/transcripts/` to decide what to process.

Each packet includes:
- Transcript source path, hash, title, date, and expected summary path.
- Candidate task IDs and people profiles.
- Manager / partner / customer classification hints.
- Required routing checklist.
- Summary contract for hybrid appendix output.

## 3. Synthesize With `meeting-synth`

For every packet:
1. Read the packet JSON.
2. Read the referenced transcript only when needed for synthesis evidence.
3. Execute `.agent/skills/meeting-synth/SKILL.md`.
4. Write the summary to the packet's `expected_summary_path`.
5. Use the hybrid appendix contract:
   - Include `Source Transcript`.
   - Include `Transcript SHA256`.
   - Include `Pipeline Run ID`.
   - Include `Key Evidence` snippets.
   - Include `Routed Updates`.
   - Do **not** append the full raw transcript by default.

## 4. Route Durable Updates

Apply the packet routing checklist:
- New action items -> `5. Trackers/TASK_MASTER.md` and detail files in `5. Trackers/tasks/` when needed.
- Existing task updates -> task detail `Progress Log` / `Stakeholder Quotes`.
- Stakeholder enrichment -> `4. People/{firstname-lastname}.md`.
- Manager-mode updates -> `1. Company/ways-of-working.md`, manager profile, stakeholder dynamics, and scope changes.
- Partner/customer updates -> relevant `2. Products/partners/` or client/product files when applicable.

Every summary must include a `Routed Updates` section that lists the exact files updated or says `No durable update required`.

Slack-derived updates must be labeled as Slack evidence in `Routed Updates`, include only short snippets rather than full message dumps, and preserve the original Slack read/unread state.

## 5. Validate

After all summaries and durable updates are written, run:

```bash
python3 system/scripts/transcript_pipeline.py validate --run-id <RUN_ID> --json
```

Validation must mark each manifest item as `validated` or `validation_failed` and record missing summary contract fields.

## 6. Recent Meetings Output

Generate the final compact response from validated summaries:

```bash
python3 system/scripts/transcript_pipeline.py recent --limit 5 --md
```

If validation fails, report the errors and the run report path before summarizing partial results.
