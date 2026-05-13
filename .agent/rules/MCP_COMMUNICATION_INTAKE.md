# MCP Communication Intake

This kit supports read-only communication intake through runtime-provided MCP or connector capabilities while keeping `.agent/` as the workflow source of truth.

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

## Workflow Use

- `/beats-comms` is the canonical bounded intake command for `slack:`, `teams:`, `outlook:`, and `calendar:` scopes.
- Platform scopes must be explicit. Do not broad-scan workspaces, all chats, all channels, all mail, all DMs, or calendar history.
- Slack scopes that may return many results must be pre-chunked with `system/scripts/chat_intake_state.py chunks` before the first Slack query. This includes mention/DM intake, `to:me`, multi-day channel history, and explicit windows longer than 5 calendar days.
- Prefer MCP/connector reads first. Use bridge scripts only when MCP/connector access is unavailable and the workflow labels the fallback limitations in the run report.
