---
description: Run scoped Slack, Teams, Outlook, Calendar, and transcript intake into local workstream/task updates without sending or mutating source systems.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same read-only communication intake and durable output contract.

# Workflow: `/beats-comms`

Use this workflow as the canonical communication context refresh path. Other workflows may call it before synthesis when the user asks for updated Slack, Teams, Outlook, Calendar, Quill, Granola, or manually pasted transcript context, but only with explicit named read-only source windows or user-provided evidence.

Read `.agent/rules/MCP_COMMUNICATION_INTAKE.md` before platform reads. It defines the shared runtime capability table for Antigravity, Codex, Claude Code, and fallback bridge behavior.

## 0. PM Decision Router Preflight

Load `.agent/skills/pm-decision-router/SKILL.md` before task routing. For manual evidence snippets, saved transcript abstracts, or connector result summaries, classify the text with:

```bash
python3 system/scripts/pm_decision_router.py --text "<communication evidence>"
```

Use the router result only after named read-only source evidence has been collected. `scope_challenge` and `ask_user` results must be returned as explicit questions; do not create active Task Master work from ambiguous communication evidence. Source-system safety rules remain stronger than router output.

## 1. Resolve Communication Scope

Use the remainder of the user's `/beats-comms` command to determine platform scopes.

If `/beats-comms` is called by `/day`, `/week`, or `/boss`, first use the caller's `critical_commitment_refresh.py plan` output. Manifest-backed scopes from that plan are explicit named read-only source windows for this run.

Supported scope forms:
- `slack: <channel|DM|thread|query|window>`
- `teams: <chat|channel|thread|query|window>`
- `outlook: <mail query|sender|subject|folder|window>`
- `calendar: <lookahead|date range|meeting query>`
- `transcripts: <manual|quill|granola|packet|meeting title|window>`
- `both:` may be used only as a shorthand for explicit Slack and Teams scopes.

If any requested or expected platform lacks explicit scope, ask the user for a scope before reading that platform. The default scope policy is `require_scope`.

Do not broad-scan Slack workspaces, all Teams, all channels, all chats, all DMs, all mail, all folders, full calendar history, or unknown unread surfaces.

If a platform scope omits a time window, compute the effective window with `system/scripts/chat_intake_state.py window`:
- `slack`, `teams`, and `outlook` default to 5 business days back, shortened to the newer successful checkpoint for the same platform/scope when present in `3. Meetings/chat-transcripts/_manifest.json` or `3. Meetings/reports/command-runs/_manifest.json`.
- `calendar` includes the last 5 business days of calendar changes plus forward lookahead, shortened only when the same calendar source/window has a newer successful checkpoint.

For Slack scopes that may return many results, including mention/DM intake such as `to:me`, channel history over multiple days, and any explicit window longer than 5 calendar days, pre-plan page-cap-safe reads with `system/scripts/chat_intake_state.py chunks` before calling Slack. Do not try one full-window Slack query first; follow `.agent/workflows/beats-slack.md` and execute the chunk plan oldest-to-newest.

### Manual Evidence Shortcut

If the user provides the communication evidence directly in the current turn as a screenshot, pasted email/chat text, transcript excerpt, meeting notes, or short exported snippet, do not require a platform scope and do not run connector window/chunk planning. Treat the user-provided artifact as the named read-only source for this run.

The shortcut still must:
- Preserve source-system safety rules.
- Save a compact transcript under `3. Meetings/chat-transcripts/{platform}/`.
- Save the platform and combined run reports.
- Record the successful run in `3. Meetings/chat-transcripts/_manifest.json`.
- Record the command/source outcome in `3. Meetings/reports/command-runs/_manifest.json` when this intake is invoked by a recurring task command.
- Route local task/profile updates through `task-manager`.
- Triangulate the extracted signal against `5. Trackers/WORKSTREAMS.md` and matching `5. Trackers/workstreams/` files when present.
- Run targeted task health refresh with `python3 system/scripts/task_master_triage.py --apply --touched-task <TASK_ID>` for each touched task.

Escalate back to the normal scoped connector flow only when the screenshot/snippet is insufficient and fresh source-system reading is needed.

## 2. Bind Safety Rules

