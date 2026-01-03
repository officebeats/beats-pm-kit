# Beats PM Brain - Agent Index

> **For Antigravity**: This file describes all available agents and how they work together.

---

## 🚀 Quick Start for Antigravity

When a user opens this folder in Antigravity, read this file first to understand:

1. What agents are available
2. How they work together
3. How to route user requests

---

## 🧠 System Architecture

### Parallel Agent Execution

**Antigravity's superpower**: Run multiple agents simultaneously from a single input.

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                               │
│           (text, transcript, notes, commands)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENTS                           │
│                                                                 │
│  • Meeting Synthesizer (#transcript, #meeting, #notes)          │
│  • Requirements Translator (general input routing)              │
│  • Daily Synthesizer (#morning, #lunch, #eod, #day)            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ PARALLEL │   │ PARALLEL │   │ PARALLEL │
        │ AGENT 1  │   │ AGENT 2  │   │ AGENT N  │
        └──────────┘   └──────────┘   └──────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORGANIZED FILES ACROSS SYSTEM                      │
│     (5. Trackers/critical/, 5. Trackers/bugs/, 5. Trackers/people/, 5. Trackers/projects/, 5. Trackers/strategy/, etc.)    │
└─────────────────────────────────────────────────────────────────┘
```

### The Power of Parallel Execution

When a user pastes a meeting transcript, Antigravity can:

1. Parse the content once
2. Identify all actionable items
3. Execute multiple agents **simultaneously**:
   - Boss Tracker handles boss requests
   - Bug Chaser handles bugs
   - Engineering Collaborator handles technical items
   - UX Collaborator handles design tasks
   - Stakeholder Manager flags updates needed
4. Create all files in parallel
5. Return a unified summary

**This turns a 10-minute manual task into a 10-second automated process.**

---

## 📁 Agent Files

### Orchestrator Agents (Route to Others)

| Agent                       | File                         | Primary Commands                                                  | Purpose                                             |
| --------------------------- | ---------------------------- | ----------------------------------------------------------------- | --------------------------------------------------- |
| **Meeting Synthesizer**     | `meeting-synthesizer.md`     | `#transcript`, `#meeting`, `#notes`, `#call`, `#1on1`, `#standup` | Parse meetings → delegate to sub-agents in parallel |
| **Requirements Translator** | `requirements-translator.md` | `#boss`, `#bug`, `#task`, `#feature`, `#ux`, `#eng`, `#note`      | Route individual items to correct locations         |
| **Daily Synthesizer**       | `daily-synthesizer.md`       | `#morning`, `#lunch`, `#eod`, `#day`, `#weekly`, `#monthly`       | Generate briefs by scanning all trackers            |

### Specialized Agents (Do Specific Work)

| Agent                        | File                          | Primary Commands        | Purpose                                            |
| ---------------------------- | ----------------------------- | ----------------------- | -------------------------------------------------- |
| **Boss Tracker**             | `boss-tracker.md`             | `#boss`                 | Track boss requests with SLAs, never let them slip |
| **Bug Chaser**               | `bug-chaser.md`               | `#bug`, `#bug critical` | Track bugs with SLA-based follow-up                |
| **Engineering Collaborator** | `engineering-collaborator.md` | `#eng`, `#eng spike`    | Bridge PM ↔ Engineering                            |
| **UX Collaborator**          | `ux-collaborator.md`          | `#ux`, `#ux mockup`     | Bridge PM ↔ UX/Design                              |
| **Stakeholder Manager**      | `stakeholder-manager.md`      | `#stakeholder`          | Proactive stakeholder communication                |
| **Strategy Synthesizer**     | `strategy-synthesizer.md`     | `#strategy`             | Surface patterns, identify opportunities           |
| **Weekly Synthesizer**       | `weekly-synthesizer.md`       | `#weekly`, `#monthly`   | Weekly/monthly rollups                             |

---

## 🎯 Command Quick Reference

### Capture Commands

| Command           | Routes To                   | Agent                    |
| ----------------- | --------------------------- | ------------------------ |
| `#boss [text]`    | 5. Trackers/critical/boss-requests.md   | Boss Tracker             |
| `#bug [text]`     | 5. Trackers/bugs/bugs-master.md         | Bug Chaser               |
| `#task [text]`    | 5. Trackers/projects/                   | Requirements Translator  |
| `#feature [text]` | 5. Trackers/feedback/feature-requests/  | Requirements Translator  |
| `#ux [text]`      | 5. Trackers/people/ux-tasks.md          | UX Collaborator          |
| `#eng [text]`     | 5. Trackers/people/engineering-items.md | Engineering Collaborator |
| `#note [text]`    | \system/inbox/notes/              | Requirements Translator  |

### Meeting/Transcript Commands

| Command           | Use For                | Agent               |
| ----------------- | ---------------------- | ------------------- |
| `#transcript`     | Paste call transcripts | Meeting Synthesizer |
| `#meeting`        | Paste meeting notes    | Meeting Synthesizer |
| `#notes`          | Raw notes dump         | Meeting Synthesizer |
| `#call [subject]` | Quick call capture     | Meeting Synthesizer |
| `#1on1 [person]`  | 1:1 meeting notes      | Meeting Synthesizer |
| `#standup`        | Standup notes          | Meeting Synthesizer |

### Brief Commands

| Command    | What It Generates                        | Agent              |
| ---------- | ---------------------------------------- | ------------------ |
| `#morning` | Morning brief (critical + calendar)      | Daily Synthesizer  |
| `#lunch`   | Midday brief (progress + afternoon)      | Daily Synthesizer  |
| `#eod`     | End of day (wrap-up + tomorrow)          | Daily Synthesizer  |
| `#day`     | On-demand brief (adapts to current time) | Daily Synthesizer  |
| `#weekly`  | Weekly summary                           | Weekly Synthesizer |
| `#monthly` | Monthly rollup                           | Weekly Synthesizer |

### Strategy Commands

| Command           | What It Does        | Agent                |
| ----------------- | ------------------- | -------------------- |
| `#strategy`       | Full synthesis      | Strategy Synthesizer |
| `#strategy pulse` | Quick pattern check | Strategy Synthesizer |

---

## 📂 Folder Structure Reference

```
beats-pm-antigravity-brain/
├── docs/agents.md              ← YOU ARE HERE (agent index)
├── SETTINGS.md            ← User configuration
├── START-HERE-FTUE.md     ← First-time setup wizard
│
├── system/agents/               ← Agent prompt files
│   ├── meeting-synthesizer.md   ← ORCHESTRATOR
│   ├── requirements-translator.md ← ORCHESTRATOR
│   ├── daily-synthesizer.md     ← ORCHESTRATOR
│   ├── boss-tracker.md
│   ├── bug-chaser.md
│   ├── engineering-collaborator.md
│   ├── ux-collaborator.md
│   ├── stakeholder-manager.md
│   ├── strategy-synthesizer.md
│   └── weekly-synthesizer.md
│
├── system/inbox/                ← Drop zone for raw input
├── system/queue/                ← Items needing user input
├── 5. Trackers/critical/              ← Boss requests, escalations
├── 5. Trackers/bugs/                  ← Bug tracking
├── 5. Trackers/feedback/              ← Feature requests
├── 5. Trackers/people/                ← Stakeholders, team tasks
├── 5. Trackers/projects/              ← Active projects
├── 5. Trackers/strategy/              ← Opportunities, decisions
├── vault/meetings/              ← Briefs, meeting notes
└── TEMPLATES/             ← Reusable templates
```

---

## 🔄 Agent Interaction Patterns

### Pattern 1: Direct Command

User types `#boss get me Q1 metrics` → Boss Tracker creates entry directly

### Pattern 2: Orchestrated Parallel

User pastes `#transcript [meeting notes]` → Meeting Synthesizer fans out:

- Boss Tracker (if boss items found)
- Bug Chaser (if bugs mentioned)
- Engineering Collaborator (if technical items)
- UX Collaborator (if design items)
- All execute **in parallel**

### Pattern 3: Synthesis/Scan

User types `#morning` → Daily Synthesizer scans all trackers → generates brief

### Pattern 4: Strategy Roll-up

User types `#strategy` → Strategy Synthesizer pulls from all sources → identifies patterns

---

## ⚡ Efficiency Tips for Antigravity

1. **Parallel by default**: When Meeting Synthesizer delegates, run all sub-agents simultaneously
2. **Read SETTINGS.md first** for user preferences (boss name, team, timezone)
3. **Confirm before bulk actions**: When creating multiple items, show summary first
4. **Link items**: When creating related items, cross-reference their IDs
5. **Use templates**: Reference TEMPLATES/ for consistent formatting

---

_Beats PM Brain - Built for parallel AI agent execution_
