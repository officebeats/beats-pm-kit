# Getting Started

Beats PM Kit is a local-first Markdown workspace for grounding product work in past meetings, transcripts, chats, decisions, and accepted tasks.

## Quick Setup

1. Clone `https://github.com/officebeats/beats-pm-kit`.
2. Open the repository in Codex, Claude Code, Gemini CLI, Antigravity, or another supported runtime.
3. Run `python3 system/scripts/bootstrap.py --agent --non-interactive`.
4. Run `/start` and optionally `/obsidian` to use the existing repository as a vault.

Private profile details belong in ignored local files such as `SETTINGS.md`; never add them to the public template.

## Core Workflow

1. Capture or export evidence from Granola, Quill, Outlook, Teams, or Slack.
2. Use `/find`, `/paste`, or `/transcript` to retrieve and normalize that evidence.
3. Reconcile commitments through `/track` into the Markdown Task Master and task notes.
4. Use `/day`, `/week`, `/plan`, and `/create` for delivery work grounded in those sources.

## Folder Structure

| Folder | Purpose |
|:---|:---|
| `0. Incoming/` | Raw local intake and exports |
| `1. Company/` | Company context and working agreements |
| `2. Products/` | PRDs, initiatives, and product briefs |
| `3. Meetings/` | Transcripts, summaries, and evidence archives |
| `4. People/` | Local stakeholder context |
| `5. Trackers/` | Task Master, workstreams, tasks, and follow-ups |
| `6. SOPs/` | Local procedures and reusable runbooks |

The numbered workspace folders are ignored by default except for their public skeleton files.

## Optional Interfaces

| Interface | Location | Use |
|:---|:---|:---|
| Markdown and Obsidian | Repository root | Canonical task and knowledge workspace |
| Read-only dashboard views | `system/dashboard/` | Optional browsing of supported task schemas |
| Documentation catalog | `system/docs-site/` | Dependency-free Markdown guide generated from canonical registry data |
