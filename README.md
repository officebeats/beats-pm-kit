<div align="center">

<!-- HERO BANNER -->

<img src="system/docs/assets/hero-banner.png" alt="Beats PM Kit - Codex-first AI operating system for product managers" width="100%"/>

<br/>

# 🧠 Beats PM Kit

### **A Codex-first AI operating system for product managers**

<p><strong>Stop drowning in noise. Paste anything. Get structured PRDs, roadmaps, and tasks. Local-first repo storage, runtime-neutral state.</strong></p>

<!-- BADGES -->

<p>
  <img src="https://img.shields.io/badge/Optimized%20for-Codex-00A651?style=for-the-badge&logo=openai&logoColor=white&labelColor=1a1a2e" alt="Optimized for Codex"/>
  &nbsp;
  <a href="https://github.com/officebeats/beats-pm-kit/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-kit?style=for-the-badge&logo=github&labelColor=1a1a2e&color=E6B422" alt="GitHub Stars"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Runtime-State_Neutral-4285F4?style=for-the-badge&labelColor=1a1a2e" alt="Runtime-neutral state"/>
</p>

<!-- VALUE PROP PILLS -->

<p>
  <img src="https://img.shields.io/badge/Execution-62_PM_Skills-00A651?style=flat-square" alt="62 PM Skills"/>
   • 
  <img src="https://img.shields.io/badge/Privacy-Local_First_Storage-00A651?style=flat-square" alt="Local-first storage"/>
   • 
  <img src="https://img.shields.io/badge/Exec_Layer-The_Boss_Protocol-00A651?style=flat-square" alt="The Boss Protocol"/>
   • 
  <img src="https://img.shields.io/badge/Agents-22_Personas-00A651?style=flat-square" alt="22 Agents"/>
</p>

<br/>

<p>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/🚀_Get_Started-Install_in_60_seconds-00A651?style=for-the-badge" alt="Get Started as a Product Manager"/></a>
</p>

</div>

---

## 🎯 The Problem

Product managers drown in context — meeting notes, Slack threads, stakeholder requests, competing priorities. Every day you context-switch between 6+ tools and lose critical signal in the noise. There's no system that captures the chaos and surfaces what actually matters. **So I built one.**

## 🏗️ Architecture at a Glance

A **multi-agent AI system** with 22 specialized personas orchestrating 62 public PM skills across 5 supported runtimes. Codex is the optimized default, while one source of truth (`.agent/`) keeps the state and playbooks portable.

```
User Input → Context Guard → Agent Router → Skill Loader (JIT) → Structured Output
                                  ↓
                        22 Persona Agents
                     (Strategy · Execution · GTM · Research · Engineering)
                                  ↓
                          62 PM Skills (P0/P1/P2 tiered)
                     (PRDs · Roadmaps · Meeting Synth · Task Tracking)
```

## 💡 Why This Approach

| Decision | Rationale |
|:---|:---|
| **Agents over prompts** | Personas create consistent, role-scoped behavior that individual prompts can't. A "Staff PM" agent thinks differently than a "GTM Lead." |
| **Skills as functions** | 62 modular public skills (P0/P1/P2 tiered) allow JIT loading — only load what you need to manage token budgets. |
| **Codex-first, runtime-neutral** | Codex gets the optimized adapter path, while Antigravity, Gemini CLI, Claude Code, and KiloCode reuse the same `.agent/` source of truth. |
| **Local-first privacy** | Repo storage stays local by default. Your selected AI runtime or model provider may still process prompts, tool outputs, and attachments. |

## ⚖️ Tradeoffs I Made

| Decision | Tradeoff |
|:---|:---|
| Single `.agent/` source of truth | Simpler sync across runtimes, but every adapter must respect the same contract |
| 3-skill ceiling per request | Controls cost/latency, but limits complex multi-step operations in a single turn |
| Codex-first orchestration | Best current path for file edits, local verification, skills, subagents, and CI; Antigravity remains a compatibility path |
| Slash commands as playbook triggers | Deterministic workflows, but adds a learning curve vs. pure natural language |

## 🔄 What I'd Improve Next

