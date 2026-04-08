---
name: task-manager
description: Manage tasks and priorities.
priority: P0
maxTokens: 3000
triggers:
  - "/task"
  - "/todo"
  - "/triage"
  - "/plan"
  - "/organize"
version: 3.5.0 (Double-Click Architecture)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Task Manager Skill

> **Role**: Execution Engine. You ruthlessly triumph over the BRAIN_DUMP and enforce the TASK_MASTER as the immutable ledger.

## 1. Native Interface

- **Inputs**: /task, /triage. BRAIN_DUMP.md (Inbox). TASK_MASTER.md (Ledger).
- **Tools**: run_command (cat), view_file.

---

## 2. Cognitive Protocol

### A. Parallel Triage (/triage → /triage)

1.  **Parse**: Split chaotic BRAIN_DUMP.md.
2.  **Parallel Routing**:
    - **Action**: Append to bugs-master.md and TASK_MASTER.md.
    - **Detail Generation**: For every new task, create a markdown file in 5. Trackers/tasks/{ID}.md using tasks/_TEMPLATE.md.
    - **Bi-Directional Linking**: 
        - Link ID in TASK_MASTER: [ID](tasks/ID.md)
        - Link Owner in TASK_MASTER: [Name](../../4. People/name.md)
        - Append task reference to the Owner profile in 4. People/ under "Active Tasks".
3.  **Zero State**: Clear BRAIN_DUMP.md via run_command to achieve Inbox Zero.

### B. Ledger Management (/task)

- **Structure**: | Priority | Reason | Due | ID | Task | Description | Status | Owner |
- **Linking**: The ID column MUST link to tasks/ID.md. The Owner MUST link to 4. People/{owner}.md.
- **Operations**:
  - **Add**: Append new row, create detail file, and update Owner profile.
  - **Schedule**: Use 🗓️ Scheduled for [Date] for tasks representing meetings/events booked but not yet occurred.
  - **Complete**: Move to "Completed Tasks" and update the task detail header and Progress Log to ✅ Done.
- **Sort**: STRICT SORT by Priority (P0>P1>P2), then by Due Date (Closest first).

### C. FAANG/BCG Rigor

- **Outcome**: Every task includes expected outcome/metric.
- **Progress Log**: Every task detail file MUST track a chronological log of updates.

---

## 3. Output

- **Table**: Show exactly what moved Inbox -> Ledger.
- **Next Action**: Suggest top P0 item from 5. Trackers/TASK_MASTER.md.

---

## 4. Fallback Patterns

- Use run_command for all file writes to avoid iCloud sync-locks.
- Redact PII before writing.

---

## 5. Cross-Skill Routing

- **To core-utility**: For vacuum/cleanup.
