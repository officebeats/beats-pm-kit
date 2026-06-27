---
description: Plan the current and upcoming week.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /week - Weekly Tactical Plan

**Trigger**: User types `/week`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. The weekly plan should always anchor around this meeting. Boss Asks should be resolved *before* Friday.

## Steps

1.  **Optional Communication Context Refresh**:
    - **Action**: If the user asks for updated/current communication context and provides bounded scopes such as `slack: #channel`, `teams: <chat>`, `outlook: <query>`, `calendar: next 14 days`, `transcripts: quill/granola/manual`, or a bounded combination, run `/beats-comms` before weekly synthesis.
    - **Safety**: Use only read-only MCP/connector operations, save communication transcripts through `chat-transcript-archive`, and preserve unread state. If no bounded scope is supplied, do not read source systems; continue from existing local transcripts or ask for the missing scope.
    - **Context Handoff**: Include newly written transcript and run report paths in the weekly context mining step.

2.  **Parallel Context Mining**:
    - **Action**: In a SINGLE turn, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, and `5. Trackers/critical/boss-requests.md`.
    - **Deadlines**: Scan for dates in the next 14 days.
    - **Calendar**: Ask user "Any key meetings this week?" (Interactive).

3.  **Synthesis (Staff PM)**:
    - Group items into **This Week** (Must Do) and **Next Week** (Tee Up).
    - Highlight **Risks**: Items due soon but not started.
    - Highlight **Boss Outcomes**: dated commitments, readiness checks, and owner actions that satisfy boss requests.
    - Highlight **Completed Outcomes**: what got checked off this week and the evidence/source date.
    - Keep the plan workstream-first; task IDs belong only in hidden/internal references.
    - Use succinct title, bullet, and sub-bullet sections for every workstream instead of ID-led tables.
    - For Manager-facing weekly email language, do not use "outcomes" as a synonym for accomplishments. Use the format:
      - `[Date]: [deliverable/checkpoint] will be ready/confirmed`
      - `Readiness checks: [owner] will [action] by [date]`

4.  **Output**:
    - Create/Update `5. Trackers/WEEKLY_PLAN.md`.
    - Format:

      ```markdown
      # Weekly Plan: [Date Range]

      ## 🚨 Top 3 (The "Big Rocks")

      1. [Task A] (Due: Friday)
      2. [Boss Ask]
      3. [Strategy Item]

      ## Outcomes

      [Date]: [Deliverable/checkpoint] will be ready
      [Date]: [Decision/checkpoint] will be confirmed

      ## Completed Outcomes

      [Date completed]: [Completed item] - [source/evidence]

      ## Readiness Checks

      - [Owner] will [specific action] by [date]
      - [Owner] will [specific action] by [date]

      ## 📅 This Week

      ### [Workstream Title]

      - Latest outcome: [dated outcome or current commitment]
        - Evidence: [source/date]
      - Completed: [completed item or "None newly confirmed"]
        - Completed: [date/source]
      - Open items:
        - [Owner/action/date/source]
      - Recommended next 3:
        - [Action 1]
        - [Action 2]
        - [Action 3]

      ## 🔭 Next Week (Preview)

      - [ ] Prep for QBR
      - [ ] Launch v2
      ```
