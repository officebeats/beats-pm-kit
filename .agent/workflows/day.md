---
description: Daily briefing and planning.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

### Daily Workflow

1. **Critical Commitment Preflight**: Run `python3 system/scripts/critical_commitment_refresh.py plan --mode day --json` and `python3 system/scripts/critical_commitment_refresh.py rank --mode day --json` before synthesis. If the plan reports `should_pause_for_user: true`, stop and tell the user which configured or expected integration failed, why it matters, the recommended fix, and the safe choices: reconnect/configure, paste or export for this run, skip once, or disable that source from defaults.
2. **Default Communication Context Refresh**: Use the preflight plan to run manifest-backed bounded Slack, Outlook, Calendar, Teams, transcript, Quill, Granola, Obsidian, Atlassian, and agent-memory reads before synthesis. Use parallel agents for independent read-only source collection when available. If a platform lacks a manifest/config scope, prompt instead of broad-scanning. If a source read fails, prompt the user before proceeding degraded.
3. **Read-Only Safety**: Third-party systems are read-only by default. Never send, draft, reply, react, schedule, create, assign, transition, comment, upload, patch, delete, move, or mutate Slack, Teams, Outlook, Calendar, Jira, Confluence, Obsidian, Quill, Granola, or graph-memory state unless the user explicitly confirms that exact mutation in the current turn. Local tracker/file updates are allowed.
4. Activate `daily-synthesizer` with the `/day` trigger.
5. Triangulate all fresh evidence against `5. Trackers/WORKSTREAMS.md`, `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present. Consolidate duplicate open items, latest outcomes, and completed checklist items under the matching workstream.
6. After the briefing is generated, trigger the `memory-consolidator` skill over the prior 24 hours of tasks, PRDs, meeting transcripts, and chat transcripts. Follow the output rules of the skill.

### Executive Focus Mode (Optional)

If the user types `/day --focus` or `/now`, generate a compact executive briefing instead of the full daily synthesis:

1. **Read** `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present.
2. **Use Ranked Commitments**: Lead with items ranked by `critical_commitment_refresh.py rank --mode day`; leadership callouts, boss-of-boss asks, external partner/customer commitments, and dated end-user commitments outrank ordinary stale work.
3. **Sync Calendar**: Use the manifest-backed Calendar scope from the critical preflight to populate the schedule section. Update tasks in the tracker to `🗓️ Scheduled for [Date]` if they match upcoming events.
4. **Calculate** days until Friday Boss 1:1. Escalate Boss Ask priorities accordingly.
5. **Output** the following structure:
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
