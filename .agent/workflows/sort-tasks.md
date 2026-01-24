---
description: Sort the Task Master list by Priority (P0>P1>P2) and Due Date (NOW>ASAP>Date), moving completed items to the bottom.
---

# Sort Task Master

This workflow automatically sorts the `TASK_MASTER.md` file according to the following logic:
1.  **Separation**: Separates active tasks from completed tasks (marked with `🟢 Done`).
2.  **Sorting Active Tasks**:
    -   **Primary**: Priority (P0 > P1 > P2).
    -   **Secondary**: Due Date (NOW > ASAP > Upcoming Dates > TBD).
3.  **Completion**: Moves all completed tasks to a separate "Completed Tasks" table at the bottom of the file.

## Steps

1.  Run the sorting script.
    // turbo
    ```bash
    python3 system/sort_task_master.py
    ```
