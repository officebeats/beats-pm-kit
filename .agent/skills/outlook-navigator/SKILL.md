---
name: outlook-navigator
description: Read-only Outlook email scraper for context and task extraction.
priority: P1
triggers:
  - "/outlook"
  - "/inbox"
  - "/sync-mail"
version: 1.0.0
---

> **Compatibility Directive**: Optimized for Google Antigravity/macOS desktop clients.

# Outlook Navigator Skill

## Goal
The outlook-navigator is the 'Eye' of the brain into the user's primary communication channel. It fetches recent emails for context but NEVER performs write operations (no replying, no deleting).

## Inputs
- `/outlook` (Fetch last 5)
- `/outlook --count 10`
- `/inbox`

## Protocol

1.  **Fetch**: Run `python3 system/scripts/outlook_bridge.py --count {n}`.
2.  **Persist**: Write the results to `0. Incoming/outlook_context.md` for downstream skills (e.g. `meeting-synth`) to consume.
    - // turbo
    - `python3 system/scripts/outlook_bridge.py --count 10 > 0. Incoming/outlook_context.md`
3.  **Analyze**:
    - Identify **Deadlines** (dates, "by Friday", "asap").
    - Identify **Decisions** (approvals, rejects).
    - Identify **Company Strategy** changes.
3.  **Triage**:
    - If a task is found -> Suggest `/track` item.
    - If context is found -> Suggest `memory-consolidator` update.

## Output Format

### 📬 Inbox Context (Read-Only)

- **[Subject]** (from [Sender] at [Date])
  * *Snippet*: "[200-char preview...]"
  * *PM Action*: [Identified task or context update]