- **Automated eval harness** — Measure agent output quality across runtimes with standardized scoring rubrics
- **Cost dashboard** — Token spend tracking per skill/agent to optimize the 3-skill ceiling budget
- **RAG over meeting history** — Cross-session memory via retrieval-augmented generation for better context recall
- **Agent quality benchmarks** — Comparative testing across model providers (Gemini vs Claude vs GPT) per skill category

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/officebeats/beats-pm-kit
cd beats-pm-kit
chmod +x install.sh && ./install.sh
```

That's it. The installer creates your folder structure, detects your AI runtime, fixes symlinks, installs and syncs the Dotcontext headless dependency, and runs a health check. Takes ~10 seconds.

> **Requires:** Python 3.8+ (pre-installed on macOS/most Linux). No `pip install`, no `npm`, no Docker.
> **Note:** The system uses **Dotcontext** as a mandatory, headless dependency. The setup process and any future repository updates will automatically ensure Dotcontext is installed, synced, and initialized to maintain a consistent AI operating environment.

---

### 2. Launch Your Runtime

Open the `beats-pm-kit` folder in any of these AI coding tools. **All are CLIs unless noted.**

| Runtime | Launch Command | Capabilities |
|:--------|:---------------|:-------------|
| **[OpenAI Codex](https://github.com/openai/codex)** (CLI/Desktop) | `codex` | ⭐ Primary — file edits, verification, project skills, subagents, Codex Action |
| **[Google Antigravity](https://antigravity.google/)** (Desktop IDE) | Open folder in Antigravity | Compatibility — parallel fan-out, MCP tools, browser agent |
| **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** (CLI) | `gemini` | File access, web search, tool use |
| **[Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)** (CLI) | `claude` | File access, subagents, tool use |
| **[KiloCode](https://kilocode.ai/)** (CLI) | `kilo` | File access, tool use |

> **Which should I use?** Use Codex by default. Antigravity remains supported when you want its IDE surface, but the kit no longer depends on Antigravity as the canonical runtime.
> **Codex note:** Codex uses `AGENTS.md` as the primary adapter, `CODEX_COMMANDS.md` for explicit slash-command routing, project-scoped `.codex/agents/*.toml`, promoted local skills for high-frequency Beats commands, and repo git hooks plus CI to keep adapters synchronized. See [system/docs/codex.md](system/docs/codex.md).

---

### 3. First-Time Setup (The `/start` Wizard)

On your **first session**, the kit auto-detects it's a fresh install and walks you through a 2-minute setup:

```
You open your CLI → Kit detects no .initialized file → Runs /start automatically
```

The wizard asks 3 questions:
1. **Your name** — for task ownership and doc headers
2. **Your manager** — seeds the Boss Protocol for 1:1 prep
3. **Your product focus** — configures your strategic context

Then it shows you the **6 core commands** and you're ready to go.

> **Skip the wizard?** Type `/help` instead to jump straight to the command reference.
> **Re-run it later?** Type `/start` anytime.

---

## 🌪️ Why Product Managers Need This

**Product Management is broken.**
Your day is fragmented across Slack threads, Zoom transcripts, Jira tickets, and stakeholder emails. Context is constantly lost.

This kit is an **Agentic Operating System** built specifically for Product Managers. It now uses **OpenAI Codex** as the optimized default for local repo work, verification, project-scoped skills, and optional CI automation.

- **The Black Hole Inbox:** Copy anything to your clipboard. Type `/paste`. Watch the AI extract tasks/bugs and route them to the proper tracker.
- **The Meeting Synthesizer:** Type `/meet`. The AI reads your transcripts, extracts action items, and generates structured notes.
- **The "Boss Protocol":** Type `/boss`. The system cross-references your active tasks with your boss's recent requests, flags stale workstreams, and drafts your 1:1 talking points.

### 🔒 Local-first storage and privacy boundaries

| Your Data           | Where It Lives                   | Repo Storage |
| :------------------ | :------------------------------- | :----------- |
| Company strategy    | `1. Company/` on your machine  | Ignored by git |
| PRDs & specs        | `2. Products/` on your machine | Ignored by git |
| Meeting transcripts | `3. Meetings/` on your machine | Ignored by git |
| Task trackers       | `5. Trackers/` on your machine | Ignored by git |

Folders 1-5 are `.gitignored` by default. The repo is local-first for storage, while your chosen AI runtime or connector may still process the prompts, files, or tool outputs you ask it to handle.

---

## 🧬 Inside the Engine: Three-Tier Architecture

### 🤖 1. The Virtual PM Team (22 Persona Agents)

The _Identity_ layer. Who is doing the work?

| Agent                     | Focus                 | Key Skills                                                  |
| :------------------------ | :-------------------- | :---------------------------------------------------------- |
| **Chief Product Officer** | Strategy & Org        | `chief-strategy-officer`, `boss-tracker`, `vacuum-protocol` |
| **Staff PM**              | Execution & Delivery  | `task-manager`, `prd-author`, `meeting-synth`               |
| **Product Strategist**    | Market & Vision       | `chief-strategy-officer`, `okr-manager`                     |
| **Program Manager**       | Governance & Releases | `dependency-tracker`, `retrospective`, `risk-guardian`       |
| **Tech Lead**             | Feasibility & Eng     | Engineering interface for PM decisions                       |
| **Data Scientist**        | Quant Insights        | `data-analytics`, metrics & funnels                          |
| **UX Researcher**         | Qual Insights         | `ux-research-suite`, journey maps                            |
| **GTM Lead**              | Launch & Growth       | `product-marketer`, `growth-engine`                          |
| **QA Engineer**           | Quality Assurance     | `test-scenarios`, `bug-chaser`                               |
| **Career Coach**          | PM Career Growth      | `leadership-career-coach`                                    |
| **Doc Writer**            | PRDs & Specs          | `prd-author`, `document-exporter`                            |
| **Orchestrator**          | Multi-agent Coord     | Routes to all agents above                                   |
| **Architect**             | System Architecture   | `engineering-planner`                                       |
| **Code Reviewer**         | Code Quality          | `engineering-collab`                                        |
| **Critic**                | Plan & Spec Validation| `engineering-planner`                                       |
| **Debugger**              | Issue Resolution      | `code-simplifier`                                           |
| **Designer**              | Multimodal Design     | `ui-ux-designer`                                            |
| **Executor**              | Code Implementation   | `autopilot`, `team-orchestrator`                            |
| **Planner**               | Task Graphs           | `engineering-planner`, `team-orchestrator`                  |
| **Security Reviewer**     | Vulnerability Audit   | `risk-guardian`                                             |
| **Switchboard**           | Cross-IDE Comm        | Workflow routing and agent-to-agent messaging               |

### 🎯 2. The Core Playbooks (40 Slash Workflows)

The _Routing_ layer. Lean slash commands that trigger complex operations through `CODEX_COMMANDS.md` and `.agent/workflows/`.

> **💡 Natural Conversation vs Commands:** You are **not required** to use slash commands. If you just talk to the AI naturally (e.g., "Summarize this meeting" or "Help me plan my day"), the system will organically load the correct Agents and Skills. The `/commands` are simply explicit playbook shortcuts to guarantee a highly specific logic sequence (like the exact 7 steps of `/meet`). Both methods seamlessly pull from the same `.agent/` architecture.

| Command        | Purpose                                  |
| :------------- | :--------------------------------------- |
| `/accuracy`    | High accuracy mode with self-review      |
| `/archive`     | Query or search the plan archive         |
| `/boss`        | The 1:1 "Managing Up" Prep               |
| `/build`       | Handoff PRD to Engineering Agents        |
| `/challenge`   | Internal adversarial review workflow     |
| `/chat`        | Activate chat consultation workflow      |
| `/create`      | Generate PRDs, Specs, and One-Pagers     |
| `/day`         | Daily briefing & planning                |
| `/discover`    | Build Opportunity Solution Trees         |
| `/export`      | Export current conversation to archive   |
| `/fan-out`     | Parallel multi-agent dispatch            |
| `/handoff`     | Delegate tasks to external agents        |
| `/handoff-chat`| Clipboard/chat delegation workflow       |
| `/handoff-lead`| One-shot lead execution workflow         |
| `/handoff-relay`| Execute-now, stage-rest relay workflow  |
| `/help`        | User manual & system docs                |
| `/improve-plan`| Deep planning, dependency checks, review |
| `/intel`       | Competitive intel and context capture    |
| `/interview`   | Socratic deep interview on requirements  |
| `/meet`        | Transcript → structured action items     |
| `/office-cli`  | Manage Office 365 integrations           |
| `/paste`       | Clipboard → structured intake            |
| `/plan`        | Strategic roadmaps & OKRs                |
| `/prep`        | Interview prep, research & roleplay      |
| `/prioritize`  | Backlog scoring via RICE / Kano / MoSCoW |
| `/quill`       | 5-meeting compact rollup w/ action items |
| `/regression`  | Full CI tests on the kit                 |
| `/retro`       | Sprint / PI retrospective                |
| `/review`      | Doc / Spec / Code quality control        |
| `/sprint`      | Sprint backlog generation                |
| `/start`       | Interactive First-Time Setup Wizard      |
| `/team`        | Coordinated multi-agent execution        |
| `/teams`       | Teams chat ingestion and sync            |
| `/track`       | Battlefield View of Tasks & Bugs         |
| `/transcript`  | Process all meetings from last 10 days   |
| `/trello`      | Synchronize tasks with Trello board      |
| `/update`      | Pull latest kit version from GitHub      |
| `/vacuum`      | System optimization & cleanup            |
| `/vibe`        | System health and diagnostics            |
| `/week`        | Weekly briefing & recap                  |

### 🚀 3. The Capability Engine (62 Public PM Skills)

The _Execution_ layer. Skills are loaded Just-In-Time to keep the context window fast.

| Category | Skills |
| :--- | :--- |
| **Strategy** | `chief-strategy-officer`, `business-strategy-suite`, `product-strategy-suite`, `positioning-strategist`, `company-profiler` |
| **Discovery** | `discovery-engine`, `assumption-mapper`, `brainstorming-engine`, `epic-hypothesis`, `customer-interview-suite`, `deep-interview` |
| **Execution** | `task-manager`, `prd-author`, `agile-story-crafter`, `epic-breakdown-advisor`, `requirements-translator`, `wwas`, `autopilot`, `team-orchestrator`, `engineering-planner` |
| **Roadmapping** | `roadmapping-suite`, `risk-guardian`, `dependency-tracker`, `ab-test-analysis` |
| **Metrics** | `data-analytics`, `metrics-finance-suite`, `growth-engine` |
| **Research** | `ux-research-suite`, `ui-ux-designer` |
| **GTM** | `product-marketer`, `launch-strategy`, `positioning-strategist` |
| **Meetings** | `meeting-synth`, `daily-synth`, `weekly-synth`, `boss-tracker`, `outlook-navigator` |
| **Communication** | `comms-crafter-suite`, `stakeholder-management-suite`, `document-exporter` |
| **System** | `core-utility`, `vacuum-protocol`, `context-retriever`, `inbox-processor`, `memory-consolidator`, `cross-model-bridge` |
| **Growth** | `leadership-career-coach`, `ai-shaped-readiness-advisor`, `context-engineering-advisor` |

---

## 📁 Directory Topology

```
beats-pm-kit/
├── 0. Incoming/           # The Drop Zone (Raw Notes, Screenshots)
├── 1. Company/            # Strategy & Profiles
├── 2. Products/           # PRDs, Specs, Epics
├── 3. Meetings/           # Transcripts & Summaries
├── 4. People/             # Stakeholders & CRM
├── 5. Trackers/           # Task Master Ledgers
│
├── .agent/                # ⭐ SOURCE OF TRUTH (The AI Engine)
│   ├── agents/            # 22 Virtual PM Team Personas
│   ├── rules/             # GEMINI.md (System Constitution)
│   ├── skills/            # 62 public PM Skills (P0/P1/P2 tiers)
│   ├── templates/         # Document & Report Templates
│   ├── workflows/         # 40 Slash Workflows
│   ├── archive/           # Archived agents & skills (recoverable)
│   └── MANIFEST.json      # Machine-readable index with token budgets
│
├── system/                # Python Core Logic
│   ├── scripts/           # Agent dispatcher, setup, vacuum, health check
│   └── tests/             # Test suites
│
├── AGENTS.md              # Codex adapter (generated locally)
├── CODEX_COMMANDS.md      # Codex slash-command index
├── GEMINI.md              # Runtime-neutral source config
└── README.md              # ← You are here
```

---

## 🖥️ Runtime Compatibility

Built on a **single source of truth** (`.agent/`) with Codex as the optimized runtime and compatibility adapters for other tools.

| Capability | Codex (CLI/Desktop) | Antigravity (Desktop IDE) | Gemini (CLI) | Claude Code (CLI) | KiloCode (CLI) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Project custom agents** | ✅ `.codex/agents/*.toml` | ❌ | ❌ | ⚠️ Runtime-specific | ❌ |
| **Agent Personas (22)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Public Skills (62)** | ✅ JIT load | ✅ | ✅ | ✅ | ✅ |
| **Slash Workflows (40)** | ✅ `/command` | ✅ `/command` | ✅ `#command` | ✅ `/command` | ✅ `/command` |
| **Promoted Codex skills (22)** | ✅ Native | ❌ | ❌ | ❌ | ❌ |
| **Parallel Fan-Out** | ✅ Subagents when explicitly requested | ✅ Native | ❌ Sequential | ⚠️ Runtime-specific | ❌ Sequential |
| **Context Guard** | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Codex Operating Model:** Use `AGENTS.md` for the inventory, `CODEX_COMMANDS.md` for slash routing, `.codex/agents/*.toml` for project-scoped subagent roles, and `.agent/workflows/<command>.md` plus the minimum required `SKILL.md` files for each task.

### 🔌 Power User Tools

For advanced users who want to supercharge their workflow:

| Tool | Description |
|:---|:---|
| **[OpenCLI](https://github.com/jackwener/opencli)** | Universal CLI hub for AI agents. Transform any website, Electron app, or local binary into scriptable CLI commands. Reuses browser login session and auto-generates adapters. |
| **[Horizon](https://github.com/peters/horizon)** | GPU-accelerated spatial terminal observatory. Manage terminals, AI agents, and dev tools on an infinite canvas with Claude Code integration and git status monitoring. |

---

## 🚀 Compatibility Enhancements

These optional tools remain useful for Antigravity users. They are compatibility add-ons, not required for the Codex-first path.

| Extension | Description | Install |
|:---|:---|:---:|
| **[Antigravity Cockpit](https://open-vsx.org/vscode/item?itemName=jlcodes.antigravity-cockpit)** | Premium dashboard-style quota monitor for Antigravity AI — track usage, limits, and spending at a glance | `jlcodes.antigravity-cockpit` |
| **[Antigravity iOS App](https://open-vsx.org/vscode/item?itemName=uladluch.antigravity-mobile-connector)** | Control Antigravity from your iPhone — send prompts, monitor generations, and manage projects on the go | `uladluch.antigravity-mobile-connector` |
| **[AG Auto Click & Scroll](https://open-vsx.org/vscode/item?itemName=zixfel.ag-auto-click-scroll)** | Auto-click Run and Allow buttons, plus auto-scroll the chat panel with a visual settings UI | `zixfel.ag-auto-click-scroll` |
| **[Pencil](https://open-vsx.org/vscode/item?itemName=highagency.pencildev)** | Design files directly in Antigravity — create, edit, and preview `.pen` design files with AI assistance | `highagency.pencildev` |
| **[Antigravity Flush](https://open-vsx.org/vscode/item?itemName=pkkkkkkkkkkkkk.antigravity-flush)** | Fix Opus model crashes by clearing context to prevent token limit truncation errors | `pkkkkkkkkkkkkk.antigravity-flush` |
| **[Antigravity Remote Control](https://open-vsx.org/vscode/item?itemName=hasugoii.antigravity-remote-control)** | Control Antigravity from your phone — 1-click tunnel, QR code, real-time chat | `hasugoii.antigravity-remote-control` |
| **[Gemini Image Editor](https://open-vsx.org/vscode/item?itemName=Zazmic.palm-api-image-editor)** | In-editor image tools — convert to WebP, resize, and remove backgrounds with Gemini | `Zazmic.palm-api-image-editor` |
| **[Antigravity Sync](https://open-vsx.org/vscode/item?itemName=samador.antigravity-settings-sync)** | Sync your Antigravity settings and extensions across machines using GitHub | `samador.antigravity-settings-sync` |
| **[Better Antigravity](https://open-vsx.org/vscode/item?itemName=kanezal.better-antigravity)** | Community-driven fixes and improvements — auto-run fix, chat rename, and more | `kanezal.better-antigravity` |
| **[Antigravity Autopilot](https://github.com/timteh/antigravity-autopilot)** | Auto-accept agent steps using OS-level accessibility (Windows UI Automation) — works when other extensions fail | `timteh.antigravity-autopilot` |

---

## 🔧 System Rules

The kit operates on a single rule file that governs all agent behavior:

| Rule File | Purpose |
| :--- | :--- |
| **`GEMINI.md`** | The system constitution — startup sequence, Context Guard (auto-fires every request), agent/skill loading protocol, privacy directives, architecture overview |

### Context Guard (Auto-Fires Every Request)

Built directly into `GEMINI.md`, these rules reduce token waste without any manual intervention:

1. **Parallel-first** — Batch independent tool calls
2. **No re-reads** — Never re-read files already viewed in session
3. **Compact responses** — Skip preamble, lead with the answer
4. **3-skill ceiling** — Max 3 skill assets per request
5. **Conversation decay** — Auto-manages context after 15+ exchanges to keep sessions fast

---

## 👨‍💻 Built by product people, for product people.

<div align="center">

**OfficeBeats**

_Product Lead_

Building the future of AI-powered product management. Stop chasing status updates. Start driving strategy.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/)
&nbsp;
[![X (Twitter)](https://img.shields.io/badge/X-Follow-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/)

⭐ **Star this repo** if it saves you 10 hours this week.

</div>
