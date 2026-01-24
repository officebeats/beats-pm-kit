---
description: Generate a prioritized sprint backlog for dev team planning.
---

# /sprint - Dev Team Alignment

**Trigger**: Planning meeting with engineering team.

## Steps

1.  **Parallel Context Gathering**:
    - **Action**: In a SINGLE turn, read `5. Trackers/TASK_MASTER.md`, `5. Trackers/bugs/bugs-master.md`, and `5. Trackers/critical/boss-requests.md`.
    - **Filter**: Isolate tasks tagged `[Eng]` or with engineering owners.

2.  **Prioritization**:
    - Group by Priority: P0 (Blockers) → P1 (Sprint) → P2 (Backlog).
    - Flag any items where `Due Date < 7 days` and `Status != Done`.

3.  **Capacity Check** (Optional):
    - If user provides sprint duration (e.g., "2 weeks"), estimate if backlog fits.
    - Highlight overcommitment risk.

4.  **Output**:
    - Generate a "Sprint Proposal" table:

      ```markdown
      # 🏃 Sprint Proposal: [Date Range]

      ## P0 - Must Ship (Blockers)

      | Task | Product | Owner | Due |
      | :--- | :------ | :---- | :-- |

      ## P1 - Sprint Goals

      | Task | Product | Owner | Estimate |
      | :--- | :------ | :---- | :------- |

      ## P2 - Stretch / Backlog

      | Task | Product | Owner | Notes |
      | :--- | :------ | :---- | :---- |

      ## 🐛 Bugs

      | Bug | Severity | Product | Status |
      | :-- | :------- | :------ | :----- |
      ```

5.  **Follow-Up**:
    - Suggest: "Run `/meet` after the planning session to capture decisions."
