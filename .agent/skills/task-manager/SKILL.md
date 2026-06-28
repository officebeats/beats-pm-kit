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
version: 4.1.0 (Workstream Snapshot)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Task Manager Skill

> **Role**: Execution Engine. You ruthlessly triumph over the BRAIN_DUMP and enforce the TASK_MASTER as the immutable ledger.

## 1. Native Interface

- **Inputs**: /task, /triage, /paste screenshots, /transcript packets, bare `task-manager` / `$task-manager`, BRAIN_DUMP.md (Inbox), TASK_MASTER.md (Ledger).
- **Tools**: run_command (cat), view_file.

If Trello is enabled in local settings/config and the entrypoint is `/track`, run:

```bash
python3 system/scripts/trello_bridge.py intake --apply
```

Then review `system/inbox/trello/reports/latest-intake.md` plus packet files in `system/inbox/trello/incoming/` before accepting any new Trello-originated work into the ledger.

---

## 1A. No-Context Workstream Snapshot

When the user invokes `task-manager`, `$task-manager`, `/task`, or the Task Manager skill without additional pasted evidence, a command, or a scoped source:

1. Do **not** broad-scan Outlook, Teams, Slack, Trello, Jira, Confluence, Quill, Granola, Obsidian, or local graph memory.
2. Return the human-facing workstream snapshot first, using:

```bash
python3 system/scripts/workstream_snapshot.py --mode task --limit 12
```

3. If `5. Trackers/WORKSTREAMS.md` has real workstream rows, render those rows exactly in the title, bullet, and sub-bullet format from § 1B.
4. If `5. Trackers/WORKSTREAMS.md` is missing or only contains the template row, use the script fallback from ranked local Task Master commitments and say that it is a local fallback, not a live-source refresh.
5. Keep internal Task Master IDs, Jira IDs, Trello IDs, and source IDs out of headings and evidence prose. Use them only as local links, metadata, or an `Agent refs` line.
6. Include a short coverage note:
   - `Local workstream snapshot only` when no live source refresh was requested.
   - `Live refresh blocked` only when a requested or configured source failed health and the user must decide how to proceed.

This no-context mode is a snapshot command, not a triage run. Do not run `task_master_triage.py --apply`, Trello sync, live connector reads, or third-party health prompts unless the user asks for a refresh, `/day`, `/week`, `/boss`, `/track`, `/beats-comms`, or a scoped source intake.

---

## 1B. Default Evidence Inputs

Screenshots/images and transcripts are task-master management inputs by default.

- First extract task/status signal: new work, existing-task progress, blockers, owner/date changes, due dates, source links, and referenced ticket IDs.
- Then apply the Priority Gate before accepting any new active work.
- If the source is ambiguous, return exact candidate `TASK_MASTER.md` rows or detail-file updates for the user to confirm.
- Do not treat screenshots or transcripts as generic profile lookup, reply drafting, or summary requests unless the user explicitly asks for that in the same turn.

## 1C. Workstream Operating Model

The human-facing unit of planning is the workstream, not the Task Master ID.

- Maintain the workstream index in `5. Trackers/WORKSTREAMS.md` when present.
- Maintain per-workstream detail files in `5. Trackers/workstreams/{slug}.md` when present.
- Workstream titles must be well-articulated, plain English, and 9 words or fewer.
- Do not show Task Master IDs, Jira IDs, card IDs, or source IDs in workstream titles, task labels, evidence prose, or owner questions. Keep them in agent refs, links, metadata, card bodies, managed comments, or evidence logs.
- Each workstream must track:
  - Latest outcomes.
  - Completed outcomes and completed checklist items, with completion date and source.
  - Open items from Outlook, Teams, Slack, Calendar, manual transcripts, Quill, Granola, and local transcript packets when a named read-only source window is available.
  - The recommended next 3 actions.
  - Internal agent references linking to Task Master rows, task files, Trello cards, Jira/Confluence artifacts, and transcript/chat evidence.
- Before finishing `/task`, `/track`, `/day`, `/week`, `/boss`, `/beats-comms`, or `/transcript`, reconcile new evidence against the workstream list so duplicate source signals consolidate into the same workstream instead of creating parallel status islands.
- Before recurring aggregation for `/day`, `/week`, or `/boss`, run `python3 system/scripts/critical_commitment_refresh.py plan --mode <day|week|boss> --json` and `python3 system/scripts/critical_commitment_refresh.py rank --mode <day|week|boss> --json`.
- If a configured or expected integration is broken, unavailable, missing a scope, or unsafe, prompt the user with what failed, why it matters, the recommended fix, and safe choices. Do not silently proceed with degraded coverage.
- If live Outlook, Teams, Slack, Quill, Granola, Obsidian, or graph-memory access is unavailable or lacks a named read-only source window, prompt instead of broad-scanning. Continue degraded only after the user explicitly chooses to skip once, paste/export evidence, configure the source, or disable it from defaults.
- Treat third-party systems as read-only unless the user explicitly confirms the exact mutation in the current turn. Never send, draft, reply, react, schedule, create, assign, transition, comment, upload, patch, delete, or move third-party state by default.
- Leadership, boss-of-boss, external partner/customer, and dated end-user commitments must rank above ordinary stale work.
- Intake from Outlook, Teams, Slack, Planner, Atlassian, transcripts, Quill, Granola, Trello, Obsidian, and graph memory must normalize into this workstream model before creating new local tasks.
- Each source finding should carry: workstream match/title, latest outcome, completed outcome signal, open item, recommended next action, authority tier, commitment type, due gate, evidence strength, completion state, and source reference.
- Each task/workstream display must carry `display_title`, `started_at`, `initial_source`, `latest_source`, and internal `agent_refs`. Render evidence as `[title]; started from [initial source] on [date]; latest progress from [latest source] on [date].`
- Explicit completion evidence may check off local/Trello checklist items and must preserve the completion date/source.
- Implied completion evidence becomes a confirmation question; do not check off the item silently.

