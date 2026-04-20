<div align="center">

<!-- HERO BANNER -->

<img src="system/docs/assets/hero-banner.png" alt="Beats PM Antigravity Kit - The Ultimate AI Operating System for Product Managers" width="100%"/>

<br/>

# 🧠 Beats PM Antigravity Kit

### **The AI Operating System That Thinks Like a 10x Product Manager**

<p><strong>Stop drowning in noise. Paste anything. Get structured PRDs, roadmaps, and tasks. Zero manual tracking. 100% Local Privacy.</strong></p>

<!-- BADGES -->

<p>
  <img src="https://img.shields.io/badge/Powered%20by-Antigravity-00A651?style=for-the-badge&logo=google&logoColor=white&labelColor=1a1a2e" alt="Antigravity Framework"/>
  &nbsp;
  <a href="https://github.com/officebeats/beats-pm-kit/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-kit?style=for-the-badge&logo=github&labelColor=1a1a2e&color=E6B422" alt="GitHub Stars"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Architected_for-MAANG_Leaders-4285F4?style=for-the-badge&labelColor=1a1a2e" alt="FAANG Ready"/>
</p>

<!-- VALUE PROP PILLS -->

<p>
  <img src="https://img.shields.io/badge/🚀_Execution-52_PM_Skills-00A651?style=flat-square" alt="52 PM Skills"/>
   • 
  <img src="https://img.shields.io/badge/🔒_100%25_Local-Zero_Cloud_Storage-00A651?style=flat-square" alt="Privacy First"/>
   • 
  <img src="https://img.shields.io/badge/💼_Exec_Layer-The_Boss_Protocol-00A651?style=flat-square" alt="The Boss Protocol"/>
   • 
  <img src="https://img.shields.io/badge/🤖_Agents-20_Personas-00A651?style=flat-square" alt="20 Agents"/>
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

A **multi-agent AI system** with 20 specialized personas orchestrating 52 PM skills across 5 runtimes. One source of truth (`.agent/`) powers all of them with a Context Guard that auto-optimizes every request.

```
User Input → Context Guard → Agent Router → Skill Loader (JIT) → Structured Output
                                  ↓
                        20 Persona Agents
                     (Strategy · Execution · GTM · Research · Engineering)
                                  ↓
                          52 PM Skills (P0/P1/P2 tiered)
                     (PRDs · Roadmaps · Meeting Synth · Task Tracking)
```

## 💡 Why This Approach

| Decision | Rationale |
|:---|:---|
| **Agents over prompts** | Personas create consistent, role-scoped behavior that individual prompts can't. A "Staff PM" agent thinks differently than a "GTM Lead." |
| **Skills as functions** | 52 modular skills (P0/P1/P2 tiered) allow JIT loading — only load what you need to manage token budgets. |
| **Runtime-agnostic** | Same `.agent/` source of truth runs on Antigravity, Gemini CLI, Claude Code, Codex, and KiloCode. No vendor lock-in. |
| **Local-first privacy** | All company data stays on your machine. Zero cloud sync. Enterprise-safe from day one. |

## ⚖️ Tradeoffs I Made

| Decision | Tradeoff |
|:---|:---|
| Single `.agent/` source of truth | Simpler sync across runtimes, but every adapter must respect the same contract |
| 3-skill ceiling per request | Controls cost/latency, but limits complex multi-step operations in a single turn |
| Parallel fan-out (Antigravity only) | 3-5x faster execution, but creates runtime preference for power users |
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

That's it. The installer creates your folder structure, detects your AI runtime, fixes symlinks, and runs a health check. Takes ~10 seconds.

> **Requires:** Python 3.8+ (pre-installed on macOS/most Linux). No `pip install`, no `npm`, no Docker.

---

### 2. Launch Your Runtime

Open the `beats-pm-kit` folder in any of these AI coding tools. **All are CLIs unless noted.**

