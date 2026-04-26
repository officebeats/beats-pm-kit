# Codex Command Index

This file makes slash-command routing explicit for Codex.

## Dispatch Rule

If the user's first non-whitespace token is `/command`:

1. Strip the leading `/`.
2. Look up the command in the table below.
3. Read the matching workflow file in `.agent/workflows/`.
4. Treat any remaining user text as workflow input.
5. If no match exists, report an unknown command and suggest `/help`.

Promoted Codex skill adapters can be synced locally with `python3 system/scripts/sync_codex_skill_adapters.py`.

## Commands

| Command | Workflow File | Codex Mode | Aliases | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `/accuracy` | `.agent/workflows/accuracy.md` | Dispatch only | — | Implement with high accuracy and self-review (optimized for per-prompt pricing) |
| `/archive` | `.agent/workflows/archive.md` | Dispatch only | — | See workflow file |
| `/boss` | `.agent/workflows/boss.md` | Native skill `beats-boss` | — | Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc. |
| `/build` | `.agent/workflows/build.md` | Dispatch only | — | Hand off a PRD or specification to the Engineering team agents for actual implementation. |
| `/challenge` | `.agent/workflows/challenge.md` | Dispatch only | — | Internal adversarial review workflow (self mode only) |
| `/chat` | `.agent/workflows/chat.md` | Dispatch only | — | Consultative planning mode (Switchboard Operator) |
| `/create` | `.agent/workflows/create.md` | Native skill `beats-create` | — | Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks). |
| `/day` | `.agent/workflows/day.md` | Native skill `beats-day` | `/status`, `/morning`, `/brief`, `/now` | Daily briefing and planning. |
| `/discover` | `.agent/workflows/discover.md` | Dispatch only | — | Run a product discovery cycle with OST, assumption mapping, and experiment design. |
| `/export` | `.agent/workflows/export.md` | Dispatch only | — | Export current conversation to archive database |
| `/fan-out` | `.agent/workflows/fan-out.md` | Dispatch only | — | Fan-out a complex PM task to multiple specialized agents in parallel, then synthesize results. |
| `/handoff-chat` | `.agent/workflows/handoff-chat.md` | Dispatch only | — | Clipboard/chat delegation workflow |
| `/handoff-lead` | `.agent/workflows/handoff-lead.md` | Dispatch only | — | Lead Coder one-shot execution workflow |
| `/handoff-relay` | `.agent/workflows/handoff-relay.md` | Dispatch only | — | Relay handoff workflow for model-switch pauses |
| `/handoff` | `.agent/workflows/handoff.md` | Dispatch only | — | Default terminal delegation workflow |
| `/help` | `.agent/workflows/help.md` | Dispatch only | — | The User Manual. Lists commands and explains the system. |
| `/improve-plan` | `.agent/workflows/improve-plan.md` | Dispatch only | — | Deep planning, dependency checks, and adversarial review |
| `/intel` | `.agent/workflows/intel.md` | Dispatch only | — | Capture product knowledge, competitive intelligence, and strategic context from slides, emails, or verbal notes. |
| `/interview` | `.agent/workflows/interview.md` | Dispatch only | — | Run a Socratic deep interview to clarify ambiguous requirements before planning. |
| `/meet` | `.agent/workflows/meet.md` | Native skill `beats-meet` | — | Synthesize meeting transcripts into action items, decisions, and summaries. |
| `/office-cli` | `.agent/workflows/office-cli.md` | Dispatch only | — | Check if OfficeCLI is installed and install it if not. Creates, reads, and edits Word, Excel, and PowerPoint files. |
| `/paste` | `.agent/workflows/paste.md` | Native skill `beats-paste` | — | Capture clipboard content (text, images, files) and save for processing. |
| `/plan` | `.agent/workflows/plan.md` | Native skill `beats-plan` | — | Create or update strategic plans, roadmaps, and OKRs. |
| `/prep` | `.agent/workflows/prep.md` | Dispatch only | — | Prepare for an interview with research and roleplay. |
| `/prioritize` | `.agent/workflows/prioritize.md` | Dispatch only | — | Score and rank a backlog using RICE, ICE, MoSCoW, Kano, or weighted scoring. |
| `/quill` | `.agent/workflows/quill.md` | Dispatch only | — | Process and display the last 5 Quill meetings in a compact, color-coded bullet list with 3-point summaries and action items. |
| `/regression` | `.agent/workflows/regression.md` | Dispatch only | — | See workflow file |
| `/retro` | `.agent/workflows/retro.md` | Dispatch only | — | Run a sprint or PI retrospective with structured format and action tracking. |
| `/review` | `.agent/workflows/review.md` | Dispatch only | — | Code review, Doc review, Release prep. |
| `/sprint` | `.agent/workflows/sprint.md` | Dispatch only | — | Generate a prioritized sprint backlog for dev team planning. |
| `/start` | `.agent/workflows/start.md` | Dispatch only | — | First-time guided setup wizard. Run on first session or manually with /start. |
| `/team` | `.agent/workflows/team.md` | Dispatch only | — | N coordinated engineering/execution agents on a shared task list. |
| `/teams` | `.agent/workflows/teams.md` | Dispatch only | — | Capture Teams chat context and update the Task Master. |
| `/track` | `.agent/workflows/track.md` | Native skill `beats-track` | — | Manage the battlefield. Tasks, Bugs, and Boss Asks. |
| `/transcript` | `.agent/workflows/transcript.md` | Native skill `beats-transcript` | — | Process all Quill meetings from the last 10 business days. |
| `/trello` | `.agent/workflows/trello.md` | Dispatch only | — | Synchronize Beats PM Tracker IDs with a Trello Board, or attach files. |
| `/update` | `.agent/workflows/update.md` | Guarded skill `beats-update` | — | Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes. |
| `/vacuum` | `.agent/workflows/vacuum.md` | Guarded skill `beats-vacuum` | `/archive`, `/cleanup` | Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task archiving, hierarchical integrity auditing, or explicitly triggers /vacuum, /archive, or /cleanup. |
| `/vibe` | `.agent/workflows/vibe.md` | Dispatch only | — | System health and diagnostics. |
| `/week` | `.agent/workflows/week.md` | Native skill `beats-week` | — | Plan the current and upcoming week. |
