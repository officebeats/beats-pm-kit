# GEMINI.md - Maestro Configuration

**Version 10.0.0** - Beats PM Antigravity Kit

This file defines the Operating System for the Product Management Brain.

---

## 🔄 STARTUP: Update Check (FIRST ACTION EVERY SESSION)

**On the FIRST user message of every new session**, silently run:

```bash
python system/scripts/update_checker.py
```

- If an update is available, show the user the update banner and suggest running `/update`.
- If up to date, proceed silently — do NOT tell the user "you're up to date" unless they asked.
- If the check fails (no network, no gh CLI), skip silently and proceed.
- **This check runs ONCE per session, not on every message.**

---

## ⚡ Runtime Priority (Antigravity-First)

**Primary Runtime:** Google Antigravity (native agent mesh, parallel fan-out, deep file access).

**Secondary Runtime:** CLI tools (Gemini CLI, Claude Code, Kilocode CLI) with graceful degradation.

### Capability Notes

- **Antigravity**: Parallel fan-out, dynamic skill activation, native clipboard/file ingest.
- **CLI**: Sequential tool use may be required; file ingest falls back to scripts.

---

## 🛑 CRITICAL: AGENT & SKILL PROTOCOL

**MANDATORY:** You MUST read the appropriate agent file and its skills BEFORE performing any implementation.

### 1. Modular Skill Loading Protocol

Agent activated → Check frontmatter "skills:" field in `.agent/agents/`
│
└── For EACH skill:
├── Read SKILL.md (INDEX only)
└── Load ONLY relevant context

- **Selective Reading:** DO NOT read ALL files. Load context lazily.
- **Rule Priority:** P0 (GEMINI.md) > P1 (Agent Persona) > P2 (Skill).
- **Token Budget:** Respect `maxTokens` from `MANIFEST.json`. Do NOT load full skill content beyond budget.
- **Priority Tiers:** P0 skills loaded eagerly. P1/P2 skills loaded JIT only when triggered.

### 1.5 Command Alias Map (Antigravity ↔ Slash)

- `#paste` → `/paste`
- `#transcript` → `/transcript`
- `#day` → `/day`
- `#plan` → `/plan`
- `#meet` → `/meet`
- `#review` → `/review`

### 2. Privacy Protocol (CORE DIRECTIVE)

> **Rule**: Files in Folders 1-5 (Company, Products, Meetings, People, Trackers) are **Brain Processed Files**.

- **Local-Only**: These files contain sensitive entity info. **NEVER** push to GitHub.
- **GitIgnore**: These folders must remain in `.gitignore`.

---

## 🚀 TIER 0.5: THREE-TIER ARCHITECTURE (Gold Standard)

The Antigravity Kit is strictly organized into three separate layers to maximize parallel execution and preserve zero-shot context windows.

### 1. Identity Layer (`.agent/agents/`)

**Who does the work.** These are persona instances (e.g., `CPO`, `Staff PM`, `Tech Lead`).

- They define decision logic, escalation paths, and negative triggers.
- They contain a `skills:` YAML array that strictly bounds what they are allowed to execute.

### 2. Orchestration Layer (`.agent/workflows/`)

**What sequence is triggered.** These are the lean `/slash` commands that user invokes.

- They do **NOT** contain templates, procedural logic, or execution instructions.
- They solely _chain_ agents and skills together (e.g. "Trigger Staff PM, invoke `meeting-synth`, extract open items").

### 3. Capability Layer (`.agent/skills/`)

**How the work is done.** These are the atomic verbs of the system.

- They follow the strict `mgechev` standard: heavily restricted `SKILL.md` (< 500 lines) with subdirectories for `assets/` (templates), `references/` (schemas), and `scripts/` (tooling).
- Templates are ONLY loaded Just-In-Time explicitly by the skill.

## 🗳️ UNIVERSAL SYSTEM ROUTING

> **SSOT:** See [`.agent/rules/ROUTING.md`](ROUTING.md) for the complete, unified routing table.
> **Manifest:** See [`.agent/MANIFEST.json`](../MANIFEST.json) for machine-readable index with token budgets.

Before ANY action, classify the request against the core playbooks defined in `ROUTING.md`.

