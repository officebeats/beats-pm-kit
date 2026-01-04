# Beats PM Antigravity Brain

> Instructional Memory for Gemini CLI. This file is read automatically on every session.

## System Overview

You are assisting with the **Beats PM Antigravity Brain**, a file-based knowledge management system for Product Managers. All data is stored in Markdown files.

## Folder Structure (0-5 Standard)

| Folder | Purpose |
| :--- | :--- |
| `0. Incoming/` | Raw intake (screenshots, clipboard) |
| `1. Company/` | Company profiles, strategy |
| `2. Products/` | PRDs, initiatives, product bugs |
| `3. Meetings/` | Daily briefs, meeting notes |
| `4. People/` | Stakeholder directory |
| `5. Trackers/` | Bugs, boss-requests, projects |

## Key Files

- **KERNEL.md**: Universal routing rules (read for detailed agent logic)
- **SETTINGS.md**: User preferences (boss, team, products)
- **STATUS.md**: Current state dashboard

## Agent Commands

| Command | Action |
| :--- | :--- |
| `#day` | Generate time-adaptive brief |
| `#boss` | Log boss request |
| `#bug` | Log bug |
| `#task` | Log task |
| `#transcript` | Process meeting transcript |

## Behavior Rules

1. **Lazy-Load**: Only read KERNEL.md, SETTINGS.md, STATUS.md on startup. Load other files on-demand.
2. **Parallel Execution**: Run multiple agents simultaneously when parsing transcripts.
3. **Succinct Output**: Tables over prose. No fluff.
4. **Source Preservation**: Always preserve raw source text when extracting insights.
5. **Parking Lot**: If input is unclear, log to BRAIN_DUMP.md instead of asking 20 questions.
6. **Access Override**: Files in `1. Company` through `5. Trackers` and `SETTINGS.md` are gitignored for privacy but **fully readable**. If `view_file` fails due to gitignore, you MUST use `run_command` (e.g., `cat`) to read them. Do not ask for permission; just do it.
7. **User Persona**: The user is the **"Defacto AI PM"** (Consumer Focus). Prioritize Consumer-Facing AI solutions over Backend/Infrastructure ideas unless explicitly asked for technical specs.
8. **Formatting**: Use **sub-bullets** for detailed lists (prose) rather than comma-delimited strings/tables, unless data is strictly structured.
9. **Leadership Resonance**: Check SETTINGS7. Does your leadership come from any other industries (e.g., Finance, Retail, Automotive)? This helps me suggest relevant analogies. or metaphors from the user's defined industries to increase persuasive impact.

## Privacy

- Files in 1-5 folders are **local only**—never push to GitHub.
- Use `.gitkeep` files to preserve folder structure.

## Conductor Integration

Context files in `.gemini/` define project architecture and templates. Use `/conductor:newTrack` for spec-driven development.
