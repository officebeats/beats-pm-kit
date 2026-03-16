# Architecture

## Three-Tier Architecture

The Antigravity Kit follows a strict separation of concerns:

```
├── .agent/
│   ├── agents/      ← Identity Layer (WHO does the work)
│   ├── workflows/   ← Orchestration Layer (WHAT sequence is triggered)
│   └── skills/      ← Capability Layer (HOW the work is done)
```

### 1. Identity Layer — Agents

Persona instances that define decision logic, escalation paths, and capabilities.

| Agent | Focus | Key Skills |
|-------|-------|-----------|
| Chief Product Officer | Strategy & Org | boss-tracker, vacuum-protocol |
| Staff PM | Execution & Delivery | task-manager, prd-author, meeting-synth |
| Product Strategist | Market & Vision | okr-manager, competitive-intel |
| Program Manager | Governance & Releases | release-manager, retrospective |
| Tech Lead | Feasibility & Eng | engineering-collab, code-simplifier |
| Data Scientist | Quant Insights | data-analytics |
| UX Researcher | Qual Insights | ux-researcher |
| GTM Lead | Launch & Growth | product-marketer |

### 2. Orchestration Layer — Workflows

Lean `/slash` commands that chain agents and skills. They do NOT contain templates or execution logic — they solely define the sequence.

### 3. Capability Layer — Skills

Atomic verbs of the system. Each skill follows the mgechev standard:
- `SKILL.md` — Instructions (< 500 lines)
- `assets/` — Templates
- `references/` — Schemas
- `scripts/` — Tooling

## Data Flow

```
User input → Workflow → Agent → Skill → Markdown output
                                  ↓
                          5. Trackers/ (persistent)
```

All data is stored as Markdown in the standard folder structure (0-5).