Default user-facing format:

```markdown
### Workstream Title
- Latest outcome: [succinct result, decision, or state]
  - Evidence: [task/workstream title; started from initial source on date; latest progress from latest source on date]
- Completed: [done item or "None newly confirmed"]
  - Completed: [date/source]
- Open items: [count or short list]
  - [Owner] - [action] by [date/gate], from [source]
- Recommended next 3:
  - [Action 1]
  - [Action 2]
  - [Action 3]
```

Use this title, bullet, and sub-bullet structure for recurring Task Master-related closeouts unless the user explicitly asks for a table or export format.

## 1D. Fast Raw-Evidence Intake

For a single pasted email/chat/thread or a message prefaced with "for task manager", use the fast path unless the user explicitly asks for full triage, Trello sync, `/day`, `/week`, or broad communication refresh:

```bash
python3 system/scripts/task_intake_fast.py --text "<raw pasted evidence>" --source "<source label>"
```

Fast intake rules:

- Always save the raw evidence first under `0. Incoming/raw/`, preserving names, timestamps, links, and message wording.
- Add a short summary and task-manager routing read below the raw evidence; keep interpretation separate from the raw source.
- If an existing task match is strong enough, update that task and the matching `TASK_MASTER.md` row.
- If confidence is low, still create an `INBOX-###` candidate task rather than dropping the signal.
- Defer expensive health triage by default. Run `task_master_triage.py --apply --touched-task <ID>` only when the user asks for the full health refresh or a deeper workflow needs it.
- Rebuild the task cache with `python3 system/scripts/build_task_index.py` during `/day`, `/week`, `/vacuum`, or after substantial tracker edits.
- Treat task IDs as internal anchors only. User-facing labels, weekly-email sections, closeouts, and source-note headings must use succinct descriptive phrases such as `[New] IAD Indicia guideline tenant configuration`.

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
  - Workstream and card titles must be useful, succinct, and descriptive: 9 words or fewer as a plain-English phrase.
  - Task titles should still be short and descriptive, usually 3-8 words.
  - Trello card titles, weekly-email sections, closeouts, and source-note headings must omit Task Master IDs. Keep the ID in links, internal fields, card bodies, managed comments, attachments, or local-path references instead.
  - Put the longer explanation in the body, not the title: one summary sentence of 15 words or fewer.
  - Support the summary with at most 3 short bullets when more context is needed.
  - Include outcome metric, scope boundary, evidence strength, dependency, and next decision gate in the detail file for every accepted active task when known.
  - If any of owner, due date, outcome metric, scope boundary, evidence strength, dependency, or next decision gate is missing for committed work, list the missing field as a concrete question instead of silently accepting a vague task.
  - Maintain a concrete checkbox list for pending work. `## ✅ Subtasks` is the canonical source for task-level open items and should map cleanly to the Trello checklist.
  - Completed checkbox items must stay visible in local task/workstream history with completion date and source. During Trello sync, mirror completed items as checked checklist entries for the current reporting window instead of deleting them from the managed view.
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

Exception: the no-context workstream snapshot mode in § 1A is read-only and must not run this broad apply pass unless the user asks for triage or refresh.

1. Run `python3 system/scripts/task_master_triage.py --apply`
2. Refresh the managed triage summary block in `5. Trackers/TASK_MASTER.md`
3. Refresh `5. Trackers/WORKSTREAMS.md` and matching `5. Trackers/workstreams/` files when they exist
4. Surface overdue, stale, at-risk, and possibly-complete items as explicit questions to the owner
5. For each flagged item, include:
   - What it is
   - Last activity
   - Communication signal
   - Relevant links
   - Clarify
6. Never ask the owner to interpret a bare task ID without title/context
7. Never silently mark an open task done just because the latest note sounds positive

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
- **Completion Evidence**: Every completed item includes when it completed and which source confirmed it.
- **Progress Log**: Every task detail file MUST track a chronological log of updates.

---

## 4. Output

- **Workstreams first**: Lead with the title, bullet, and sub-bullet format from § 1B for any recurring Task Master-related output.
- **Movement summary**: Show exactly what moved Inbox -> Ledger after the workstream readout.
- **Gate Results**: Flag any tasks that were rejected or flagged "Needs manager approval."
- **Next Action**: Suggest the top `Today` item from `5. Trackers/TASK_MASTER.md`.
- **Display rule**: Show descriptive workstream/task phrases first. Put internal IDs only in local links, metadata, managed bodies, or an `Agent refs` line.

---

## 5. Fallback Patterns

- Use run_command for all file writes to avoid iCloud sync-locks.
- Preserve user-provided raw source details in source notes; do not summarize away names, timestamps, links, or message wording.

---

## 6. Cross-Skill Routing

- **To core-utility**: For vacuum/cleanup.
- **To ways-of-working**: For scope validation reference.
