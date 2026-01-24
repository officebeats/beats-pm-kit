---
name: task-manager
description: Manage tasks and priorities.
triggers:
  - "/task"
  - "/todo"
  - "/triage"
  - "/plan"
  - "/organize"
version: 3.2.0 (Native Optimized)
author: Beats PM Brain
---

# Task Manager Skill

> **Role**: Execution Engine. You ruthlessly triumph over the `BRAIN_DUMP` and enforce the `TASK_MASTER` as the immutable ledger.

## 1. Native Interface

- **Inputs**: `/task`, `/triage`. `BRAIN_DUMP.md` (Inbox). `TASK_MASTER.md` (Ledger).
- **Tools**: `view_file`, `write_to_file`.

### Runtime Capability

- **Antigravity**: Parallel triage of bugs/features/tasks.
- **CLI**: Sequential triage with user confirmation when ambiguous.

## 2. Cognitive Protocol

### A. Parallel Triage (`#triage` → `/triage`)

1.  **Parse**: Split chaotic `BRAIN_DUMP.md`.
2.  **Parallel Routing**:
    - **Action**: In a SINGLE turn, use `multi_replace_file_content` to:
      - Append Bugs to `bugs-master.md`.
      - Append Tasks to `TASK_MASTER.md`.
      - Clear `BRAIN_DUMP.md`.
3.  **Zero State**: Ensure Inbox Zero is achieved in one move.

### B. Ledger Management (`/task`)

- **Structure**: `| Priority | Reason | Due | ID | Task | Description | Status | Owner |`
- **Operations**:
  - **Add**: Append new row to Top Table.
  - **Sort**: STRICT SORT by Priority (P0>P1>P2), THEN by Due Date (Closest first).
  - **Complete**: Move to "Completed Tasks" table at BOTTOM of file.
  - **Scale**: P0=Blocker, P1=Next. S=Hours, XL=Months.

### C. FAANG/BCG Rigor

- **Outcome Field**: Every task includes expected outcome/metric.
- **Owner + Date**: Required for P0/P1 items.
- **Dependency Tag**: `Depends on [Team/Task]` when applicable.

## 3. Output

- **Table**: Show exactly what moved Inbox -> Ledger.
- **Next Action**: Suggest top P0 item from `5. Trackers/TASK_MASTER.md`.

## 4. Fallback Patterns

- If `BRAIN_DUMP.md` not found, use context.
- Default to `5. Trackers` if routing fails.
