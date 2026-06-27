---
description: Daily briefing and planning.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

### Daily Workflow

1. **Optional Communication Context Refresh**: If the user asks for updated/current communication context and provides bounded scopes such as `slack: #channel`, `teams: <chat>`, `outlook: <query>`, `calendar: next 7 days`, `transcripts: quill|granola|manual|packet`, or a bounded combination, run `/beats-comms` or `/transcript` first as appropriate. Use only read-only MCP/connector operations, save communication transcripts through `chat-transcript-archive`, and include the new transcript/report paths in the briefing context. If no bounded scope is supplied, do not read source systems; continue from existing local transcripts/trackers or ask for the missing scope.
2. Activate `daily-synthesizer` with the `/day` trigger.
3. Triangulate all fresh evidence against `5. Trackers/WORKSTREAMS.md`, `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present. Consolidate duplicate open items, latest outcomes, and completed checklist items under the matching workstream.
4. After the briefing is generated, trigger the `memory-consolidator` skill over the prior 24 hours of tasks, PRDs, meeting transcripts, and chat transcripts. Follow the output rules of the skill.

### Executive Focus Mode (Optional)

If the user types `/day --focus` or `/now`, generate a compact executive briefing instead of the full daily synthesis:

1. **Read** `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present.
1b. **Sync Calendar**: Prefer `/beats-comms calendar: next 3 days` with MS365 MCP/connector read-only access to populate the `## 📅 Schedule` section. Use `python3 system/scripts/outlook_bridge.py --calendar 3` only as a less-portable macOS AppleScript fallback. Update tasks in the tracker to `🗓️ Scheduled for [Date]` if they match upcoming events.
2. **Calculate** days until Friday Boss 1:1. Escalate Boss Ask priorities accordingly.
3. **Output** the following structure:
   - **Critical Workstreams**: 3-5 sections using this shape:

     ```markdown
     ### Workstream Title
     - Latest outcome: [result, decision, or current state]
       - Evidence: [source/date/path]
     - Completed: [done item or "None newly confirmed"]
       - Completed: [date/source]
     - Open items: [count or short list]
       - [Owner] - [action] by [date/gate], from [source]
     - Recommended next 3:
       - [Action 1]
       - [Action 2]
       - [Action 3]
     ```

   - **Today**: The smallest set of actions that moves those workstreams forward.
   - **Questions / Gaps**: Source gaps, stale items, and possibly-complete items needing confirmation.
   - **Strategic Commentary**: Optional 1-line thought on velocity or bottleneck.

Workstream titles must be plain English, 9 words or fewer, and never include internal task/card/source IDs.
