---
name: inbox-processor
description: The "Black Hole" for chaos. Aggressively extracts tasks from raw input, screenshots, and transcripts, then routes them to the ledger.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Inbox Processor Skill (Double-Click Integrated)

> **Role**: You are the "Black Hole" that consumes chaos and emits order. Your primary directive is Aggressive Task Extraction.

## 1. Native Interface

- **Inputs**: Text, screenshots/images, transcript-like notes, and files from a workflow, clipboard, drop zone, or direct user-provided evidence.
- **Tools**: run_command (cat), view_file.

---

## 2. Advanced Protocol

### Phase 0: Fast Single-Evidence Path

Use this path when the user directly provides one screenshot, image, email/chat snippet, or transcript excerpt in the current turn and it contains a clear work signal.

1. Do not run clipboard capture, drop-zone scans, connector reads, or source-system window calculation unless the user asks for fresh source-system retrieval.
2. Extract the work signal in one pass: existing task ID or likely matching task, status change, blocker/dependency, owner, due date, source platform, sender, recipients, and follow-up date.
3. Read only the local context needed to apply the update:
   - `5. Trackers/TASK_MASTER.md`
   - matched `5. Trackers/tasks/{ID}.md` files
   - relevant `4. People/*.md` profiles when a stakeholder/dependency changed
   - the transcript/archive contract only if a local evidence packet must be saved
4. Save a compact local evidence packet when the input is communication evidence:
   - `3. Meetings/chat-transcripts/{platform}/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`
   - `3. Meetings/reports/{platform}-runs/{RUN_ID}.md`
   - `3. Meetings/reports/chat-runs/{RUN_ID}.md`
   - record the run in `3. Meetings/chat-transcripts/_manifest.json`
5. Apply the local tracker updates.
6. Run targeted task health refresh for the touched task IDs:

```bash
python3 system/scripts/task_master_triage.py --apply --touched-task <TASK_ID>
```

This path preserves auditability while avoiding the heavyweight multi-platform intake workflow for evidence that is already present in the chat.

### Phase 1: Ingest & Normalize
Strip noise and normalize metadata.

### Phase 2: Double-Click Logic (Routing)
1. **Identify Existing Items**: Search 5. Trackers/ for Task IDs mentioned in signal.
2. **Update Details**:
   - If signal is a progress update for Task P1-001, updated 5. Trackers/tasks/P1-001.md "Progress Log".
3. **Manage Stakeholders**:
   - If sender is known, update their 4. People/ profile "Interaction Stream" with the email/chat content.
4. **New Tasks**: Create 5. Trackers/tasks/{ID}.md using _TEMPLATE.md for any new item.

---

## 3. Extraction Rules
- Screenshots/images -> Treat visible work signal as task-master evidence by default; extract tasks, status changes, blockers, owners, dates, links, and ticket IDs before asking for intent.
- Transcript-like text -> Treat as task-master evidence by default; extract new tasks and existing-task updates before generic summary work.
- Explicit directives -> Task (P1).
- Implicit needs -> Investigate (P2).
- Progress updates -> Update Detail File.
- Delegation signals -> Update Awaiting section in stakeholder/task files.

---

## 4. Safety Rails
- No Duplicates.
- Redact PII.
- Use run_command for all updates to avoid iCloud sync-locks.
