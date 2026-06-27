---
description: Manage the battlefield. Tasks, Bugs, and Boss Asks.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# ⚔️ Task & Execution Playbook

This workflow guides the **Staff PM** to manage daily execution.

## Steps

0fast. **Fast Raw-Evidence Intake**:
    - **Use when**: The user provides a single pasted chat/email/thread, especially prefaced with "for task manager", and does not ask for full triage, Trello sync, `/day`, `/week`, or broad source refresh.
    - **Action**: Run `python3 system/scripts/task_intake_fast.py --text "<raw pasted evidence>" --source "<source label>"`.
    - **Contract**: The script must save a raw source note plus summary, then update a matched task or create an `INBOX-###` candidate task even when confidence is low.
    - **Display rule**: Use succinct descriptive phrases for user-facing labels; keep IDs such as `PLAN-014` or `INBOX-001` as internal anchors only.
    - **Workstream rule**: Map the evidence to an existing workstream title when possible. If none exists, propose a plain-English workstream title of 9 words or fewer and keep IDs out of the visible title.
    - **Latency rule**: Do not read broad tracker context before this script. Do not run `task_master_triage.py` unless a full health pass is explicitly requested.
    - **Escalation**: If the script returns a candidate task and the user wants refinement, continue with the full workflow below.

0a. **PM Decision Router Preflight**:
    - **Action**: Load `.agent/skills/pm-decision-router/SKILL.md`.
    - **Classify**: For any provided brain dump, note, screenshot OCR, or transcript snippet, run `python3 system/scripts/pm_decision_router.py --text "<input>"`.
    - **Use Result**: Existing task updates must update the matched task before creating new work. `scope_challenge` results must go through the Priority Gate and return explicit owner/scope questions instead of becoming active tasks.
    - **Quality Bar**: For accepted `task_update` or `new_task` work, carry outcome metric, owner, due date, scope boundary, evidence strength, dependency, and next decision gate into the task detail file.

0.  **Optional Trello Preflight**:
    - **Action**: If Trello is enabled locally, run `python3 system/scripts/trello_bridge.py intake --apply` before reading trackers.
    - **Context**: Review `system/inbox/trello/reports/latest-intake.md` and any packet files in `system/inbox/trello/incoming/` so Trello-originated task candidates can be triaged formally instead of silently accepted.
    - **Output**: Include the configured Trello board URL in the user-facing summary when available.

1.  **Parallel State Check**:
    - **Action**: In a SINGLE turn, read `5. Trackers/WORKSTREAMS.md`, relevant `5. Trackers/workstreams/` files, `5. Trackers/TASK_MASTER.md`, `5. Trackers/critical/boss-requests.md`, and `5. Trackers/bugs/bugs-master.md` when present.

2.  **Turbo Triage**:
    - **Input**: User Brain Dump.
    - **Action**: Parse input and route to the correct file using `multi_replace_file_content` to update all necessary trackers in PARALLEL.
    - **Lane**: Place work into `Today`, `Next`, `Later`, `Follow Up`, or `Triage`.
    - **Title/body rule**: Keep the workstream/card title as a succinct descriptive phrase of 9 words or fewer; put the longer explanation in the body as a 15-word-max summary plus up to 3 short bullets.
    - **Completion rule**: When evidence confirms an item is done, check it off locally, record completion date/source, and preserve it in the workstream/task history. Do not silently close uncertain items; surface them as confirmation questions.
    - **Triangulation rule**: Consolidate duplicate Outlook, Teams, Slack, Calendar, manual transcript, Quill, Granola, and local packet signals under the same workstream before creating a new visible card or section.

3.  **FAANG/BCG Quality Gate**:
    - **Owner + Date** required for `Today` and `Next` tasks.
    - **Outcome Metric** required for `Today` and `Next` tasks.
    - **Dependency** noted if blocked by another team.

4.  **Boss Ask Protocol**:
    - If the user mentions a "Boss" or "Leadership" request, IMMEDIATELY flag as `[BOSS]` in `5. Trackers/critical/boss-requests.md`.

5.  **Output**:
    - Display the updated workstream list first:

      ```markdown
      ### Workstream Title
      - Latest outcome: [result, decision, or current state]
        - Evidence: [source/date/path]
      - Completed: [done item or "None newly confirmed"]
        - Completed: [date/source]
      - Open items: [count or short list]
        - [Owner] - [action] by [date/gate], from [source]
      - Recommended next 3:
        - [Action 1]
        - [Action 2]
        - [Action 3]
      ```

    - Then show gate results, files updated, accepted internal task IDs, and unresolved questions.
