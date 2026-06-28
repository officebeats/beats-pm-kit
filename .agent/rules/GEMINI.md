# GEMINI.md - Maestro Configuration

**Version 10.11.0** - BeatsPM Product OS

This file defines the Operating System for the Product Management Brain.

---

## 🔄 STARTUP: First-Run + Health Check (FIRST ACTION EVERY SESSION)

**On the FIRST user message of every new session**, execute this sequence:

### A. First-Run Detection
If the user provides only the Beats PM Kit GitHub URL, clone/open the repo and run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

Check if `.beats/initialized` exists in the project root:
- **If `.beats/initialized` is MISSING** → Run `python3 system/scripts/bootstrap.py --agent --non-interactive`, then trigger `/start` only if optional profile setup is needed.
- **If `.beats/initialized` EXISTS** → Proceed to Step B.

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
9. **No Outbound Email On User's Behalf:** Never send emails as the user. Do not create, send, forward, or reply to email unless the user explicitly asks for that specific message in the current turn. Default to local notes or draft text in the response instead of using mail tools.
10. **MCP Communication Intake:** `/beats-comms` is the read-only named-source intake path for Slack, Teams, Outlook, and Calendar across Antigravity, Codex, and Claude Code. Follow `.agent/rules/MCP_COMMUNICATION_INTAKE.md`; keep private MCP config, tokens, tenant/client IDs, allowlists, transcripts, and run reports out of tracked files.
11. **Screenshot & Transcript Default Intent:** When the user shares a screenshot, image, or transcript without an explicit alternate instruction, assume the intent is task-master management. Extract tasks, status changes, blockers, owners, due dates, source references, and referenced tickets/links; route through the task-manager Priority Gate into `5. Trackers/TASK_MASTER.md` or return exact local tracker updates to confirm. Do not default to profile lookup, reply drafting, or generic summarization.
12. **PM Decision Router:** For `/paste`, `/track`, `/transcript`, `/beats-comms`, `/discover`, `/create`, `/plan`, and `/prioritize`, classify ambiguous input with `.agent/skills/pm-decision-router/SKILL.md` before accepting durable work. `scope_challenge` and `ask_user` results become explicit questions, not silent active tasks.
13. **Obsidian MCP Read-Only:** Obsidian may be used only as optional read/search/open-file context for the direct-vault kit folder. Check `system/scripts/obsidian_mcp_health.py`; if unavailable, fall back to repo-local `rg`. Never write, patch, delete, move, or command-execute through Obsidian MCP in v1.
14. **Root Cleanliness:** Keep public root clutter minimal. Use `system/scripts/root_cleaner.py --dry-run` to inspect local clutter and `--apply` only when cleanup is explicitly intended; unknown user files move to ignored `0. Incoming/root-cleanup/` instead of being deleted.

---

## 🤖 MULTI-AGENT RUNTIME INTEGRATION

1. **Universal Gateway**: `python3 system/scripts/beats.py {command}`.
2. **Antigravity**: Eagerly use parallel tool calls and `mcp-pencil`.
3. **Shared Context**: Read `5. Trackers/STATUS.md` before starting.
4. **Runtime-Neutral Communication Capabilities**: Prefer runtime-provided read-only MCP/connector capabilities for Slack, Teams, Outlook, and Calendar. Use bridge scripts only as documented fallbacks.

---

_End of System Config — v10.11.0_
