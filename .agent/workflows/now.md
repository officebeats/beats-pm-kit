---
description: Generate a Focused Executive Briefing on Immediate Priorities (P0) and active backlogs.
---

# /now - Executive Focus Protocol

This workflow generates a high-signal briefing on the *immediate* state of play. It forces focus on P0 criticals and provides a full battlefield view.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. All "Boss Ask" items should be weighted against this weekly deadline. Today's date determines urgency.

## 1. Context Acquisition

1.  **Read Ledger**: Read `5. Trackers/TASK_MASTER.md` to get the latest task state.
2.  **Calculate Days to Boss 1:1**: Determine how many days remain until Friday. Use this to escalate "Boss Ask" priorities accordingly.

## 2. Synthesis & Output

**You must generate a report with the following structure:**

### 🚨 Critical Focus (Top 3 P0s)

*Analyze the P0 list and select the absolute top 3 items based on Due Date (`NOW` > `ASAP`) and Impact (`Boss Ask` > `Blocker`).*

1.  **[Task Name]** (Due: `[Date]`)
    *   *Context*: [1-sentence explanation of why this is #1. Is it a boss ask? A blocker? Overdue?]
2.  **[Task Name]** (Due: `[Date]`)
    *   *Context*: [Why is this #2?]
3.  **[Task Name]** (Due: `[Date]`)
    *   *Context*: [Why is this #3?]

### 📋 Battlefield View (Next 10 Priorities)

*Present a clean Markdown table of the **next 10** highest priority active tasks (excluding the Top 3 already listed above).*

| Priority | Reason | Due | ID | Task | Status | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ... | ... | ... | ... | ... | ... | ... |

*(Note: Omit the 'Description' column in this view to keep it compact).*

---

### 🧠 Strategic Commentary
*(Optional: Add a 1-line thought on the overall velocity or bottleneck if apparent).*
