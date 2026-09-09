---
name: inbox-processor
description: The "Black Hole" for chaos. Aggressively extracts tasks from raw input, screenshots, and transcripts, then routes them to the ledger.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Inbox Processor Skill (Double-Click Integrated)

> **Role**: You are the "Black Hole" that consumes chaos and emits order. Your primary directive is Aggressive Task Extraction.

## 1. Native Interface

- **Inputs**: /paste, /inbox. Text, screenshots/images, transcript-like notes, and files.
- **Tools**: run_command (cat), view_file.

---

## 2. Advanced Protocol

### Phase 0: Fast Single-Evidence Path

Use this path when the user directly provides one screenshot, image, email/chat snippet, or transcript excerpt in the current turn and it contains a clear work signal.

1. Do not run clipboard capture, drop-zone scans, connector reads, or source-system window calculation unless the user asks for fresh source-system retrieval.
2. Extract the work signal in one structured pass: platform, scope, sender, timestamp, message, candidate task title/owner/due/lane, stakeholder details, workstream, and peripheral signals.
3. Execute the automated deterministic Python pipeline in one call:

```bash
python3 system/scripts/communication_intake.py --payload '<STRUCTURED_JSON>'
```

The pipeline atomically:
- Generates the communication transcript (`3. Meetings/chat-transcripts/{platform}/`)
- Generates the platform and chat run reports (`3. Meetings/reports/`)
- Creates or updates the canonical task note (`5. Trackers/tasks/`)
- Creates or updates stakeholder profiles (`4. People/` and `4. People/PEOPLE.md`)
- Creates or updates the workstream record (`5. Trackers/workstreams/`)
- Records the intake run in `3. Meetings/chat-transcripts/_manifest.json`
- Rebuilds Task Master, applies workstream MOC evidence links, and updates task triage
- Returns structured JSON with preview links and ready-to-display workstream snapshot

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
