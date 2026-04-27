---
description: Run scoped Slack and Teams communication intake into local task updates and searchable chat transcripts without sending or mutating source systems.
---

> **Compatibility Directive**: Antigravity is canonical. Codex, Claude Code, Claude Desktop, Gemini CLI, and other CLIs must follow the same read-only communication intake and durable output contract.

# Workflow: `/beats-comms`

## 1. Resolve Communication Scope

Use the remainder of the user's `/beats-comms` command to determine platform scopes.

Supported scope forms:
- `slack: <channel|DM|thread|query|window>`
- `teams: <chat|channel|thread|query|window>`
- `both: <bounded shared time window or explicit scopes>`

If either platform lacks explicit scope, ask the user for a scope before reading that platform. The default scope policy is `require_scope`.

Do not broad-scan Slack or Teams workspaces, all channels, all chats, all DMs, or unknown unread surfaces.

If a platform scope omits a time window, that platform workflow must compute the effective read window with `system/scripts/chat_intake_state.py window`. The default is 5 business days back, shortened to the newer `last_successful_processed_at` for the same platform/scope when present in `3. Meetings/chat-transcripts/_manifest.json`.

## 2. Bind Safety Rules

This workflow is read-only for source systems:
- Never send, draft, schedule, reply, react, edit, delete, pin, bookmark, upload, create chats/channels/canvases/files/Planner tasks, or otherwise mutate Slack, Teams, or Microsoft state.
- Never create, edit, transition, comment, assign, add worklogs, update pages, delete, or otherwise mutate Jira or Confluence while enriching referenced context.
- Preserve unread state. Do not call tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Do not use Slack or Teams UI/browser navigation for unread review.
- Use connector reads only when they are read-only; otherwise ask for user-provided export/text.

## 3. Execute Platform Workflows

Run the scoped platform workflows independently:
- Slack scope -> follow `.agent/workflows/beats-slack.md`.
- Teams scope -> follow `.agent/workflows/beats-teams.md`.

Each platform workflow must save its chat transcript, scan that saved transcript with `.agent/skills/atlassian-context-archive/SKILL.md`, and archive only referenced Jira/Confluence context before task routing.

If runtime supports parallel execution, Slack and Teams intake may run in parallel because their source reads and local transcript files are independent. Avoid concurrent writes to the same task detail file or the Atlassian manifest; merge task updates after both evidence sets are collected.

## 4. Merge Results

After platform-specific transcripts and run reports are written:
- Deduplicate candidate tasks across Slack and Teams.
- Deduplicate Atlassian artifact references across Slack and Teams by manifest key and content hash.
- Prefer existing task updates over duplicate new tasks.
- Route accepted work to local repo files only.
- Write a combined run report to `3. Meetings/reports/chat-runs/{RUN_ID}.md`.
- Include combined issues and recommendations for connector gaps, read-state uncertainty, Atlassian connector gaps, unresolved source URLs, duplicate skips, reference cap skips, and task routing conflicts.

## 5. Final Output

Return:
- Slack transcript files saved.
- Teams transcript files saved.
- Atlassian artifacts saved or skipped.
- Combined run report path.
- Files updated.
- Accepted tasks and IDs.
- Issues and recommended follow-ups.
- Manual Slack/Teams follow-ups owned by the user.
- Safety confirmation that no source-system send or mutation actions were performed, including no Jira/Confluence mutations.
