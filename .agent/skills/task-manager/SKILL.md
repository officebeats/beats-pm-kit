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

## 2. Cognitive Protocol

### A. Triage (`#triage`)

1.  **Parse**: Split chaotic `BRAIN_DUMP.md`.
2.  **Route**:
    - **Bug** -> `bug-chaser`.
    - **Feature** -> `prd-author`.
    - **Idea** -> `strategy-synth`.
    - **Task** -> Move to Ledger.
3.  **Clean**: Ensure `BRAIN_DUMP.md` is empty -> "Inbox Zero".

### B. Ledger Management (`/task`)

- **Structure**: `| Priority (P0-P3) | Task | Product | Status (⏳/🚧/✅) |`
- **Operations**:
  - **Add**: Append new row.
  - **Complete**: Mark ✅.
  - **Scale**: P0=Blocker, P1=Next. S=Hours, XL=Months.

## 3. Output

- **Table**: Show exactly what moved Inbox -> Ledger.
- **Next Action**: Suggest top P0 item.
