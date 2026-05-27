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
  - "/paste"
  - "/transcript"
  - "screenshot"
  - "transcript"
version: 4.0.0 (Priority Gate)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Task Manager Skill

> **Role**: Execution Engine. You ruthlessly triumph over the BRAIN_DUMP and enforce the TASK_MASTER as the immutable ledger.

## 1. Native Interface

- **Inputs**: /task, /triage, /paste screenshots, /transcript packets, BRAIN_DUMP.md (Inbox), TASK_MASTER.md (Ledger).
- **Tools**: run_command (cat), view_file.

If Trello is enabled in local settings/config and the entrypoint is `/track`, run:

```bash
python3 system/scripts/trello_bridge.py intake --apply
```

Then review `system/inbox/trello/reports/latest-intake.md` plus packet files in `system/inbox/trello/incoming/` before accepting any new Trello-originated work into the ledger.

---

## 1A. Default Evidence Inputs

Screenshots/images and transcripts are task-master management inputs by default.

- First extract task/status signal: new work, existing-task progress, blockers, owner/date changes, due dates, source links, and referenced ticket IDs.
- Then apply the Priority Gate before accepting any new active work.
- If the source is ambiguous, return exact candidate `TASK_MASTER.md` rows or detail-file updates for the user to confirm.
- Do not treat screenshots or transcripts as generic profile lookup, reply drafting, or summary requests unless the user explicitly asks for that in the same turn.

---

## 2. Priority Gate (MANDATORY)

**Before creating or accepting ANY new task**, enforce the Priority Gate:

### 2A. Source Validation

Check WHO is assigning the task:
- **the user's direct manager** (direct manager) → ✅ Proceed immediately.
- **the skip-level manager** → ✅ Proceed, inform the manager at next check-in.
- **another authorized stakeholder** → ✅ Proceed, inform the manager at next check-in.
- **Anyone else** → ⚠️ Flag as "Needs manager approval" — do NOT add to active sprint.

### 2B. Scope Validation

Check WHAT the task involves. **Auto-reject** if it falls into OUT OF SCOPE areas:
- Legacy integration issues → ❌ "Out of scope — redirect to integration team."
- Existing UI launches → ❌ "Out of scope — legacy product teams own this."
- Release management → ❌ "Out of scope — CTO responsibility."
- "Filler" or PO-level work for other teams → ❌ "Out of scope — the user is a PM, not a PO."
- Day-to-day engineering support → ❌ "Out of scope — not available PM for tactical eng requests."

### 2C. Strategic Hold Check

If a task involves story refinement, story distribution, or tactical execution artifacts:
- Check if incoming leadership (VP-level) has been onboarded.
- If incoming leadership has NOT started → ⏸️ "Strategic hold — wait for leadership direction before accelerating."

### Reference

The authoritative source for scope and operating rules is: `1. Company/ways-of-working.md`

---

## 3. Cognitive Protocol

### A. Parallel Triage (/triage → /triage)

1.  **Parse**: Split chaotic BRAIN_DUMP.md.
2.  **Priority Gate**: Run § 2 validation on every extracted task.
3.  **Parallel Routing**:
    - **Action**: Append to bugs-master.md and TASK_MASTER.md.
    - **Detail Generation**: For every new task, create a markdown file in 5. Trackers/tasks/{ID}.md using tasks/_TEMPLATE.md.
    - **Bi-Directional Linking**: 
        - Link ID in TASK_MASTER: [ID](tasks/ID.md)
        - Link Owner in TASK_MASTER: [Name](../../4. People/name.md)
        - Append task reference to the Owner profile in 4. People/ under "Active Tasks".
4.  **Zero State**: Clear BRAIN_DUMP.md via run_command to achieve Inbox Zero.

### B. Ledger Management (/task)

