---
description: Plan the current and upcoming week.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /week - Weekly Tactical Plan

**Trigger**: User types `/week`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. The weekly plan should always anchor around this meeting. Boss Asks should be resolved *before* Friday.

## Steps

1.  **Optional Communication Context Refresh**:
    - **Action**: If the user asks for updated/current communication context and provides bounded scopes such as `slack: #channel`, `teams: <chat>`, `outlook: <query>`, `calendar: next 14 days`, `transcripts: quill|granola|manual|packet`, or a bounded combination, run `/beats-comms` or `/transcript` before weekly synthesis as appropriate.
    - **Safety**: Use only read-only MCP/connector operations, save communication transcripts through `chat-transcript-archive`, and preserve unread state. If no bounded scope is supplied, do not read source systems; continue from existing local transcripts or ask for the missing scope.
    - **Context Handoff**: Include newly written transcript and run report paths in the weekly context mining step.

2.  **Parallel Context Mining**:
    - **Action**: In a SINGLE turn, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md` when present.
    - **Deadlines**: Scan for dates in the next 14 days.
    - **Calendar**: Ask user "Any key meetings this week?" (Interactive).

3.  **Synthesis (Staff PM)**:
    - Group by workstream first; do not lead with Task Master IDs.
    - Workstream titles must be plain English, 9 words or fewer, and never include internal task/card/source IDs.
    - Highlight **Boss Outcomes**: succinct action-item style outcomes that satisfy leadership requests.
    - Highlight **Completed Outcomes**: completed checklist items and decisions, with completion date and source.
    - Highlight **Open Items**: current asks from Outlook, Teams, Slack, Calendar, manual transcripts, Quill, Granola, and local transcript packets when bounded evidence exists.
    - Highlight **Recommended Next 3** for each active workstream.
    - Highlight **Risks**: items due soon but not started or blocked.

4.  **Output**:
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
