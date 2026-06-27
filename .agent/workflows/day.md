---
description: Daily briefing and planning.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

### Daily Workflow

1. **Optional Communication Context Refresh**: If the user asks for updated/current communication context and provides bounded scopes such as `slack: #channel`, `teams: <chat>`, `outlook: <query>`, `calendar: next 7 days`, `transcripts: quill/granola/manual`, or a bounded combination, run `/beats-comms` first. Use only read-only MCP/connector operations, save communication transcripts through `chat-transcript-archive`, and include the new transcript/report paths in the briefing context. If no bounded scope is supplied, do not read source systems; continue from existing local transcripts or ask for the missing scope.
1b. **Workstream Triangulation**: Before briefing, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and boss requests. Group the briefing by workstream title, not task ID. Use the succinct title, bullet, and sub-bullet format from `task-manager`: latest outcome, completed outcome, open items, and recommended next 3.
2. Activate `daily-synthesizer` with the `/day` trigger.
3. After the briefing is generated, trigger the `memory-consolidator` skill over the prior 24 hours of tasks, PRDs, meeting transcripts, and chat transcripts. Follow the output rules of the skill.

### Executive Focus Mode (Optional)

If the user types `/day --focus` or `/now`, generate a compact executive briefing instead of the full daily synthesis:

1. **Read** `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md`.
1b. **Sync Calendar**: Prefer `/beats-comms calendar: next 3 days` with MS365 MCP/connector read-only access to populate the `## 📅 Schedule` section. Use `python3 system/scripts/outlook_bridge.py --calendar 3` only as a less-portable macOS AppleScript fallback. Update tasks in the tracker to `🗓️ Scheduled for [Date]` if they match upcoming events.
2. **Calculate** days until Friday Boss 1:1. Escalate Boss Ask priorities accordingly.
3. **Output** the following structure:
   - **🚨 Critical Workstreams**: Ranked by due date, boss impact, and blocker severity. Each item uses title, bullets, and sub-bullets.
   - **📋 Battlefield View**: Compact workstream sections, not an ID-led table:
     - `### [Workstream Title]`
     - `- Latest outcome: ...`
     - `  - Evidence: ...`
     - `- Completed: ...`
     - `  - Completed: date/source`
     - `- Open items: ...`
     - `  - Owner/action/date/source`
     - `- Recommended next 3:`
     - `  - Action`
   - **🧠 Strategic Commentary**: Optional 1-line thought on velocity or bottleneck.
