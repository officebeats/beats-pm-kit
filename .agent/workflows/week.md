---
description: Plan the current and upcoming week.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /week - Weekly Tactical Plan

**Trigger**: User types `/week`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. The weekly plan should always anchor around this meeting. Boss Asks should be resolved *before* Friday.

## Steps

1.  **Critical Commitment Preflight**:
    - **Action**: Run `python3 system/scripts/critical_commitment_refresh.py plan --mode week --json` and `python3 system/scripts/critical_commitment_refresh.py rank --mode week --json` before weekly synthesis.
    - **Prompt-on-breakage**: If the plan reports `should_pause_for_user: true`, stop and tell the user which configured or expected integration failed, why it matters, the recommended fix, and the safe choices: reconnect/configure, paste or export for this run, skip once, or disable that source from defaults.
    - **Priority**: Use the ranked commitments so direct manager, boss-of-boss, executive, external partner/customer, and dated end-user commitments outrank ordinary stale work.

2.  **Default Communication Context Refresh**:
    - **Action**: Use manifest-backed bounded Slack, Outlook, Calendar, Teams, transcript, Quill, Granola, Obsidian, Atlassian, and agent-memory reads before synthesis. Use parallel agents for independent read-only source collection when available.
    - **Safety**: Third-party systems are read-only by default. Never send, draft, reply, react, schedule, create, assign, transition, comment, upload, patch, delete, move, or mutate Slack, Teams, Outlook, Calendar, Jira, Confluence, Obsidian, Quill, Granola, or graph-memory state unless the user explicitly confirms that exact mutation in the current turn.
    - **Scope**: If a platform lacks a manifest/config scope, prompt instead of broad-scanning. If a configured source read fails, prompt before proceeding degraded.
    - **Context Handoff**: Include newly written transcript and run report paths in the weekly context mining step.

3.  **Parallel Context Mining**:
    - **Action**: In a SINGLE turn, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present.
    - **Deadlines**: Scan for dates in the next 14 days.
    - **Calendar**: Use the preflight Calendar plan first; ask the user about key missing meetings only when Calendar is unavailable or incomplete.

4.  **Synthesis (Staff PM)**:
    - Group by workstream first; do not lead with Task Master IDs.
    - Workstream titles must be plain English, 9 words or fewer, and never include internal task/card/source IDs.
    - Highlight **Boss Outcomes**: succinct action-item style outcomes that satisfy leadership requests.
    - Highlight **Completed Outcomes**: completed checklist items and decisions, with completion date and source.
    - Highlight **Open Items**: current asks from Outlook, Teams, Slack, Calendar, manual transcripts, Quill, Granola, and local transcript packets when bounded evidence exists.
    - Highlight **Recommended Next 3** for each active workstream.
    - Highlight **Risks**: items due soon but not started or blocked.

5.  **Output**:
    - Create/Update `5. Trackers/WEEKLY_PLAN.md`.
    - Format:

      ```markdown
      # Weekly Plan: [Date Range]

      ## Outcomes

      - [Outcome or committed result] by [date/gate]
        - Evidence: [source/date/path]
      - [Outcome or committed result] by [date/gate]
        - Evidence: [source/date/path]

      ## Completed Outcomes

      - [Completed item]
        - Completed: [date/source]

      ## Workstreams

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

      ## Source Gaps / Questions

      - [Connector gap, stale workstream, or possibly-complete item needing confirmation]
      ```
