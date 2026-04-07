# GEMINI.md - Maestro Configuration

**Version 10.3.0** - Beats PM Antigravity Kit

This file defines the Operating System for the Product Management Brain.

---

## 🔄 STARTUP: First-Run + Health Check (FIRST ACTION EVERY SESSION)

**On the FIRST user message of every new session**, execute this sequence:

### A. First-Run Detection
Check if `.initialized` exists in the project root:
- **If `.initialized` is MISSING** → This is a fresh install. Trigger the `/start` workflow (read `.agents/workflows/start.md`) to run the interactive setup wizard. After the wizard completes, create the `.initialized` marker file.
- **If `.initialized` EXISTS** → Proceed to Step B.

### B. Health Check
Silently run:

```bash
python system/scripts/context_health.py
```

- This script checks for updates AND measures conversation health in one call.
- If an update is available, silently note it and proceed. Mention only if the user asks about system status.
- If context health returns 🔴 CRITICAL, silently optimize context. No user-facing warning.
- If up to date and healthy, proceed silently.
- **This check runs ONCE per session, not on every message.**

---

## ⚡ CONTEXT GUARD (ALWAYS ACTIVE)

These rules fire automatically on **every request** — no user action needed.

1. **Parallel-first:** Always batch independent tool calls. Never make 5 sequential calls when 3 parallel ones work.
2. **No re-reads:** Never re-read a file already viewed in this session unless the user explicitly asks or the file was modified.
3. **Compact responses:** Skip preamble. Don't restate the user's question. Lead with the answer.
4. **3-skill ceiling:** Never load more than 3 skill assets in a single request. Queue the rest.
5. **Conversation decay:** After 15+ back-and-forth exchanges, silently optimize by condensing context and prioritizing recency. No user prompt.
6. **Cloud Integrity (High-Performance):** If the workspace is on an iCloud/CloudDocs path, **MANDATORY** usage of `run_command` (`cat > filename << 'EOF' ... EOF`) for all file creations and overwrites. DO NOT use `write_to_file` as it triggers sync-locks and tool-cancellation on large blocks.

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
- `#build` → `/build`
- `#interview` → `/interview`
- `#team` → `/team`

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


---

## 🤖 MULTI-AGENT RUNTIME INTEGRATION (Gold Standard)

To ensure the BeatsPM Kit works seamlessly across different LLM agents:

1. **Universal Gateway**: Use `python3 system/scripts/beats.py {command}` for all /slash logic.
2. **Runtime Specifics**:
   - **Antigravity**: Eagerly use parallel tool calls and `mcp-pencil` for UI tasks.
   - **Codex (CLI/Desktop)**: Prioritize direct script execution in `system/scripts/`.
   - **Claude Code**: Prioritize XML-structured status reports and `beats.py` for task mgmt.
3. **Shared Context**: All runtimes MUST read `5. Trackers/STATUS.md` and `STRATEGIC_INSIGHTS.md` before starting.

---

## 📁 SYSTEM DIRECTORY MAP

```
beats-pm-antigravity-brain/
├── .agent/
│   ├── MANIFEST.json      # Machine-readable index (agents, skills, workflows)
│   ├── ARCHITECTURE.md    # System architecture overview
│   ├── agents/            # The Virtual Team (12 PM Personas)
│   ├── rules/             # GEMINI.md (System Constitution)
│   ├── skills/            # Domain Expertise (46 Skills, P0/P1/P2)
│   ├── workflows/         # Playbook Instructions (17 Commands)
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
| **QA Engineer**           | Quality Assurance     | `test-scenarios`, `bug-chaser`                                                                                     |
| **Career Coach**          | PM Career Growth      | `leadership-career-coach`                                                                                          |
| **Doc Writer**            | PRDs & Specs          | `prd-author`, `document-exporter`                                                                                  |
| **Orchestrator**          | Multi-agent Coord     | Routes to all agents above                                                                                         |
| **Architect**             | System Architecture   | `engineering-planner`                                                                                              |
| **Critic**                | Plan & Spec Validation| `engineering-planner`                                                                                              |
| **Executor**              | Code Implementation   | `autopilot`, `team-orchestrator`                                                                                   |
| **Planner**               | Task Graphs           | `engineering-planner`, `team-orchestrator`                                                                         |

---

## 🔋 TOKEN OPTIMIZATION & ADVANCED PROTOCOLS

> **Key rules:** Index, Don't Inline. P0 eager, P1/P2 JIT. Research→Plan→Reset→Implement.
> **Full protocols:** Load `.agent/rules/assets/advanced-protocols.md` JIT when performing strategic decisions, discovery, or prioritization work.

---

_End of System Config — v10.0.1_
