---
description: Plan the current and upcoming week.
source_tool: antigravity
source_path: .agents\workflows\week.md
imported_at: 2026-04-25T21:29:42.832Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /week - Weekly Tactical Plan

**Trigger**: User types `/week`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. The weekly plan should always anchor around this meeting. Boss Asks should be resolved *before* Friday.

## Steps

1.  **Parallel Context Mining**:
    - **Action**: In a SINGLE turn, read `5. Trackers/TASK_MASTER.md` AND `5. Trackers/critical/boss-requests.md`.
    - **Deadlines**: Scan for dates in the next 14 days.
    - **Calendar**: Ask user "Any key meetings this week?" (Interactive).

2.  **Synthesis (Staff PM)**:
    - Group items into **This Week** (Must Do) and **Next Week** (Tee Up).
    - Highlight **Risks**: Items due soon but not started.
    - Highlight **Boss Wins**: Items that satisfy boss requests.

3.  **Output**:
    - Create/Update `5. Trackers/WEEKLY_PLAN.md`.
    - Format:

      ```markdown
      # Weekly Plan: [Date Range]

      ## 🚨 Top 3 (The "Big Rocks")

      1. [Task A] (Due: Friday)
      2. [Boss Ask]
      3. [Strategy Item]

      ## 📅 This Week

      | Day | Priority | Context |
      | :-- | :------- | :------ |
      | Mon | ...      | ...     |

      ## 🔭 Next Week (Preview)

      - [ ] Prep for QBR
      - [ ] Launch v2
      ```
