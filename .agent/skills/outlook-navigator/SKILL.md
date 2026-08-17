---
name: outlook-navigator
description: Read-only Outlook mail and Calendar intake for context, task extraction, schedule awareness, and stakeholder enrichment.
---

> **Compatibility Directive**: Prefer read-only MS365 MCP/connector capabilities in Antigravity, Codex, Claude Code, and compatible runtimes. Use macOS AppleScript bridge scripts only as less-portable fallbacks when MCP/connector reads are unavailable.

# Outlook Navigator Skill

## Quick Path

1. Resolve an explicit named mail or calendar scope; compute missing windows with `chat_intake_state.py window --platform outlook|calendar --scope "<SCOPE>"` (mail defaults 5 business days back; calendar 14 days forward).
2. Prefer read-only MS365 MCP/connector reads; use `outlook_bridge.py` (AppleScript) only when connector reads are unavailable and label it as a fallback.
3. Persist evidence via the chat-transcript-archive skill to `3. Meetings/chat-transcripts/outlook|calendar/` plus run reports.
4. Analyze for deadlines, decisions, strategy changes, scheduled events, latest/completed outcomes, and open items per workstream.
5. Enrich `4. People/{firstname-lastname}.md` from senders, CCs, and email signatures.
6. Triage: route workstream updates, suggest `/track` items, send boss asks to `5. Trackers/critical/boss-requests.md`; ask before checking off implied completions.

Never create, send, modify, or delete mail or calendar items. Go deeper into the Protocol steps for scope rules and the Hard Safety Rules before any borderline operation.

## Goal
The outlook-navigator is the read-only mail and calendar intake path. It fetches named Outlook and Calendar source windows for local workstream/task synthesis but does not mutate Microsoft 365 state.

## Inputs
- `/outlook` (Fetch last 5)
- `/outlook --count 10`
- `/outlook --calendar 7` (Fetch calendar events for next N days)
- `/beats-comms outlook: <named mail query/window>`
- `/beats-comms calendar: <named lookahead/window>`
- `/inbox`

## Protocol

### Step 1: Resolve Scope And Window

Require an explicit named read-only mail or calendar source window before reading source systems.

Valid mail scopes include sender, subject keyword, folder, conversation, or time window. Valid calendar scopes include lookahead days, date range, meeting title, or participant.

If the scope omits a time window, compute it with:

```bash
python3 system/scripts/chat_intake_state.py window --platform outlook --scope "<SCOPE>"
python3 system/scripts/chat_intake_state.py window --platform calendar --scope "<SCOPE>"
```

Outlook defaults to 5 business days back. Calendar defaults to 14 days forward.

### Step 2: Prefer MS365 MCP/Connector Reads

Use read-only MS365 MCP/connector capabilities first when surfaced by the runtime:

- Outlook mail: list/search/get mail messages, folders, attachments metadata, people/contacts as needed for a scoped read.
- Calendar: list/get calendar events, schedule view, meeting metadata, meeting transcript metadata/content when explicitly scoped and available.

Do not use write-capable tools for sends, replies, forwards, draft creation, event creation, meeting updates, reminders, Todo, Planner, or mailbox/calendar modifications during intake.

### Step 3: Fallback To macOS Bridge Scripts

Use `outlook_bridge.py` only when MCP/connector reads are unavailable or the runtime cannot surface the needed read operation. Label this as a less-portable AppleScript fallback in the run report.

Fetch recent scoped inbox snippets:

```bash
python3 system/scripts/outlook_bridge.py --count {n}
```

Deep-read specific matching emails only when needed for extraction:

```bash
python3 system/scripts/outlook_bridge.py --search "subject keyword"
```

Fetch calendar lookahead:

```bash
python3 system/scripts/outlook_bridge.py --calendar {days}
```

### Step 4: Persist Local Evidence

Save named source evidence through `.agent/skills/chat-transcript-archive/SKILL.md`:

- Outlook transcript -> `3. Meetings/chat-transcripts/outlook/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`
- Calendar transcript -> `3. Meetings/chat-transcripts/calendar/{YYYY-MM-DD}_{scope-slug}_{RUN_ID}.md`
- Outlook report -> `3. Meetings/reports/outlook-runs/{RUN_ID}.md`
- Calendar report -> `3. Meetings/reports/calendar-runs/{RUN_ID}.md`

