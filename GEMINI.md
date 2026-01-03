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

## Privacy

- Files in 1-5 folders are **local only**—never push to GitHub.
- Use `.gitkeep` files to preserve folder structure.

## Conductor Integration

Context files in `.gemini/` define project architecture and templates. Use `/conductor:newTrack` for spec-driven development.
