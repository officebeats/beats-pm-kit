# Codex Command Index

This file makes slash-command routing explicit for Codex.

## Dispatch Rule

If the user's first non-whitespace token is `/command`:

1. Strip the leading `/`.
2. Look up the command in the table below.
3. Read the matching workflow file in `.agent/workflows/`.
4. Treat any remaining user text as workflow input.
5. If no match exists, report an unknown command and suggest `/help`.

## Commands

| Command | Workflow File | Purpose |
| :--- | :--- | :--- |
| `/boss` | `.agent/workflows/boss.md` | Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc. |
| `/build` | `.agent/workflows/build.md` | Hand off a PRD or specification to the Engineering team agents for actual implementation. |
| `/create` | `.agent/workflows/create.md` | Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks). |
| `/day` | `.agent/workflows/day.md` | Daily briefing and planning. |
| `/discover` | `.agent/workflows/discover.md` | Run a product discovery cycle with OST, assumption mapping, and experiment design. |
| `/fan-out` | `.agent/workflows/fan-out.md` | Fan-out a complex PM task to multiple specialized agents in parallel, then synthesize results. |
| `/help` | `.agent/workflows/help.md` | The User Manual. Lists commands and explains the system. |
| `/intel` | `.agent/workflows/intel.md` | Capture product knowledge, competitive intelligence, and strategic context from slides, emails, or verbal notes. |
| `/interview` | `.agent/workflows/interview.md` | Run a Socratic deep interview to clarify ambiguous requirements before planning. |
| `/meet` | `.agent/workflows/meet.md` | Synthesize meeting transcripts into action items, decisions, and summaries. |
| `/paste` | `.agent/workflows/paste.md` | Capture clipboard content (text, images, files) and save for processing. |
| `/plan` | `.agent/workflows/plan.md` | Create or update strategic plans, roadmaps, and OKRs. |
| `/prep` | `.agent/workflows/prep.md` | Prepare for an interview with research and roleplay. |
| `/prioritize` | `.agent/workflows/prioritize.md` | Score and rank a backlog using RICE, ICE, MoSCoW, Kano, or weighted scoring. |
| `/quill` | `.agent/workflows/quill.md` | Process and display the last 5 Quill meetings in a compact, color-coded bullet list with 3-point summaries and action items. |
| `/regression` | `.agent/workflows/regression.md` | See workflow file |
| `/retro` | `.agent/workflows/retro.md` | Run a sprint or PI retrospective with structured format and action tracking. |
| `/review` | `.agent/workflows/review.md` | Code review, Doc review, Release prep. |
| `/sprint` | `.agent/workflows/sprint.md` | Generate a prioritized sprint backlog for dev team planning. |
| `/start` | `.agent/workflows/start.md` | First-time guided setup wizard. Run on first session or manually with /start. |
| `/team` | `.agent/workflows/team.md` | N coordinated engineering/execution agents on a shared task list. |
| `/teams` | `.agent/workflows/teams.md` | Capture Teams chat context and update the Task Master. |
| `/track` | `.agent/workflows/track.md` | Manage the battlefield. Tasks, Bugs, and Boss Asks. |
| `/transcript` | `.agent/workflows/transcript.md` | Process all Quill meetings from the last 10 business days. |
| `/update` | `.agent/workflows/update.md` | Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes. |
| `/vacuum` | `.agent/workflows/vacuum.md` | Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task archiving, hierarchical integrity auditing, or explicitly triggers /vacuum, /archive, or /cleanup. |
| `/vibe` | `.agent/workflows/vibe.md` | System health and diagnostics. |
| `/week` | `.agent/workflows/week.md` | Plan the current and upcoming week. |
