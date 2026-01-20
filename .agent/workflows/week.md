---
description: Plan the current and upcoming week.
---

# /week - Weekly Tactical Plan

**Trigger**: User types `/week`.

## Steps

1.  **Context Mining**:
    - **Deadlines**: Scan `5. Trackers/TASK_MASTER.md` for dates in the next 14 days.
    - **Urgency**: Scan `5. Trackers/critical/boss-requests.md` for "ASAP" or "P0".
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
