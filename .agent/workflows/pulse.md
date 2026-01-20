---
description: Check system health and context (Time, Task Load, Stale State).
---

# /pulse - Context Awareness Check

**Trigger**: User types `/pulse` or system auto-runs on startup.

> **Value Prop**: A "Just-in-Time" reality check. It tells you if you're neglecting your dashboard, if you're overloaded, or if it's time for a specific ritual (like Weekly Review).

## Steps

// turbo

1.  **Execute Pulse Script**:
    - Run: `python system/scripts/pulse.py`
    - Logic:
      - Checks Time of Day (Morning, Lunch, EOD).
      - Counts P0/High Tasks in `TASK_MASTER.md`.
      - Checks age of `STATUS.md`.

## Output

- A single, formatted line with an emoji and a nudge.
- Example: `☕ GAP: Good morning. 3 P0 failures detected. Run /day?`