- **Task writing standard**:
  - Task titles must be useful and succinct: 5 words or fewer for the task/card title itself.
  - Trello card titles must omit Task Master IDs. Keep the ID in the card body, managed comment, attachment, or local-path reference instead.
  - Put the longer explanation in the body, not the title: one summary sentence of 15 words or fewer.
  - Support the summary with at most 3 short bullets when more context is needed.
  - Include outcome metric, scope boundary, evidence strength, dependency, and next decision gate in the detail file for every accepted active task when known.
  - If any of owner, due date, outcome metric, scope boundary, evidence strength, dependency, or next decision gate is missing for committed work, list the missing field as a concrete question instead of silently accepting a vague task.
  - Maintain a concrete checkbox list for pending work. `## ✅ Subtasks` is the canonical source for task-level open items and should map cleanly to the Trello checklist.
  - Completed checkbox items can stay in the local doc for history, but Trello should only mirror what is still open.
  - Keep the open-item checklist to 3 items or fewer when possible; exceed that only when the work genuinely needs it.
  - Do not use `P0`/`P1`/`P2` prefixes in status labels or Trello labels. Prefer lane-based placement such as `Today`, `Next`, `Later`, or `Follow Up`.
- **Structure**: | ID | Task | Owner | Due | Status |
- **Linking**: The ID column MUST link to tasks/ID.md. The Owner MUST link to 4. People/{owner}.md.
- **Operations**:
  - **Add**: Run Priority Gate (§ 2) first, then append new row, create detail file, and update Owner profile.
  - **Schedule**: Use 🗓️ Scheduled for [Date] for tasks representing meetings/events booked but not yet occurred.
  - **Manual Override**: If user says "X is scheduled" without calendar verification, trust and update status.
  - **Complete**: Move to "Completed Tasks" and update the task detail header and Progress Log to ✅ Done.
- **Sort**: Keep active work grouped by lane (`Today`, `Next`, `Later`, `Follow Up`, `Triage`) and then by Due Date (closest first).

### B1. Task Health Review (MANDATORY)

Before finishing `/task`, `/triage`, or any daily planning pass:

1. Run `python3 system/scripts/task_master_triage.py --apply`
2. Refresh the managed triage summary block in `5. Trackers/TASK_MASTER.md`
3. Surface overdue, stale, at-risk, and possibly-complete items as explicit questions to the owner
4. For each flagged item, include:
   - What it is
   - Last activity
   - Communication signal
   - Relevant links
   - Clarify
5. Never ask the owner to interpret a bare task ID without title/context
6. Never silently mark an open task done just because the latest note sounds positive

For a single user-provided screenshot, email/chat snippet, or transcript excerpt that updates known task IDs, use the targeted fast path instead of rewriting every flagged task file:

```bash
python3 system/scripts/task_master_triage.py --apply --touched-task TASK-123
```

- Repeat `--touched-task` for every task detail file changed in the intake.
- This still refreshes the `TASK_MASTER.md` managed triage summary and writes the day triage report.
- It only adds/removes managed triage blocks inside the touched task files; a full `/task`, `/triage`, `/day`, or `/week` run should still use the broad `--apply` mode.

### C. FAANG/BCG Rigor

- **Outcome**: Every task includes expected outcome/metric.
- **Scope Boundary**: Every accepted task states what is in scope, what is out of scope, and who owns the next decision.
- **Evidence Strength**: Mark the source as None, Weak, Moderate, or Strong so the user can tell whether work came from a hard signal or a loose ask.
- **Decision Gate**: Every non-trivial task includes the next date or event where the task should be continued, killed, delegated, or reframed.
- **Progress Log**: Every task detail file MUST track a chronological log of updates.

---

## 4. Output

- **Table**: Show exactly what moved Inbox -> Ledger.
- **Gate Results**: Flag any tasks that were rejected or flagged "Needs manager approval."
- **Next Action**: Suggest the top `Today` item from `5. Trackers/TASK_MASTER.md`.

---

## 5. Fallback Patterns

- Use run_command for all file writes to avoid iCloud sync-locks.
- Redact PII before writing.

---

## 6. Cross-Skill Routing

- **To core-utility**: For vacuum/cleanup.
- **To ways-of-working**: For scope validation reference.
