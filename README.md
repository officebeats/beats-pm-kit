<div align="center">

<!-- HERO BANNER -->

<img src="system/docs/assets/hero-banner.png" alt="Beats PM Kit - AI product management toolkit for agentic product workflows" width="100%"/>

<br/>

# 🧠 Beats PM Kit

### **An open-source AI PM operating system for local-first product operations**

<p><strong>Turn meeting notes, Slack threads, stakeholder asks, tickets, and product docs into structured PRDs, roadmaps, tasks, briefs, and decisions.</strong></p>

<!-- BADGES -->

<p>
  <img src="https://img.shields.io/badge/Primary_Runtime-Antigravity-00A651?style=for-the-badge&logo=google&logoColor=white&labelColor=1a1a2e" alt="Antigravity primary runtime"/>
  &nbsp;
  <a href="https://github.com/officebeats/beats-pm-kit/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-kit?style=for-the-badge&logo=github&labelColor=1a1a2e&color=E6B422" alt="GitHub Stars"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Open_Source-AI_PM_Kit-4285F4?style=for-the-badge&labelColor=1a1a2e" alt="Open-source AI PM kit"/>
</p>

<!-- VALUE PROP PILLS -->

<p>
  <img src="https://img.shields.io/badge/Execution-63_PM_Skills-00A651?style=flat-square" alt="63 PM Skills"/>
   • 
  <img src="https://img.shields.io/badge/Workflows-39_Playbooks-00A651?style=flat-square" alt="39 workflow playbooks"/>
   • 
  <img src="https://img.shields.io/badge/Agents-22_Personas-00A651?style=flat-square" alt="22 Agents"/>
   • 
  <img src="https://img.shields.io/badge/Storage-Local_First-00A651?style=flat-square" alt="Local-first storage"/>
</p>

<br/>

<p>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Get_Started-Install_in_60_seconds-00A651?style=for-the-badge" alt="Get Started as a Product Manager"/></a>
</p>

</div>

---

## 🎯 The Problem

Product managers drown in context — meeting notes, Slack threads, stakeholder requests, competing priorities. Every day you context-switch between 6+ tools and lose critical signal in the noise. There's no system that captures the chaos and surfaces what actually matters. **So I built one.**

Beats PM Kit is an **AI product management toolkit** for PMs, product leaders, founders, and builders who want agentic product workflows without scattering strategy across disconnected tools. It is also a practical example of **vibe coding for product managers**: using AI to turn messy operating context into durable product artifacts.

## 🏗️ Architecture at a Glance

A **multi-agent AI system** with 22 specialized personas orchestrating 39 workflow playbooks and 63 PM skills across the core supported runtimes: Antigravity, Codex, Gemini CLI, Claude Code, and KiloCode. One source of truth (`.agent/`) powers all of them with a Context Guard that keeps every request focused.

```
User Input → Context Guard → Agent Router → Skill Loader (JIT) → Structured Output
                                  ↓
                        22 Persona Agents
                     (Strategy · Execution · GTM · Research · Engineering)
                                  ↓
                    39 Workflow Playbooks + 63 PM Skills
                     (PRDs · Roadmaps · Meeting Synth · Task Tracking)
```

The design goal is simple: **cross-runtime AI agents** that feel useful in real product work, while keeping the repo small enough for people to inspect, fork, and trust.

## 💡 Why This Approach

| Decision | Rationale |
|:---|:---|
| **Agents over prompts** | Personas create consistent, role-scoped behavior that individual prompts can't. A "Staff PM" agent thinks differently than a "GTM Lead." |
| **Skills as functions** | 63 modular skills (P0/P1/P2 tiered) allow JIT loading — only load what you need to manage token budgets. |
| **Runtime-agnostic** | Same `.agent/` source of truth runs on Antigravity, Codex, Gemini CLI, Claude Code, and KiloCode. Generated adapter folders stay local and ignored. |
| **Local-first privacy** | Private workspace folders stay local and gitignored by default. CI blocks PII, secrets, local runtime state, and generated adapter bloat from the public repo. |

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

The installer creates your folder structure, detects your AI runtime, fixes symlinks, syncs the Dotcontext headless dependency when needed, and runs a health check.

