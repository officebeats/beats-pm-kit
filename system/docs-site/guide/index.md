# Getting Started

Welcome to the **Antigravity Brain** — a file-based PM knowledge system powered by AI agents.

## Quick Setup

1. Clone the repo and open it in your terminal
2. Run `/setup` in your AI tool (Gemini CLI, Claude Code, or Antigravity)
3. Edit `SETTINGS.md` with your personal info
4. Start using slash commands: `/day`, `/task`, `/boss`, etc.

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `0. Incoming/` | Raw intake (screenshots, clipboard) |
| `1. Company/` | Company profiles, strategy |
| `2. Products/` | PRDs, initiatives, product bugs |
| `3. Meetings/` | Daily briefs, meeting notes |
| `4. People/` | Stakeholder directory |
| `5. Trackers/` | Task Master, Bug Tracker, Boss Requests |

## Key Files

- **SETTINGS.md** — Your personal config
- **GEMINI.md** — System operating instructions
- **VERSION** — Current kit version

## Architecture

The system uses a Three-Tier Architecture:

1. **Identity Layer** (`.agent/agents/`) — AI personas (CPO, Staff PM, Tech Lead)
2. **Orchestration Layer** (`.agent/workflows/`) — Slash commands that chain agents + skills
3. **Capability Layer** (`.agent/skills/`) — Atomic domain expertise

## Web UIs

The kit includes three optional web frontends:

| App | Location | Port | Command |
|-----|----------|------|---------|
| Live Dashboard | `system/dashboard/` | `:5173` | `npm run dev` |
| PM Command Center | `system/pm-dashboard/` | `:5174` | `npm run dev` |
| Docs Site | `system/docs-site/` | `:5175` | `npm run docs:dev` |