| Runtime | Launch Command | Capabilities |
|:--------|:---------------|:-------------|
| **[Google Antigravity](https://antigravity.google/)** (Desktop IDE) | Open folder in Antigravity | ⭐ Primary — parallel fan-out, MCP tools, browser agent |
| **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** (CLI) | `gemini` | File access, web search, tool use |
| **[Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)** (CLI) | `claude` | File access, subagents, tool use |
| **[OpenAI Codex](https://github.com/openai/codex)** (CLI) | `codex` | File access, code execution |
| **[KiloCode](https://kilocode.ai/)** (CLI) | `kilo` | File access, tool use |

> **Which should I use?** If you have Antigravity, use it — the kit was designed for its parallel execution. Otherwise, any CLI above works. The kit auto-adapts via adapter folders (`.gemini/`, `.claude/`, etc.).
> **Codex note:** Codex uses `AGENTS.md` as the primary adapter, `CODEX_COMMANDS.md` for explicit slash-command routing, generated `.codex/` scaffolding for runtime notes, optional promoted local skills for the highest-frequency Beats commands, and repo git hooks plus CI to keep adapters synchronized. See [system/docs/codex.md](system/docs/codex.md).

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

This kit is an **Agentic Operating System** built specifically for Product Managers. It leverages **Google Antigravity's** parallel agent execution to parse chaos into strategy.

- **The Black Hole Inbox:** Copy anything to your clipboard. Type `/paste`. Watch the AI extract tasks/bugs and route them to the proper tracker.
- **The Meeting Synthesizer:** Type `/meet`. The AI reads your transcripts, extracts action items, and generates structured notes.
- **The "Boss Protocol":** Type `/boss`. The system cross-references your active tasks with your boss's recent requests, flags stale workstreams, and drafts your 1:1 talking points.

### 🔒 100% Local. Enterprise-Grade Privacy.

| Your Data           | Where It Lives                   | Cloud Access |
| :------------------ | :------------------------------- | :----------- |
| Company strategy    | `1. Company/` on YOUR machine  | ❌ Never     |
| PRDs & specs        | `2. Products/` on YOUR machine | ❌ Never     |
| Meeting transcripts | `3. Meetings/` on YOUR machine | ❌ Never     |
| Task trackers       | `5. Trackers/` on YOUR machine | ❌ Never     |

**No cloud sync. No telemetry. No API calls with your trade secrets.**
Folders 1-5 are `.gitignored` by default. Your private data stays on your machine.

---

## 🧬 Inside the Engine: Three-Tier Architecture

### 🤖 1. The Virtual PM Team (20 Persona Agents)

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

### 🎯 2. The Core Playbooks (26 Protected Workflows)

The _Routing_ layer. Lean slash commands that trigger complex operations. All 26 are **protected core**.

> **💡 Natural Conversation vs Commands:** You are **not required** to use slash commands. If you just talk to the AI naturally (e.g., "Summarize this meeting" or "Help me plan my day"), the system will organically load the correct Agents and Skills. The `/commands` are simply explicit playbook shortcuts to guarantee a highly specific logic sequence (like the exact 7 steps of `/meet`). Both methods seamlessly pull from the same `.agent/` architecture.

| Command        | Purpose                                  |
| :------------- | :--------------------------------------- |
| `/boss`        | The 1:1 "Managing Up" Prep               |
| `/build`       | Handoff PRD to Engineering Agents        |
| `/create`      | Generate PRDs, Specs, and One-Pagers     |
| `/day`         | Daily briefing & planning                |
| `/discover`    | Build Opportunity Solution Trees         |
| `/fan-out`     | Parallel multi-agent dispatch            |
| `/help`        | User manual & system docs                |
| `/interview`   | Socratic deep interview on requirements  |
| `/meet`        | Transcript → structured action items    |
| `/paste`       | Clipboard → structured intake           |
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
| `/track`       | Battlefield View of Tasks & Bugs         |
| `/transcript`  | Process all Quill meetings from last 10 business days |
| `/update`      | Pull latest kit version from GitHub      |
| `/vacuum`      | System optimization & cleanup            |
| `/vibe`        | System health and diagnostics            |
| `/week`        | Weekly briefing & recap                  |

### 🚀 3. The Capability Engine (52 PM Skills)

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
│   ├── agents/            # 12 Virtual PM Team Personas
│   ├── rules/             # GEMINI.md (System Constitution)
│   ├── skills/            # 52 PM Skills (P0/P1/P2 tiers)
│   ├── templates/         # Document & Report Templates
│   ├── workflows/         # 17 Protected Playbooks
│   ├── archive/           # Archived agents & skills (recoverable)
│   └── MANIFEST.json      # Machine-readable index with token budgets
│
├── system/                # Python Core Logic
│   ├── scripts/           # Agent dispatcher, setup, vacuum, health check
│   └── tests/             # Test suites
│
├── GEMINI.md              # System config (v10.6.0)
└── README.md              # ← You are here
```

---

## 🖥️ Runtime Compatibility

Built on a **single source of truth** (`.agent/`) with adapters for each runtime. **Antigravity is the gold standard.**

| Capability | Antigravity (Desktop IDE) | Gemini (CLI) | Claude Code (CLI) | Codex (CLI) | KiloCode (CLI) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Parallel Fan-Out** | ✅ Native | ❌ Sequential | ❌ Sequential | ❌ Sequential | ❌ Sequential |
| **Agent Personas (12)** | ✅ Full mesh | ✅ | ✅ | ✅ | ✅ |
| **Skills (46)** | ✅ JIT load | ✅ | ✅ | ✅ | ✅ |
| **Slash Commands (18)** | ✅ `/command` | ✅ `#command` | ✅ `/command` | ✅ `/command` | ✅ `/command` |
| **Clipboard Ingest** | ✅ Native | ⚠️ Script | ⚠️ Script | ⚠️ Script | ⚠️ Script |
| **Context Guard** | ✅ Auto | ✅ | ✅ | ✅ | ✅ |
| **Speed** | ⚡ Fastest | 🟡 Good | 🟡 Good | 🟡 Good | 🟡 Good |

> **Parallel Fan-Out:** When you run `/fan-out`, Antigravity dispatches multiple specialist agents simultaneously. Other runtimes process agents sequentially, making complex workflows 3-5x slower.
> **Codex Operating Model:** Use `AGENTS.md` for the inventory, then load `.agent/workflows/<command>.md` and only the required `SKILL.md` files for the task.

### 🔌 Power User Tools

For advanced users who want to supercharge their workflow:

| Tool | Description |
|:---|:---|
| **[OpenCLI](https://github.com/jackwener/opencli)** | Universal CLI hub for AI agents. Transform any website, Electron app, or local binary into scriptable CLI commands. Reuses browser login session and auto-generates adapters. |
| **[Horizon](https://github.com/peters/horizon)** | GPU-accelerated spatial terminal observatory. Manage terminals, AI agents, and dev tools on an infinite canvas with Claude Code integration and git status monitoring. |

---

## 🚀 Antigravity Enhancements

Community extensions that supercharge your Antigravity IDE experience. Install from the Extensions panel or via the [Open VSX Registry](https://open-vsx.org/).

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

**Ernesto "Beats"**

_ex-BCG Digital Product Lead · ex-Fetch Rewards Senior Product Lead_

Building the future of AI-powered product management. Stop chasing status updates. Start driving strategy.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/productmg/)
&nbsp;
[![X (Twitter)](https://img.shields.io/badge/X-Follow-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/officebeats)

⭐ **Star this repo** if it saves you 10 hours this week.

</div>