> **Requires:** Python 3.8+. Optional runtime integrations may use their own CLIs.
> **Note:** The system uses **Dotcontext** as a headless dependency for a consistent AI operating environment.

### 2. Launch Your Runtime

Open the `beats-pm-kit` folder in any of these AI coding tools. **All are CLIs unless noted.**

| Runtime | Launch Command | Capabilities |
|:--------|:---------------|:-------------|
| **[Google Antigravity](https://antigravity.google/)** (Desktop IDE) | Open folder in Antigravity | Primary — parallel fan-out, MCP tools, browser agent |
| **[OpenAI Codex](https://github.com/openai/codex)** (CLI) | `codex` | File access, code execution, native `AGENTS.md` adapter |
| **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** (CLI) | `gemini` | File access, web search, tool use |
| **[Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)** (CLI) | `claude` | File access, subagents, tool use |
| **[KiloCode](https://kilocode.ai/)** (CLI) | `kilo` | File access, tool use |

> **Which should I use?** If you have Antigravity, use it — the kit was designed for its parallel execution. Otherwise, any CLI above works. The kit adapts through local generated adapter folders such as `.gemini/`, `.claude/`, `.codex/`, and `.kilocode/`, which remain ignored by Git.
> **Codex note:** Codex uses `AGENTS.md` as the primary adapter, `CODEX_COMMANDS.md` for explicit slash-command routing, generated `.codex/` scaffolding for runtime notes, optional promoted local skills for the highest-frequency Beats commands, and repo git hooks plus CI to keep adapters synchronized. See [system/docs/codex.md](system/docs/codex.md).

### 3. First-Time Setup (The `/start` Wizard)

On your first session, run:

```text
/start
```

The wizard asks 3 questions:

1. **Your name** — for task ownership and doc headers
2. **Your manager** — seeds the Boss Protocol for 1:1 prep
3. **Your product focus** — configures your strategic context

Then it shows you the core commands and you are ready to go.

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

### 🔒 100% Local Repo Storage. Privacy-Aware AI Runtime Use.

| Your Data | Where It Lives | Kit Cloud Sync |
| :--- | :--- | :--- |
| Company strategy | `1. Company/` on YOUR machine | ❌ Never |
| PRDs & specs | `2. Products/` on YOUR machine | ❌ Never |
| Meeting transcripts | `3. Meetings/` on YOUR machine | ❌ Never |
| Task trackers | `5. Trackers/` on YOUR machine | ❌ Never |

Folders 1-5 are `.gitignored` by default except skeleton `.gitkeep` files. CI runs `system/scripts/privacy_guard.py --tree` so private workspace content, local runtime state, personal paths, emails, private URLs, token-like strings, and generated adapter bloat cannot be reintroduced in future PRs.

Important caveat: this repo does not sync your private PM files to a kit cloud service, but your chosen **AI runtime/model provider** may process prompts, attachments, or tool outputs according to that provider's product and account settings.

---

## 🧬 Inside the Engine: Three-Tier Architecture

### 🤖 1. The Virtual PM Team (22 Persona Agents)

The _Identity_ layer. Who is doing the work?

| Agent | Focus | Key Skills |
| :--- | :--- | :--- |
| **Chief Product Officer** | Strategy & org | `product-strategy-suite`, `boss-tracker`, `vacuum-protocol` |
| **Staff PM** | Execution & delivery | `pm-decision-router`, `task-manager`, `prd-author`, `meeting-synth` |
| **Product Strategist** | Market & vision | `pm-decision-router`, `product-strategy-suite`, `roadmapping-suite` |
| **Program Manager** | Governance & releases | `dependency-tracker`, `retrospective`, `risk-guardian` |
| **Tech Lead** | Feasibility & engineering | Engineering interface for PM decisions |
| **Data Scientist** | Quant insights | `data-analytics`, `metrics-finance-suite` |
| **UX Researcher** | Qual insights | `ux-research-suite`, journey maps |
| **GTM Lead** | Launch & growth | `product-marketer`, `growth-engine` |
| **QA Engineer** | Quality assurance | `test-scenarios`, `bug-investigation` |
| **Career Coach** | PM career growth | `leadership-career-coach` |
| **Documentation Writer** | PRDs, specs, and docs | `prd-author`, `document-exporter` |
| **SOP Librarian** | Runbooks and reusable process | `sop-manager`, `document-exporter` |
| **Orchestrator** | Multi-agent coordination | Routes to all agents above |
| **Architect** | System architecture | `engineering-planner` |
| **Code Reviewer** | Code quality | `code-review`, `risk-guardian` |
| **Critic** | Plan and spec validation | `engineering-planner`, `assumption-mapper` |
| **Debugger** | Issue resolution | `bug-investigation`, `code-review` |
| **Designer** | UX and visual systems | `ui-ux-designer` |
| **Executor** | Code implementation | `autopilot`, `team-orchestrator` |
| **Planner** | Task graphs and sequencing | `engineering-planner`, `team-orchestrator` |
| **Security Reviewer** | Privacy and trust boundaries | `security-audit`, `risk-guardian` |
| **Switchboard** | Cross-IDE routing | Runtime routing and workflow dispatch |

### 🎯 2. The Core Playbooks (39 workflow playbooks)

The _Routing_ layer. Lean slash commands that trigger repeatable product operations.

> **Natural conversation vs commands:** You are not required to use slash commands. If you just talk to the AI naturally, the system can load the right agents and skills. Slash commands are explicit playbook shortcuts when you want deterministic behavior.

| Command | Purpose |
| :--- | :--- |
| `/accuracy` | High accuracy mode with self-review |
| `/archive` | Query or search the plan archive |
| `/beats-comms` | Scoped Slack, Teams, Outlook, and Calendar intake |
| `/beats-slack` | Scoped Slack task intake and transcript archive |
| `/beats-teams` | Scoped Teams task intake and transcript archive |
| `/boss` | The 1:1 managing-up prep workflow |
| `/build` | Handoff PRD to engineering agents |
| `/challenge` | Internal adversarial review workflow |
| `/chat` | Activate chat consultation workflow |
| `/create` | Generate PRDs, specs, and one-pagers |
| `/day` | Daily briefing and planning |
| `/deck` | Generate deck briefs and presentation outputs |
| `/discover` | Build Opportunity Solution Trees |
| `/fan-out` | Parallel multi-agent dispatch |
| `/handoff` | Delegate tasks to external agents |
| `/help` | User manual and system docs |
| `/improve-plan` | Deep planning, dependency checks, and review |
| `/intel` | Competitive intel and context capture |
| `/interview` | Socratic deep interview on requirements |
| `/meet` | Transcript to structured action items |
| `/office-cli` | Manage Office 365 integrations |
| `/paste` | Clipboard to structured intake |
| `/plan` | Strategic roadmaps and OKRs |
| `/prep` | Interview prep, research, and roleplay |
| `/prioritize` | Backlog scoring via RICE, Kano, or MoSCoW |
| `/regression` | Full CI tests on the kit |
| `/retro` | Sprint or PI retrospective |
| `/review` | Doc, spec, or code quality control |
| `/sop` | Generate SOPs, runbooks, and process docs |
| `/sprint` | Sprint backlog generation |
| `/start` | Interactive first-time setup wizard |
| `/team` | Coordinated multi-agent execution |
| `/track` | Battlefield view of tasks and bugs |
| `/transcript` | Process recent meeting transcripts |
| `/trello` | Synchronize tasks with a Trello board |
| `/update` | Pull latest kit version from GitHub |
| `/vacuum` | System optimization and cleanup |
| `/vibe` | System health and diagnostics |
| `/week` | Weekly briefing and recap |

### 🚀 3. The Capability Engine (63 PM skills)

The _Execution_ layer. Skills are loaded Just-In-Time to keep the context window fast.

| Category | Skills |
| :--- | :--- |
| **Strategy** | `pm-decision-router`, `product-strategy-suite`, `roadmapping-suite`, `company-profiler` |
| **Discovery** | `discovery-engine`, `assumption-mapper`, `brainstorming-engine`, `epic-hypothesis`, `customer-interview-suite` |
| **Execution** | `task-manager`, `prd-author`, `agile-story-crafter`, `epic-breakdown-advisor`, `requirements-translator`, `wwas`, `autopilot`, `team-orchestrator`, `engineering-planner` |
| **Roadmapping** | `roadmapping-suite`, `risk-guardian`, `dependency-tracker`, `ab-test-analysis` |
| **Metrics** | `data-analytics`, `metrics-finance-suite`, `growth-engine` |
| **Research** | `ux-research-suite`, `ui-ux-designer` |
| **GTM** | `product-marketer`, `launch-strategy`, `positioning-strategist` |
| **Meetings** | `meeting-synth`, `daily-synth`, `weekly-synth`, `boss-tracker`, `outlook-navigator` |
| **Communication** | `slack-task-intake`, `teams-task-intake`, `chat-transcript-archive`, `atlassian-context-archive`, `stakeholder-management-suite` |
| **System** | `core-utility`, `vacuum-protocol`, `context-retriever`, `inbox-processor`, `memory-consolidator`, `cross-model-bridge` |
| **Growth** | `leadership-career-coach`, `ai-shaped-readiness-advisor`, `context-engineering-advisor` |

---

## 📁 Directory Topology

```text
beats-pm-kit/
├── 0. Incoming/           # The drop zone: raw notes, screenshots, uploads
├── 1. Company/            # Strategy, company context, ways of working
├── 2. Products/           # PRDs, specs, epics, product briefs
├── 3. Meetings/           # Transcripts, summaries, reports, chat archives
├── 4. People/             # Stakeholders and relationship context
├── 5. Trackers/           # Task ledgers, bugs, boss requests
│
├── .agent/                # SOURCE OF TRUTH
│   ├── agents/            # 22 persona agents
│   ├── rules/             # System rules and runtime contracts
│   ├── skills/            # 63 PM skills
│   ├── templates/         # Document, deck, and SOP templates
│   ├── workflows/         # 39 workflow playbooks
│   └── MANIFEST.json      # Machine-readable index
│
├── system/                # Python core logic
│   ├── scripts/           # Dispatcher, setup, privacy guard, adapter sync
│   └── tests/             # Release readiness and regression tests
│
├── AGENTS.md              # Thin Codex adapter
├── CODEX_COMMANDS.md      # Generated slash-command routing table
├── CLAUDE.md              # Thin Claude Code adapter
├── GEMINI.md              # Thin Antigravity/Gemini adapter
└── README.md              # You are here
```

Generated adapter directories such as `.codex/`, `.gemini/`, `.claude/`, and `.kilocode/` are intentionally not tracked. Regenerate them with:

```bash
python system/scripts/sync_cli_adapters.py
```

To verify the public feature inventory:

```bash
python system/scripts/feature_inventory.py --json
```

---

## 🖥️ Runtime Compatibility

Built on a **single source of truth** (`.agent/`) with adapters for each runtime. **Antigravity is the gold standard** because it supports native parallel fan-out.

| Capability | Antigravity (Desktop IDE) | Codex (CLI) | Gemini CLI | Claude Code | KiloCode |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Parallel Fan-Out** | ✅ Native | ❌ Sequential | ❌ Sequential | ❌ Sequential | ❌ Sequential |
| **Agent Personas (22)** | ✅ Full mesh | ✅ | ✅ | ✅ | ✅ |
| **Skills (63)** | ✅ JIT load | ✅ | ✅ | ✅ | ✅ |
| **Slash Commands (39)** | ✅ `/command` | ✅ `/command` | ✅ `#command` | ✅ `/command` | ✅ `/command` |
| **Clipboard Ingest** | ✅ Native | ⚠️ Script | ⚠️ Script | ⚠️ Script | ⚠️ Script |
| **Context Guard** | ✅ Auto | ✅ | ✅ | ✅ | ✅ |
| **Speed** | Fastest | Good | Good | Good | Good |

> **Parallel Fan-Out:** When you run `/fan-out`, Antigravity dispatches multiple specialist agents simultaneously. Other runtimes process agents sequentially, making complex workflows slower.
> **Codex Operating Model:** Use `AGENTS.md` for the inventory, then load `.agent/workflows/<command>.md` and only the required `SKILL.md` files for the task.

### 🔌 Power User Tools

For advanced users who want to supercharge their workflow:

| Tool | Description |
|:---|:---|
| **[OpenCLI](https://github.com/jackwener/opencli)** | Universal CLI hub for AI agents. Transform websites, Electron apps, or local binaries into scriptable CLI commands. |
| **[Horizon](https://github.com/peters/horizon)** | GPU-accelerated spatial terminal observatory for managing terminals, AI agents, and dev tools on an infinite canvas. |

---

## 🚀 Antigravity Enhancements

Community extensions that can improve Antigravity workflows. Install from the Extensions panel or via the [Open VSX Registry](https://open-vsx.org/).

| Extension | Description | Install |
|:---|:---|:---:|
| **[Antigravity Cockpit](https://open-vsx.org/vscode/item?itemName=jlcodes.antigravity-cockpit)** | Dashboard-style quota monitor for Antigravity AI usage, limits, and spending | `jlcodes.antigravity-cockpit` |
| **[Antigravity iOS App](https://open-vsx.org/vscode/item?itemName=uladluch.antigravity-mobile-connector)** | Control Antigravity from your iPhone, send prompts, monitor generations, and manage projects | `uladluch.antigravity-mobile-connector` |
| **[AG Auto Click & Scroll](https://open-vsx.org/vscode/item?itemName=zixfel.ag-auto-click-scroll)** | Auto-click Run and Allow buttons, plus auto-scroll the chat panel with a visual settings UI | `zixfel.ag-auto-click-scroll` |
| **[Pencil](https://open-vsx.org/vscode/item?itemName=highagency.pencildev)** | Create, edit, and preview `.pen` design files with AI assistance | `highagency.pencildev` |
| **[Antigravity Flush](https://open-vsx.org/vscode/item?itemName=pkkkkkkkkkkkkk.antigravity-flush)** | Clear context when model sessions hit token-limit issues | `pkkkkkkkkkkkkk.antigravity-flush` |
| **[Antigravity Remote Control](https://open-vsx.org/vscode/item?itemName=hasugoii.antigravity-remote-control)** | Control Antigravity from your phone with tunnel, QR, and real-time chat flows | `hasugoii.antigravity-remote-control` |
| **[Gemini Image Editor](https://open-vsx.org/vscode/item?itemName=Zazmic.palm-api-image-editor)** | In-editor image tools for WebP conversion, resizing, and background removal | `Zazmic.palm-api-image-editor` |
| **[Antigravity Sync](https://open-vsx.org/vscode/item?itemName=samador.antigravity-settings-sync)** | Sync Antigravity settings and extensions across machines using GitHub | `samador.antigravity-settings-sync` |
| **[Better Antigravity](https://open-vsx.org/vscode/item?itemName=kanezal.better-antigravity)** | Community-driven fixes such as auto-run improvements and chat rename support | `kanezal.better-antigravity` |
| **[Antigravity Autopilot](https://github.com/timteh/antigravity-autopilot)** | Auto-accept agent steps using OS-level accessibility on Windows | `timteh.antigravity-autopilot` |

---

## 🔧 System Rules

The kit operates from `.agent/` as the canonical system. Runtime-specific root files stay thin and generated where possible.

| File | Purpose |
| :--- | :--- |
| **`.agent/rules/GEMINI.md`** | System constitution, Context Guard, agent/skill loading protocol, privacy directives, architecture overview |
| **`AGENTS.md`** | Codex startup and slash-command adapter |
| **`CODEX_COMMANDS.md`** | Codex command index generated from `.agent/command-registry.json` |
| **`CLAUDE.md`** | Claude Code adapter |
| **`GEMINI.md`** | Antigravity and Gemini adapter |

### Context Guard (Auto-Fires Every Request)

The Context Guard reduces token waste without manual intervention:

1. **Parallel-first** — Batch independent tool calls
2. **No re-reads** — Avoid re-reading files already viewed in session
3. **Compact responses** — Lead with the answer
4. **3-skill ceiling** — Keep most requests within three skill assets
5. **Conversation decay** — Manage context as sessions get long

---

## 👨‍💻 Built by product people, for product people.

<div align="center">

**OfficeBeats**

Open-source AI-native product operations, agentic workflow architecture, context engineering, and privacy-aware release discipline for the community.

Built as a practical portfolio of AI-forward product management: strategy systems, cross-runtime AI agents, local-first product operations, and vibe coding for product managers.

⭐ **Star this repo** if it helps you turn messy PM context into clearer product work.

</div>