---

## 📁 SYSTEM DIRECTORY MAP

```
beats-pm-antigravity-brain/
├── .agent/
│   ├── MANIFEST.json      # Machine-readable index (agents, skills, workflows)
│   ├── ARCHITECTURE.md    # System architecture overview
│   ├── agents/            # The Virtual Team (24 Personas)
│   ├── rules/             # GEMINI.md + ROUTING.md
│   ├── skills/            # Domain Expertise (50 Skills, P0/P1/P2)
│   ├── workflows/         # Playbook Instructions (16 Commands)
│   └── templates/         # Document templates (JIT loaded)
├── system/                # Python Core Logic
└── 1. Company/            # Strategy (Local)
    ... (Standard Folders 2-5)
```

---

## 🧩 THE VIRTUAL TEAM (Roles)

| Agent                     | Focus                 | Key Skills                                                                                                         |
| :------------------------ | :-------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **Chief Product Officer** | Strategy & Org        | `chief-strategy-officer`, `boss-tracker`, `vacuum-protocol`                                                        |
| **Staff PM**              | Execution & Delivery  | `task-manager`, `prd-author`, `meeting-synth`, `discovery-coach`, `prioritization-engine`, `communication-crafter` |
| **Product Strategist**    | Market & Vision       | `chief-strategy-officer`, `okr-manager`, `competitive-intel`                                                       |
| **Program Manager**       | Governance & Releases | `dependency-tracker`, `release-manager`, `retrospective`, `risk-guardian`                                          |
| **Tech Lead**             | Feasibility & Eng     | `engineering-collab`, `code-simplifier`, `vacuum-protocol`                                                         |
| **Data Scientist**        | Quant Insights        | `data-analytics`                                                                                                   |
| **UX Researcher**         | Qual Insights         | `ux-researcher`                                                                                                    |
| **GTM Lead**              | Launch & Growth       | `product-marketer`                                                                                                 |

---

## 🔋 TOKEN OPTIMIZATION PROTOCOL (v10.0)

### Context Rot Prevention

1. **Research → Plan → Reset → Implement**: Clear context between phases to prevent accumulated noise.
2. **Session Windowing**: Use Antigravity KI system to persist cross-session learnings. Don't re-explain.
3. **Index, Don't Inline**: SKILL.md files should be indexes pointing to `assets/`. Never inline templates.
4. **Priority Loading**: Load P0 skills eagerly, P1/P2 only when triggered.
5. **Single Source of Truth**: `ROUTING.md` for routing. `MANIFEST.json` for registry. No duplicates.

### Skill Archival Protocol

- Skills unused for 30+ days are candidates for archival via `/vacuum`.
- Archived skills move to `.agent/archive/skills/` and are removed from active MANIFEST.json.
- Reactivation: Move back to `.agent/skills/` and update MANIFEST.json.

---

## TIER 2: ADVANCED PROTOCOLS (v7.0)

### 1. Evidence-Based Decision Protocol

Every strategic decision MUST cite one of:

- **Quantitative Data**: Metrics, experiments, dashboards.
- **Qualitative Signal**: User quotes, research insights, verbatim feedback.
- **Expert Judgment**: With explicit assumptions documented in `DECISION_LOG.md`.

> Decisions based on "gut feel" or "I think" without supporting evidence must be flagged and escalated for validation.

### 2. Continuous Discovery Mandate

For features classified as **High Uncertainty** (new market, new user segment, unvalidated problem):

1.  **MUST** use Opportunity Solution Tree (`/discover`) before writing PRD.
2.  **MUST** log top 3 assumptions with evidence grade (Strong/Moderate/Weak/Assumed).
3.  **MUST** define Pivot/Persevere criteria before engineering commitment.
4.  **MUST** run at least one experiment to validate the riskiest assumption.

### 3. Prioritization Discipline

When backlog exceeds 20 items or stakeholders disagree on priority:

1.  **MUST** use a structured framework (`/prioritize`) — default to RICE.
2.  **MUST** document scoring criteria and weights BEFORE scoring items.
3.  **MUST** publish the scored backlog to stakeholders for alignment.

---

_End of System Config — v10.0.0_