This workflow is read-only for source systems:
- Never send, draft, schedule, reply, forward, react, edit, delete, pin, bookmark, upload, create chats/channels/canvases/files/Planner tasks, create calendar events, create meeting invites, or otherwise mutate Slack, Teams, Outlook, Calendar, or Microsoft state.
- Never create, send, forward, or reply to email unless the user explicitly asks for that specific message in the current turn; default to draft text in chat or local artifacts.
- Never create, edit, transition, comment, assign, add worklogs, update pages, delete, or otherwise mutate Jira or Confluence while enriching referenced context.
- Preserve unread state. Do not call tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Do not use Slack, Teams, Outlook, or Calendar UI/browser navigation for unread review.
- Use MCP/connector reads only when they are read-only; otherwise ask for user-provided export/text.
- If an expected connector, manifest-backed scope, or fallback integration fails, stop and prompt the user with the failure, risk if skipped, recommended fix, and safe choices. Do not silently continue degraded.

## 3. Execute Platform Workflows

Run the scoped platform workflows independently:
- Slack scope -> follow `.agent/workflows/beats-slack.md`.
- Teams scope -> follow `.agent/workflows/beats-teams.md`.
- Outlook mail scope -> follow `.agent/skills/outlook-navigator/SKILL.md` with MS365 MCP/connector reads before macOS AppleScript fallback.
- Calendar scope -> follow `.agent/skills/outlook-navigator/SKILL.md` with MS365 MCP/connector schedule reads before macOS AppleScript fallback.
- Transcript scope -> follow `.agent/workflows/transcript.md`; prefer read-only Quill/Granola MCP or export paths when available, otherwise use manual/user-provided text or local transcript packets only.

Each platform workflow must save its communication transcript, scan that saved transcript with `.agent/skills/atlassian-context-archive/SKILL.md`, and archive only referenced Jira/Confluence context before task routing.

If runtime supports parallel execution, platform intake may run in parallel because source reads and local transcript files are independent. Avoid concurrent writes to the same task detail file, chat intake manifest, or Atlassian manifest; merge task updates after evidence sets are collected.

For recurring `/day`, `/week`, and `/boss` callers, prefer parallel source agents for Slack, Outlook/Calendar, Teams, transcript/Quill/Granola, and second-brain context so the full run stays within the 90-second budget. Token cost is secondary to wall-clock speed unless the user says otherwise.

## 4. Merge Results

After platform-specific transcripts and run reports are written:
- Deduplicate candidate tasks and open items across Slack, Teams, Outlook, Calendar, manual transcripts, Quill, Granola, and local transcript packets.
- Deduplicate Atlassian artifact references across all processed platforms by manifest key and content hash.
- Prefer existing task updates over duplicate new tasks.
- Map every accepted item to a succinct workstream title of 9 words or fewer. Do not expose internal IDs in user-facing workstream titles.
- Render user-facing task/workstream evidence from display provenance: readable title, started date/source, and latest progress source. Keep Task Master IDs, Jira IDs, Trello IDs, and source IDs only in local links, metadata, or an `Agent refs` line.
- Update latest outcomes, completed outcomes, open items, and recommended next 3 actions on the relevant workstream when evidence supports it.
- Check off completed checklist items only when the source evidence or user confirmation explicitly confirms completion; keep completion date/source visible.
- Route accepted work to local repo files only.
- Write a combined run report to `3. Meetings/reports/chat-runs/{RUN_ID}.md`.
- Include combined issues and recommendations for MCP/connector gaps, read-state uncertainty, fallback bridge usage, Atlassian connector gaps, unresolved source URLs, duplicate skips, reference cap skips, and task routing conflicts.

## 5. Final Output

Return:
- Slack transcript files saved.
- Teams transcript files saved.
- Outlook transcript files saved.
- Calendar transcript files saved.
- Transcript packet, Quill, Granola, or manual transcript files processed.
- Atlassian artifacts saved or skipped.
- Combined run report path.
- Files updated.
- Accepted workstreams, tasks, and internal refs.
- Latest outcomes, completed outcomes, open items, and recommended next 3 by workstream.
- Issues and recommended follow-ups.
- Manual Slack/Teams/Outlook follow-ups owned by the user.
- Safety confirmation that no source-system send or mutation actions were performed, including no Jira/Confluence mutations.
