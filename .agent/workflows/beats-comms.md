---
description: Run scoped Slack, Teams, Outlook, and Calendar communication intake into local task updates and searchable transcripts without sending or mutating source systems.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same read-only communication intake and durable output contract.

# Workflow: `/beats-comms`

Use this workflow as the canonical communication context refresh path. Other workflows may call it before synthesis when the user asks for updated Slack, Teams, Outlook, or Calendar context, but only with explicit bounded scopes.

Read `.agent/rules/MCP_COMMUNICATION_INTAKE.md` before platform reads. It defines the shared runtime capability table for Antigravity, Codex, Claude Code, and fallback bridge behavior.

## 1. Resolve Communication Scope

Use the remainder of the user's `/beats-comms` command to determine platform scopes.

Supported scope forms:
- `slack: <channel|DM|thread|query|window>`
- `teams: <chat|channel|thread|query|window>`
- `outlook: <mail query|sender|subject|folder|window>`
- `calendar: <lookahead|date range|meeting query>`
- `both:` may be used only as a shorthand for explicit Slack and Teams scopes.

If any requested platform lacks explicit scope, ask the user for a scope before reading that platform. The default scope policy is `require_scope`.

Do not broad-scan Slack workspaces, all Teams, all channels, all chats, all DMs, all mail, all folders, full calendar history, or unknown unread surfaces.

If a platform scope omits a time window, compute the effective window with `system/scripts/chat_intake_state.py window`:
- `slack`, `teams`, and `outlook` default to 5 business days back, shortened to the newer `last_successful_processed_at` for the same platform/scope when present in `3. Meetings/chat-transcripts/_manifest.json`.
- `calendar` defaults to a 14-day forward lookahead and reports `effective_start_at` plus `effective_end_at`.

For Slack scopes that may return many results, including mention/DM intake such as `to:me`, channel history over multiple days, and any explicit window longer than 5 calendar days, pre-plan page-cap-safe reads with `system/scripts/chat_intake_state.py chunks` before calling Slack. Do not try one full-window Slack query first; follow `.agent/workflows/beats-slack.md` and execute the chunk plan oldest-to-newest.

### Manual Evidence Shortcut

If the user provides the communication evidence directly in the current turn as a screenshot, pasted email/chat text, or short exported snippet, do not require a platform scope and do not run connector window/chunk planning. Treat the user-provided artifact as the bounded source.

The shortcut still must:
- Preserve source-system safety rules.
- Save a compact transcript under `3. Meetings/chat-transcripts/{platform}/`.
- Save the platform and combined run reports.
- Record the successful run in `3. Meetings/chat-transcripts/_manifest.json`.
- Route local task/profile updates through `task-manager`.
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

## 3. Execute Platform Workflows

Run the scoped platform workflows independently:
- Slack scope -> follow `.agent/workflows/beats-slack.md`.
- Teams scope -> follow `.agent/workflows/beats-teams.md`.
- Outlook mail scope -> follow `.agent/skills/outlook-navigator/SKILL.md` with MS365 MCP/connector reads before macOS AppleScript fallback.
- Calendar scope -> follow `.agent/skills/outlook-navigator/SKILL.md` with MS365 MCP/connector schedule reads before macOS AppleScript fallback.

Each platform workflow must save its communication transcript, scan that saved transcript with `.agent/skills/atlassian-context-archive/SKILL.md`, and archive only referenced Jira/Confluence context before task routing.

If runtime supports parallel execution, platform intake may run in parallel because source reads and local transcript files are independent. Avoid concurrent writes to the same task detail file, chat intake manifest, or Atlassian manifest; merge task updates after evidence sets are collected.

## 4. Merge Results

After platform-specific transcripts and run reports are written:
- Deduplicate candidate tasks across Slack, Teams, Outlook, and Calendar.
- Deduplicate Atlassian artifact references across all processed platforms by manifest key and content hash.
- Prefer existing task updates over duplicate new tasks.
- Route accepted work to local repo files only.
- Write a combined run report to `3. Meetings/reports/chat-runs/{RUN_ID}.md`.
- Include combined issues and recommendations for MCP/connector gaps, read-state uncertainty, fallback bridge usage, Atlassian connector gaps, unresolved source URLs, duplicate skips, reference cap skips, and task routing conflicts.

## 5. Final Output

Return:
- Slack transcript files saved.
- Teams transcript files saved.
- Outlook transcript files saved.
- Calendar transcript files saved.
- Atlassian artifacts saved or skipped.
- Combined run report path.
- Files updated.
- Accepted tasks and IDs.
- Issues and recommended follow-ups.
- Manual Slack/Teams/Outlook follow-ups owned by the user.
- Safety confirmation that no source-system send or mutation actions were performed, including no Jira/Confluence mutations.