Use short snippets and metadata, not full unbounded mailbox or calendar dumps. The `3. Meetings/` output paths are ignored and local-only.

If an upcoming calendar event maps to an active task in `TASK_MASTER.md` to "Schedule a meeting with X", update the task status to `🗓️ Scheduled for [Date]` instead of completing it.

Triangulate named mail and calendar evidence against `5. Trackers/WORKSTREAMS.md` and matching `5. Trackers/workstreams/` files when present. Workstream titles must be plain English, 9 words or fewer, and free of Task Master, Trello, Jira, or source IDs.

### Step 5: Analyze
- Identify **Deadlines** (dates, "by Friday", "asap").
- Identify **Decisions** (approvals, rejects).
- Identify **Company Strategy** changes.
- Identify **Scheduled Events** that satisfy existing scheduling tasks.
- Identify **Latest Outcomes** that should update the matching workstream.
- Identify **Completed Outcomes** only when the email/calendar evidence explicitly confirms completion, then preserve completion date/source.
- Identify **Open Items** and **Recommended Next 3** actions per workstream.

### Step 6: Stakeholder Enrichment
For each person found in emails (senders, CC'd, mentioned, or in signatures):
- **Check** if `4. People/{firstname-lastname}.md` exists.
- **If exists** → Update with new context: recent topics, decisions, asks, role changes.
- **If new** → Create profile from email signature and context.
- **Signature extraction**: Parse email signatures for role, title, department, organization. This is the richest source of role/title data.
- **Privacy**: Store only professional context (name, role, org, relationship). PII (phone, email, address) may be stored in profiles since `4. People/` is gitignored. Extract everything useful from signatures — work email, cell, office address, pronouns, direct reports.

### Step 7: Triage
- If a workstream update is found -> route latest outcome, completed outcome, open item, or recommended next action into the matching workstream.
- If a task is found → Suggest `/track` item.
- If a boss ask is found → Route to `5. Trackers/critical/boss-requests.md`.
- If a new stakeholder is mentioned → Create/update profile in `4. People/`.
- If context is found → Suggest `memory-consolidator` update.
- If completion is implied but not explicit -> ask for confirmation instead of checking it off.

## Implementation Notes

### Why AppleScript Is Fallback Only
- The bridge uses `osascript` to query the locally-installed Microsoft Outlook app on macOS.
- This is less portable than MS365 MCP/connector access and should be labeled as fallback output.
- **Known issue**: Some message types (meeting invites, `«class mtME»`) don't expose `name of sender`. The bridge handles this with try/catch fallback to `address of sender`.

### HARD SAFETY RULES (Non-Negotiable)
- **NEVER create calendar events or meeting invites** — not via AppleScript, MCP, Graph API, or any other method. Calendar writes risk sending invites to attendees with wrong times, duplicates, or broken details that the user must manually undo.
- **NEVER create, send, forward, or reply to email** unless the user explicitly asks for that specific message in the current turn. By default, return draft text in chat or save a local artifact instead of using mail tools.
- **NEVER delete, move, or modify existing emails or calendar events.**

### Privacy
- This skill is **read-only** for inbox/calendar by default.
- Email content persisted to `0. Incoming/` is gitignored and local-only.
- Communication transcripts and reports under `3. Meetings/` are gitignored and local-only.
- Stakeholder profiles in `4. People/` are gitignored and local-only.

## Output Format

### 📬 Inbox Context (Read-Only)

- **[Subject]** (from [Sender] at [Date])
  * *Snippet*: "[200-char preview...]"
  * *Workstream*: [9-word-or-fewer workstream title]
  * *Latest outcome*: [Result, decision, or current state]
  * *Completed*: [Done item + date/source, or None newly confirmed]
  * *Open items*: [Owner/action/date]
  * *Recommended next 3*: [Three short actions]
  * *PM Action*: [Identified task or context update]
  * *Stakeholder*: [Created/Updated profile for X] (if applicable)
