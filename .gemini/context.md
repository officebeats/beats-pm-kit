# PM Brain Project Context

> This file defines the project context for Gemini CLI Conductor.
> It is read by the AI agent to understand the codebase before generating code or suggestions.

## Project Overview

**Name**: Beats PM Antigravity Brain
**Type**: Personal Knowledge Management System for Product Managers
**Platform**: File-based Markdown system designed for LLM-powered agents
**Version**: 1.9.0

---

## Tech Stack

| Layer | Technology | Location |
| :--- | :--- | :--- |
| **Orchestration** | Markdown prompts | `KERNEL.md` |
| **Agents** | LLM prompt files | `Beats-PM-System/system/agents/*.md` |
| **Configuration** | User preferences | `SETTINGS.md` |
| **Status Dashboard** | Current state | `STATUS.md` |
| **Cockpit UI** | React + TypeScript + Vite | `Beats-PM-System/cockpit/` |

---

## Folder Structure (0-5 Standard)

```
beats-pm-antigravity-brain/
├── 0. Incoming/         # Central intake (screenshots, clipboard, pastes)
├── 1. Company/          # Company profiles, communications, strategy
│   └── [Company]/
│       ├── PROFILE.md
│       ├── COMMUNICATION/
│       ├── STRATEGY/
│       └── PLANNING/
├── 2. Products/         # Product-specific PRDs, initiatives, bugs
│   └── [Company]/
│       └── [Product]/
├── 3. Meetings/         # Meeting notes and daily briefs
│   ├── daily-briefs/
│   ├── general/
│   └── 1-on-1s/
├── 4. People/           # Stakeholder directory
├── 5. Trackers/         # Unified trackers
│   ├── bugs/
│   ├── critical/
│   ├── people/
│   ├── projects/
│   └── strategy/
├── Beats-PM-System/     # System logic, agents, templates
├── .gemini/             # Conductor context files
├── KERNEL.md            # Universal routing rules
├── SETTINGS.md          # User configuration
└── STATUS.md            # Current state dashboard
```

---

## Agent Inventory

### Orchestrator Agents (Route to Others)

| Agent | File | Commands |
| :--- | :--- | :--- |
| Meeting Synthesizer | `meeting-synthesizer.md` | `#transcript`, `#meeting`, `#notes` |
| Requirements Translator | `requirements-translator.md` | `#boss`, `#bug`, `#task`, `#feature` |
| Daily Synthesizer | `daily-synthesizer.md` | `#day`, `#morning`, `#eod` |

### Specialized Agents

| Agent | File | Commands |
| :--- | :--- | :--- |
| Boss Tracker | `boss-tracker.md` | `#boss` |
| Bug Chaser | `bug-chaser.md` | `#bug` |
| Engineering Collaborator | `engineering-collaborator.md` | `#eng` |
| UX Collaborator | `ux-collaborator.md` | `#ux` |
| Stakeholder Manager | `stakeholder-manager.md` | `#stakeholder` |
| Strategy Synthesizer | `strategy-synthesizer.md` | `#strategy` |

---

## Architectural Patterns

### Lazy-Load Protocol
- **Startup**: Only load `KERNEL.md`, `SETTINGS.md`, `STATUS.md`.
- **On Trigger**: Load specific agent file when invoked.
- **On Demand**: Load data folders only when explicitly referenced.

### Parallel Agent Execution
Multiple agents can run simultaneously from a single input. Example: A meeting transcript fans out to Boss Tracker, Bug Chaser, and Engineering Collaborator in parallel.

### Consultant Mode (v1.9.0)
- **Company Anchor Rule**: New projects anchor to `1. Company/[Company]/`.
- **Organic Creation**: If a company isn't recognized, create `PROFILE.md` first.

### Privacy Protocol
- Files in `1. Company/`, `2. Products/`, `3. Meetings/`, `4. People/`, `5. Trackers/` are never pushed to git.
- Only system logic and templates are version-controlled.

---

## Key Workflows

### Daily Brief (`#day`)
1. Scan all trackers in parallel.
2. Prioritize: Boss requests → Critical bugs → Stale items → Calendar.
3. Generate succinct, table-based brief.
4. Update `STATUS.md` timestamp.

### Capture (`#boss`, `#bug`, `#task`)
1. Route to appropriate tracker file.
2. Auto-assign ID and priority.
3. Extract context and people mentioned.

### Meeting Processing (`#transcript`)
1. Parse transcript for actionable items.
2. Fan out to specialized agents in parallel.
3. Create files in appropriate locations.
4. Return unified summary.

---

## Testing Strategy

- **Regression Tests**: Defined in `Beats-PM-System/docs/regression-tests.md`.
- **Manual Verification**: Run `#day` after changes to verify synthesizer works.

---

## Dependencies

| Tool | Purpose |
| :--- | :--- |
| Gemini CLI | Primary AI interface |
| Git | Version control for system logic |
| Markdown | All documentation and data |
