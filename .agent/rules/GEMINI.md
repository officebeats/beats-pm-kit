# GEMINI.md - Maestro Configuration

**Version 10.6.0** - BeatsPM Product OS

This file defines the Operating System for the Product Management Brain.

---

## 🔄 STARTUP: First-Run + Health Check (FIRST ACTION EVERY SESSION)

**On the FIRST user message of every new session**, execute this sequence:

### A. First-Run Detection
Check if `.initialized` exists in the project root:
- **If `.initialized` is MISSING** → This is a fresh install. Trigger the `/start` workflow.
- **If `.initialized` EXISTS** → Proceed to Step B.

### B. Health Check
Silently run `system/scripts/context_health.py`.

---

## ⚡ CONTEXT GUARD (ALWAYS ACTIVE)

1. **Parallel-first:** Always batch independent tool calls.
2. **No re-reads:** Never re-read a file already viewed.
3. **Compact responses:** Skip preamble.
4. **Calendar Integrity (New in v10.6.0):** Use unique de-duplication when searching Outlook to prevent ghost meetings.
5. **No PII:** Never include personal names or sensitive details in system-level updates or READMEs.
6. **Priority Gate:** Before creating any new task sourced from outside the authorized stakeholders listed in `1. Company/ways-of-working.md`, flag with "⚠️ Needs manager approval" status. See task-manager skill § 2.
7. **Manager Meeting Enrichment:** When processing any transcript involving the user's direct manager, ALWAYS update `1. Company/ways-of-working.md` with new operating agreements, scope changes, stakeholder dynamics, and standing instructions. See meeting-synth skill § 3A.
8. **No Emojis in External Comms:** When drafting DMs, emails, or external-facing text, do NOT use emojis unless explicitly requested.

---

## 🤖 MULTI-AGENT RUNTIME INTEGRATION

1. **Universal Gateway**: `python3 system/scripts/beats.py {command}`.
2. **Antigravity**: Eagerly use parallel tool calls and `mcp-pencil`.
3. **Shared Context**: Read `5. Trackers/STATUS.md` before starting.

---

_End of System Config — v10.6.0_
