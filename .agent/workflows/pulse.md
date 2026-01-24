---
description: Check system health and context (Time, Task Load, Stale State).
---

# /pulse - Context Awareness Check

**Trigger**: User types `/pulse` or system auto-runs on startup.

> **Value Prop**: A "Just-in-Time" reality check. It tells you if you're neglecting your dashboard, if you're overloaded, or if it's time for a specific ritual (like Weekly Review).

## Steps

// turbo

1.  **Native Pulse Check**:
    - **Time Check**: Get local time.
    - **Task Scan**: Parallel read `TASK_MASTER.md` and `boss-requests.md`.
    - **Logic**: Count "P0" tags and "Overdue" dates.
    - **Stale Check**: Check last modified date of `STATUS.md`.

## Output

- A single, formatted line with an emoji and a nudge.
- Example: `☕ GAP: Good morning. 3 P0 failures detected. Run /day?`
