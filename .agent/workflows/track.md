---
description: Manage the battlefield. Tasks, Bugs, and Boss Asks.
---

# ⚔️ Task & Execution Playbook

This workflow guides the **Staff PM** to manage daily execution.

## Steps

1.  **Parallel State Check**:
    - **Action**: In a SINGLE turn, read `5. Trackers/TASK_MASTER.md`, `5. Trackers/critical/boss-requests.md`, and `5. Trackers/bugs/bugs-master.md`.

2.  **Turbo Triage**:
    - **Input**: User Brain Dump.
    - **Action**: Parse input and route to the correct file using `multi_replace_file_content` to update all necessary trackers in PARALLEL.
    - **Priority**: Assign P0 (Today), P1 (This Week), P2 (Backlog).

3.  **FAANG/BCG Quality Gate**:
    - **Owner + Date** required for P0/P1 tasks.
    - **Outcome Metric** required for P0/P1 tasks.
    - **Dependency** noted if blocked by another team.

4.  **Boss Ask Protocol**:
    - If the user mentions a "Boss" or "Leadership" request, IMMEDIATELY flag as `[BOSS]` in `5. Trackers/critical/boss-requests.md`.

5.  **Output**:
    - Display the updated "Today's List" (Table View).
