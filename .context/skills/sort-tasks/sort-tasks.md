---
description: Sort the Task Master list by Priority (P0>P1>P2) and Due Date (NOW>ASAP>Date), moving completed items to the bottom.
source_tool: antigravity
source_path: .agents\workflows\archive\sort-tasks.md
imported_at: 2026-04-25T21:29:42.808Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



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
