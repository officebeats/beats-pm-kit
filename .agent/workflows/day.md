---
title: Daily Product Briefing
description: Daily briefing and planning.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.

### Daily Workflow

1. **Precomputed Skeleton**: If `.beats/day_skeleton.md` exists and its first-line `<!-- generated: ... -->` timestamp is less than 20 hours old, use it as the precomputed base for the active task tables, overdue/due-today rollup, workstream snapshot, and open boss asks; spend model effort only on synthesis and prioritization on top of it. Otherwise compute those sections live (or regenerate with `python3 -m system.scripts.day_skeleton`).
2. **Critical Commitment Preflight**: Run `python3 system/scripts/critical_commitment_refresh.py plan --mode day --json` and `python3 system/scripts/critical_commitment_refresh.py rank --mode day --json` before synthesis. If the plan reports `should_pause_for_user: true`, stop and tell the user which configured or expected integration failed, why it matters, the recommended fix, and the safe choices: reconnect/configure, paste or export for this run, skip once, or disable that source from defaults.
3. **Default Communication Context Refresh**: Use the preflight plan to run manifest-backed named read-only source windows for Slack, Outlook, Calendar, Teams, transcript, Quill, Granola, Obsidian, Atlassian, and agent-memory reads before synthesis. Backward windows default to the last 5 business days and may shorten only from a successful source/command checkpoint for the same source/window; calendar also includes forward lookahead for upcoming active-workstream gates. Use parallel agents for independent read-only source collection when available. If a platform lacks a manifest/config window, prompt instead of broad-scanning. If a source read fails, prompt the user before proceeding degraded.
4. **Read-Only Safety**: Third-party systems are read-only by default. Never send, draft, reply, react, schedule, create, assign, transition, comment, upload, patch, delete, move, or mutate Slack, Teams, Outlook, Calendar, Jira, Confluence, Obsidian, Quill, Granola, or graph-memory state unless the user explicitly confirms that exact mutation in the current turn. Local tracker/file updates are allowed.
5. Activate `daily-synthesizer` with the `/day` trigger.
6. Triangulate all fresh evidence against `5. Trackers/WORKSTREAMS.md`, `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present. Consolidate duplicate open items, latest outcomes, and completed checklist items under the matching workstream.
7. Render user-facing task/workstream descriptions from display provenance: use the task/workstream title, started date/source, and latest progress source. Keep Task Master IDs, Jira IDs, Trello IDs, and source IDs only in local links, metadata, or an `Agent refs` line.
8. After the briefing is generated, trigger the `memory-consolidator` skill over the prior 24 hours of tasks, PRDs, meeting transcripts, and chat transcripts. Follow the output rules of the skill.

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
       - Evidence: [task/workstream title; started from initial source on date; latest progress from latest source on date]
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
