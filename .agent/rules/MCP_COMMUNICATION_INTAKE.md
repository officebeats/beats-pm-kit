# MCP Communication Intake

This kit supports read-only communication intake through runtime-provided MCP or connector capabilities while keeping `.agent/` as the workflow source of truth.

In user-facing language, a source window is a named read-only source plus an effective start/end window. It is not permission to broad-scan a workspace, mailbox, calendar, or tenant.

## Runtime Capability Table

| Capability | Antigravity | Codex | Claude Code | Fallback |
| --- | --- | --- | --- | --- |
| Slack read/search/thread/user/canvas | Runtime Slack MCP or connector, read-only only | Slack app connector or MCP tools, read-only only | User-scope `slack` MCP | User-provided export or pasted text |
| Teams chat/channel/thread/transcript read | Runtime MS365 MCP or connector, read-only only | Teams/MS365 app connector or MCP tools, read-only only | User-scope `ms365` MCP | User-provided export or pasted text; `teams_bridge.py` only with explicit acceptance |
| Outlook mail read/search | Runtime MS365 MCP or connector, read-only only | Outlook/MS365 app connector or MCP tools, read-only only | User-scope `ms365` MCP | `outlook_bridge.py` AppleScript fallback on macOS |
| Calendar read/schedule view | Runtime MS365 MCP or connector, read-only only | Outlook/MS365 app connector or MCP tools, read-only only | User-scope `ms365` MCP | `outlook_bridge.py --calendar` AppleScript fallback on macOS |

## Privacy Contract

- Commit only generic templates and runtime-neutral workflow rules.
- Keep tenant IDs, client IDs, tool allowlists, OAuth tokens, source URLs for private setup docs, copied messages, transcripts, and run reports in ignored local or user-scope files.
- Use `system/config/mcp.template.json` as the tracked placeholder. Copy private values only into ignored `system/config/mcp.local*.json` files or user-scope runtime config.
- Before reporting implementation complete, verify local MCP config and communication artifacts with `git check-ignore -v`.

## Source-System Safety

- All communication systems are intake-only by default.
- Never send, schedule, draft, reply, forward, react, edit, delete, pin, upload, create canvases/files, create chats/channels, create Planner tasks, or mutate mail/chat/calendar state unless the active workflow and the user's current-turn request explicitly allow the exact action.
- Email is stricter: never create, send, forward, or reply to email unless the user explicitly asks for that specific message in the current turn. Prefer draft text in chat or local artifacts.
- Never create or modify calendar events or meeting invites.
- Preserve unread state. Do not use tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Obsidian, Quill, Granola, Jira, Confluence, graph memory, and agent memory are read/search/open context sources by default. Never write, patch, move, delete, comment, transition, upload, or mutate those systems unless the user explicitly confirms that exact mutation in the current turn.
- Configured or expected integration failures must be visible to the user. Prompt with the failed source, risk if skipped, recommended fix, and safe choices before proceeding degraded.

## Workflow Use

- `/beats-comms` is the canonical named read-only intake command for `slack:`, `teams:`, `outlook:`, and `calendar:` source windows.
- Platform source windows must be explicit. Do not broad-scan workspaces, all chats, all channels, all mail, all DMs, or calendar history.
- Recurring `/day`, `/week`, and `/boss` runs may use manifest-backed scopes from `system/scripts/critical_commitment_refresh.py plan` as explicit named read-only source windows.
- Backward source windows default to the last 5 business days and may shorten only when `3. Meetings/chat-transcripts/_manifest.json` or `3. Meetings/reports/command-runs/_manifest.json` has a successful checkpoint for the same source/window. Calendar includes the last 5 business days of changes plus forward lookahead for upcoming active-workstream gates.
- Slack scopes that may return many results must be pre-chunked with `system/scripts/chat_intake_state.py chunks` before the first Slack query. This includes mention/DM intake, `to:me`, multi-day channel history, and explicit windows longer than 5 calendar days.
- Prefer MCP/connector reads first. Use bridge scripts only when MCP/connector access is unavailable and the workflow labels the fallback limitations in the run report.
- TWG is not a `/beats-comms` source and must not widen a named communication or referenced-only Atlassian window. Its optional read-only use is governed by `.agent/rules/TWG_READ_ONLY.md`.
