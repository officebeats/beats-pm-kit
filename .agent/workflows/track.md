---
description: Manage the battlefield. Tasks, Bugs, and Boss Asks.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# ⚔️ Task & Execution Playbook

This workflow guides the **Staff PM** to manage daily execution.

## Steps

0a. **PM Decision Router Preflight**:
    - **Action**: Load `.agent/skills/pm-decision-router/SKILL.md`.
    - **Classify**: For any provided brain dump, note, screenshot OCR, or transcript snippet, run `python3 system/scripts/pm_decision_router.py --text "<input>"`.
    - **Use Result**: Existing task updates must update the matched task before creating new work. `scope_challenge` results must go through the Priority Gate and return explicit owner/scope questions instead of becoming active tasks.
    - **Quality Bar**: For accepted `task_update` or `new_task` work, carry workstream, outcome metric, owner, due date, scope boundary, evidence strength, dependency, and next decision gate into the workstream and task detail file.

0.  **Optional Trello Preflight**:
    - **Action**: If Trello is enabled locally, run `python3 system/scripts/trello_bridge.py intake --apply` before reading trackers.
    - **Context**: Review `system/inbox/trello/reports/latest-intake.md` and any packet files in `system/inbox/trello/incoming/` so Trello-originated task candidates can be triaged formally instead of silently accepted.
    - **Output**: Include the configured Trello board URL in the user-facing summary when available.

1.  **Parallel State Check**:
    - **Action**: In a SINGLE turn, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/critical/boss-requests.md`, and `5. Trackers/bugs/bugs-master.md`.

2.  **Turbo Triage**:
    - **Input**: User Brain Dump.
    - **Action**: Parse input and route to the correct file using `multi_replace_file_content` to update all necessary trackers in PARALLEL.
    - **Lane**: Place work into `Today`, `Next`, `Later`, `Follow Up`, or `Triage`.
    - **Workstream rule**: Map every task/update/completion to a workstream title of 9 words or fewer. Do not show internal IDs in the human-facing label.
    - **Title/body rule**: Keep the task/card/workstream title to 9 words or fewer; put the longer explanation in the body as a 15-word-max summary plus up to 3 short bullets.
    - **Completion rule**: If evidence shows an item is done, check it off with completion date/source in the workstream, task detail, boss tracker if relevant, and Trello checklist.

3.  **FAANG/BCG Quality Gate**:
    - **Owner + Date** required for `Today` and `Next` tasks.
    - **Outcome Metric** required for `Today` and `Next` tasks.
    - **Dependency** noted if blocked by another team.

4.  **Boss Ask Protocol**:
    - If the user mentions a "Boss" or "Leadership" request, IMMEDIATELY flag as `[BOSS]` in `5. Trackers/critical/boss-requests.md`.

5.  **Output**:
    - Display the updated workstream list with latest outcomes, completed outcomes, open items, and recommended next 3.
    - Use succinct title, bullet, and sub-bullet sections. Do not lead with internal IDs.
