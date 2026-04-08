---
description: Daily briefing and planning.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

### Daily Workflow

1. Activate `daily-synthesizer` with the `/day` trigger.
2. After the briefing is generated, trigger the `memory-consolidator` skill over the prior 24 hours of tasks, PRDs, and transcripts. Follow the output rules of the skill.

### Executive Focus Mode (Optional)

If the user types `/day --focus` or `/now`, generate a compact executive briefing instead of the full daily synthesis:

1. **Read** `5. Trackers/TASK_MASTER.md` and `5. Trackers/critical/boss-requests.md`.
1b. **Sync Calendar**: `python3 system/scripts/outlook_bridge.py --calendar 3` to populate the `## 📅 Schedule` section of the exec brief and update tasks in the tracker to `🗓️ Scheduled for [Date]` if they match upcoming events.
2. **Calculate** days until Friday Boss 1:1. Escalate Boss Ask priorities accordingly.
3. **Output** the following structure:
   - **🚨 Critical Focus (Top 3 P0s)**: Ranked by Due Date (`NOW` > `ASAP`) and Impact (`Boss Ask` > `Blocker`). Each item gets a 1-sentence context note.
   - **📋 Battlefield View (Next 10 Priorities)**: Compact table — `Priority | Reason | Due | ID | Task | Status | Owner`.
   - **🧠 Strategic Commentary**: Optional 1-line thought on velocity or bottleneck.
