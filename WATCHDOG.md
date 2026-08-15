# WATCHDOG.md — advisor review priorities for beats-pm-kit

This is a product-management harness (Markdown vault + scripts), not a codebase. Review agent output against these priorities, highest first.

## Fabrication (blocker)

- Stakeholder quotes, meeting statements, or decisions that do not appear in `3. Meetings/` transcripts/summaries or `5. Trackers/` records. Every attributed claim needs a source file.
- Invented Jira keys, Confluence page IDs, ADO work item IDs, client names, or metrics. If it was not read from a tool result or a vault file this session, flag it.
- Dates/deadlines asserted without a source (calendar, transcript, or tracker).

## Outbound actions (blocker)

- Drafting is fine; SENDING is not. Flag any attempt to send email, post to Slack/Teams, or transition Jira issues unless the user explicitly asked for that exact message/action this turn (see ~/.codex/AGENTS.md guardrails).
- Confluence/Jira/ADO writes: confirm the user asked for the write, not just a draft.

## Privacy (blocker)

- PHI or member/patient-level data leaving the vault (into web searches, external MCP writes, or shared artifacts). This is a healthcare context; treat anything resembling clinical or member data as radioactive.
- Client-confidential material (8. Clients/, 7. Partners/) appearing in generic web-facing output.

## Structure drift (concern)

- Task state written anywhere other than the canonical trackers (`5. Trackers/TASK_MASTER.md` and `5. Trackers/tasks/`).
- Edits to generated adapter dirs (`.claude/`, `.codex/`, `.gemini/`, `.cursor/`, `.kilocode/`, ...) instead of the source of truth `.agent/` — the sync script will clobber them.
- New top-level files/folders that ignore the numbered-folder taxonomy.

## Quality bar (aside)

- Action-first output: recommendations before background (`.agent/rules/ACTION_FIRST_OUTPUT.md`).
- Summaries that silently drop open questions, risks, or dissenting voices from a transcript.
