<div align="center">

<img src="system/docs/assets/hero-banner.png" alt="Beats PM Kit - AI product management operating system for local-first PM task management" width="100%"/>

<br/>

# Beats PM Kit: AI Product Management Operating System

### Local-first product operations for AI-forward product managers

<p><strong>Beats PM Kit is an open-source AI product management toolkit for turning meetings, Slack and Teams threads, Outlook context, product documents, screenshots, stakeholder asks, and local files into tasks, briefs, PRDs, decisions, roadmaps, and follow-ups.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Primary_Runtime-Antigravity-00A651?style=for-the-badge&logo=google&logoColor=white&labelColor=1a1a2e" alt="Antigravity primary runtime"/>
  &nbsp;
  <a href="https://github.com/officebeats/beats-pm-kit/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-kit?style=for-the-badge&logo=github&labelColor=1a1a2e&color=E6B422" alt="GitHub Stars"/></a>
  &nbsp;
  <img src="https://img.shields.io/badge/Codex_Ready-AGENTS.md-4285F4?style=for-the-badge&labelColor=1a1a2e" alt="Codex ready with AGENTS.md"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Product_Management-AI_Workflows-00A651?style=flat-square" alt="AI product management workflows"/>
   -
  <img src="https://img.shields.io/badge/Storage-Local_First-00A651?style=flat-square" alt="Local-first storage"/>
   -
  <img src="https://img.shields.io/badge/Runtime-Codex_And_Antigravity-00A651?style=flat-square" alt="Codex and Antigravity support"/>
   -
  <img src="https://img.shields.io/badge/Knowledge-Markdown_And_Obsidian-00A651?style=flat-square" alt="Markdown and optional Obsidian knowledge graph"/>
</p>

<br/>

<p>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Get_Started-Install_in_60_seconds-00A651?style=for-the-badge" alt="Get started with Beats PM Kit"/></a>
</p>

</div>

---

## AI Product Management Workflows

Product managers lose time because product context is scattered across meetings, Slack threads, Teams chats, Outlook, Jira links, Confluence pages, spreadsheets, screenshots, and half-finished docs. Beats PM Kit gives that context a local operating system.

The kit is designed for product managers, product leaders, founders, and AI-native operators who want a fast way to manage PM work with AI while keeping source documents, task state, and workflow outputs organized on their own machine. It supports daily product operations like meeting notes to tasks, PM task management from local documents, stakeholder follow-up, product discovery, PRD writing, roadmap planning, launch preparation, bug triage, and executive-ready status updates.

It is not a generic prompt pack. It is a local-first product management workspace with agents, skills, slash-command workflows, task ledgers, privacy guardrails, and runtime adapters for tools such as Google Antigravity and OpenAI Codex.

## Built And Used Daily By An AI-Forward PM

I built Beats PM Kit because I needed a practical AI PM operating system for my own daily product work. I use it to process real product-management context: meeting transcripts, partner follow-ups, stakeholder asks, task triage, planning artifacts, reasoning QA, developer portal work, release questions, and the operational noise that usually gets lost between tools.

The result is both a working toolkit and a portfolio of AI-forward product management practice: context engineering, local-first AI workflows, agentic task management, privacy-aware automation, and cross-runtime PM operations. The goal is simple: make an AI assistant useful for the messy middle of product work, not only for polished strategy docs.

## Core Functionality

| Capability | What the kit supports |
|:---|:---|
| AI PM operating system | A structured workspace for product strategy, product execution, stakeholder context, meeting notes, task ledgers, PRDs, roadmaps, and reusable product workflows. |
| Local-first PM task management | `TASK_MASTER.md`, task detail files, boss requests, bugs, weekly plans, task triage, Trello mirroring, and durable local reports. |
| Meeting notes to tasks | Transcript and chat-intake workflows that extract action items, blockers, owners, dates, decisions, and follow-up questions into local artifacts. |
| Context-aware task routing | PM Decision Router, task-manager workflows, and bounded communication intake for Slack, Teams, Outlook, Calendar, Jira, and Confluence context. |
| Codex product management workflow | `AGENTS.md`, `CODEX_COMMANDS.md`, promoted Codex skills, and thin generated adapters so Codex can load the right workflow without carrying the whole kit in context. |
| Antigravity product management kit | Antigravity-first orchestration with parallel-friendly workflows, `.agent/` as the canonical source, and runtime-neutral fallbacks for other AI coding agents. |
| Product documentation and PRDs | `/create`, `/plan`, `/sop`, `/deck`, `/review`, and related skills for PRDs, one-pagers, runbooks, launch materials, and decision docs. |
| Local document reference | Folder conventions, manifests, transcript archives, context artifacts, resource docs, and markdown links help agents cite local files instead of relying on memory. |
| Markdown and optional Obsidian graph | The kit works as plain Markdown first. Obsidian can be used as an optional direct vault for graph navigation without duplicating files. |
| Privacy-aware automation | Private workspace folders are gitignored, generated runtime folders stay local, and privacy checks guard against publishing personal files, secrets, transcripts, or adapter bloat. |

## Local-First PM Task Management

Beats PM Kit treats the local workspace as the source of truth. Tasks live in `5. Trackers/`, communication evidence is archived in `3. Meetings/`, stakeholder context lives in `4. People/`, and reusable product context can live in `6. Resources/`, `7. Partners/`, and `8. Clients/`.

The default task-management flow is intentionally conservative:

1. Capture or reference the smallest relevant evidence.
2. Search local trackers before creating new work.
3. Update local task files first.
4. Surface stale, overdue, blocked, unclear, duplicated, or possibly complete work as explicit questions.
5. Mirror to Trello only when local state is accepted and the live board is healthy.

This makes the kit useful for fast PM triage without letting automation silently rewrite your priorities.

## Codex And Antigravity Support

The kit is optimized for both Codex and Antigravity while keeping `.agent/` as the canonical workflow layer.

| Runtime | Role in the kit | How it works |
|:---|:---|:---|
| Google Antigravity | Primary power-user runtime | Uses the canonical `.agent/` workflows, parallel-friendly orchestration, runtime rules, and generated local adapters. |
| OpenAI Codex | First-class local coding-agent runtime | Uses `AGENTS.md` as the startup adapter and `CODEX_COMMANDS.md` for slash-command routing into `.agent/workflows/`. |
| Gemini CLI | Compatibility runtime | Uses generated adapters from the same `.agent/` source of truth. |
| Claude Code | Compatibility runtime | Uses generated command pointers and the shared workflow definitions. |
| KiloCode | Compatibility runtime | Uses generated local rules, skills, agents, and workflows. |

Codex works best when it is given a clear map rather than a giant instruction file, so the root `AGENTS.md` stays thin. It points Codex to the specific workflow or skill it needs, which keeps PM task management, context reference, and README/product-doc work faster and more reliable.

## Context Engineering For Product Managers

The kit is built around context engineering: retrieve the right source material at the right time instead of stuffing every meeting, PRD, and chat transcript into every prompt.

The practical patterns are:

- `AGENTS.md` and runtime adapters act as routers.
- `.agent/workflows/` define repeatable PM playbooks.
- `.agent/skills/` provide focused capabilities such as task management, meeting synthesis, PRD authoring, risk review, documentation, and product strategy.
- Local manifests track bounded communication intake windows.
- Task triage scripts identify stale or risky work without guessing closure.
- Optional Obsidian setup turns the existing kit folder into a direct Markdown vault without creating a mirrored copy.

This keeps the kit snappy while preserving reliable references to local files and documents.

## Quick Start

### 1. Clone And Install

```bash
git clone https://github.com/officebeats/beats-pm-kit
cd beats-pm-kit
chmod +x install.sh && ./install.sh
```

The installer creates the folder structure, detects your AI runtime, fixes symlinks, syncs local adapter support when needed, and runs a health check.

Requires Python 3.8+. Optional runtime integrations may use their own CLIs or desktop apps.

### 2. Launch Your AI Runtime

Open the `beats-pm-kit` folder in your preferred AI coding or agent runtime.

| Runtime | Launch command or action | Best use |
|:---|:---|:---|
| [Google Antigravity](https://antigravity.google/) | Open this folder in Antigravity | Fastest power-user workflow and parallel agent fan-out. |
| [OpenAI Codex](https://github.com/openai/codex) | `codex` | Local Codex workflow using `AGENTS.md`, shell commands, and repo files. |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini` | File access, web search, and tool use with generated adapters. |
| [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | `claude` | Agentic file work and command dispatch through generated adapters. |
| [KiloCode](https://kilocode.ai/) | `kilo` | Additional local agent compatibility. |

If you have Antigravity, use it for the fastest workflow. If you live in Codex, the kit is still first-class: start from the repo root, let Codex read `AGENTS.md`, and use `/day`, `/track`, `/paste`, `/transcript`, `/plan`, or `/create` as explicit workflow triggers.

### 3. Run First-Time Setup

```text
/start
```

The setup workflow asks for your name, manager, product focus, and local operating preferences. It seeds the local files that make daily AI product management workflows more useful.

Type `/help` anytime to see the workflow catalog.

## Common Product Management Workflows

| Workflow | Use it when you need to |
|:---|:---|
| `/paste` | Turn copied text, screenshots, files, or visible work signals into local task-management evidence. |
| `/track` | Manage tasks, bugs, boss asks, follow-ups, and local task detail files. |
| `/day` | Generate a daily PM briefing with triage questions and top priorities. |
| `/week` | Produce a weekly tactical plan and focus areas. |
| `/meet` | Convert meeting notes or transcripts into structured notes and action items. |
| `/transcript` | Process recent transcripts into durable local meeting artifacts. |
| `/beats-comms` | Run bounded read-only intake across Slack, Teams, Outlook, and Calendar when scoped by the user. |
| `/boss` | Prepare for manager 1:1s and leadership follow-ups. |
| `/create` | Draft PRDs, specs, one-pagers, product docs, and structured PM artifacts. |
| `/plan` | Build product plans, roadmaps, OKRs, and strategic workstreams. |
| `/sop` | Create privacy-safe runbooks and standard operating procedures. |
| `/deck` | Prepare deck briefs and presentation-ready content. |
| `/review` | Review plans, docs, code, specs, and product artifacts for risk and quality. |
| `/trello` | Mirror accepted local task state into Trello when configured. |
| `/vacuum` | Clean, archive, and optimize the local kit workspace. |

Natural language still works. Slash commands exist when you want deterministic routing.

## Architecture At A Glance

```text
User input or local file
        |
        v
Context Guard and PM Decision Router
        |
        v
Workflow loader in .agent/workflows/
        |
        v
Focused skill loading from .agent/skills/
        |
        v
Local output: tasks, notes, docs, reports, decisions
```

The repo uses a single source of truth:

```text
beats-pm-kit/
+-- 0. Incoming/           # Drop zone for raw notes, screenshots, and uploads
+-- 1. Company/            # Company context and ways of working
+-- 2. Products/           # PRDs, specs, epics, and product briefs
+-- 3. Meetings/           # Transcripts, summaries, reports, and chat archives
+-- 4. People/             # Stakeholder and relationship context
+-- 5. Trackers/           # Task ledgers, bugs, boss requests, and plans
+-- 6. Resources/          # Reference docs, planning material, optional Obsidian index
+-- 7. Partners/           # Partner context and integration materials
+-- 8. Clients/            # Client context and account materials
+-- .agent/                # Canonical agents, rules, skills, templates, workflows
+-- system/                # Scripts, tests, adapters, privacy checks
+-- AGENTS.md              # Thin Codex adapter
+-- CODEX_COMMANDS.md      # Generated Codex command routing table
+-- CLAUDE.md              # Thin Claude Code adapter
+-- GEMINI.md              # Thin Antigravity/Gemini adapter
+-- README.md              # Public landing page and setup guide
```

Generated adapter directories such as `.codex/`, `.gemini/`, `.claude/`, `.kilocode/`, `.context/`, and `.obsidian/` are intentionally local and ignored.

Regenerate runtime adapters with:

```bash
python system/scripts/sync_cli_adapters.py
python system/scripts/sync_codex_skill_adapters.py --output <codex-skills-dir>
```

Verify the public feature inventory with:

```bash
python system/scripts/feature_inventory.py --json
```

## Optional Obsidian And Markdown Knowledge Graph

Obsidian is optional. Beats PM Kit works as a plain Markdown repo first.

If you use Obsidian, open the existing `beats-pm-kit` folder directly as the vault. Do not create a mirrored copy. The helper script can configure local-only Obsidian settings and create a graph index under `6. Resources/obsidian/`:

```bash
python3 system/scripts/obsidian_vault_setup.py --dry-run
python3 system/scripts/obsidian_vault_setup.py --apply
```

This gives product managers a local knowledge graph over tasks, meetings, people, partners, clients, SOPs, and reference documents while preserving the same files Codex and Antigravity already read.

## Privacy-Aware Local Workspace

The kit stores private product-management context locally by default.

| Data type | Default local location | Published by the kit |
|:---|:---|:---:|
| Company strategy and ways of working | `1. Company/` | No |
| Product docs and PRDs | `2. Products/` | No |
| Meeting transcripts and chat archives | `3. Meetings/` | No |
| Stakeholder context | `4. People/` | No |
| Task trackers and task detail files | `5. Trackers/` | No |
| SOPs and operational runbooks | `6. SOPs/` | No |

Folders 1-5 are `.gitignored` by default, and private folders are tracked only through skeleton `.gitkeep` files. The repo also includes checks such as `system/scripts/privacy_guard.py --tree` and `system/scripts/adapter_guard.py --mode check` to prevent private content, local runtime state, personal paths, token-like strings, transcripts, and generated adapter folders from entering shared kit commits.

Important caveat: this repo does not sync your private PM files to a kit cloud service, but your chosen AI runtime/model provider may process prompts, attachments, or tool outputs according to that provider's product and account settings.

## Runtime Compatibility

| Capability | Antigravity | Codex | Gemini CLI | Claude Code | KiloCode |
|:---|:---:|:---:|:---:|:---:|:---:|
| `.agent/` workflows | Yes | Yes | Yes | Yes | Yes |
| Slash-command routing | Yes | Yes | Yes | Yes | Yes |
| PM skills and agents | Yes | Yes | Yes | Yes | Yes |
| Local file reference | Yes | Yes | Yes | Yes | Yes |
| Clipboard and drop-zone intake | Native plus scripts | Scripts | Scripts | Scripts | Scripts |
| Parallel fan-out | Native | Runtime-dependent | Runtime-dependent | Runtime-dependent | Runtime-dependent |
| Generated local adapters | Yes | Yes | Yes | Yes | Yes |
| Privacy guardrails | Yes | Yes | Yes | Yes | Yes |

## Power User Tools

These tools are optional. The kit does not require them, but advanced users may find them useful.

| Tool | Description |
|:---|:---|
| [OpenCLI](https://github.com/jackwener/opencli) | Universal CLI hub for turning apps, local binaries, and websites into scriptable agent commands. |
| [Horizon](https://github.com/peters/horizon) | Spatial terminal workspace for managing terminals, agents, and development tools. |

## Antigravity Enhancements

Community extensions can improve Antigravity workflows. Install from the Extensions panel or the [Open VSX Registry](https://open-vsx.org/).

| Extension | Description | Install |
|:---|:---|:---:|
| [Antigravity Cockpit](https://open-vsx.org/vscode/item?itemName=jlcodes.antigravity-cockpit) | Dashboard-style quota monitor for Antigravity AI usage, limits, and spending. | `jlcodes.antigravity-cockpit` |
| [Antigravity iOS App](https://open-vsx.org/vscode/item?itemName=uladluch.antigravity-mobile-connector) | Control Antigravity from an iPhone, send prompts, monitor generations, and manage projects. | `uladluch.antigravity-mobile-connector` |
| [AG Auto Click & Scroll](https://open-vsx.org/vscode/item?itemName=zixfel.ag-auto-click-scroll) | Auto-click Run and Allow buttons, plus auto-scroll the chat panel. | `zixfel.ag-auto-click-scroll` |
| [Pencil](https://open-vsx.org/vscode/item?itemName=highagency.pencildev) | Create, edit, and preview `.pen` design files with AI assistance. | `highagency.pencildev` |
| [Antigravity Flush](https://open-vsx.org/vscode/item?itemName=pkkkkkkkkkkkkk.antigravity-flush) | Clear context when model sessions hit token-limit issues. | `pkkkkkkkkkkkkk.antigravity-flush` |
| [Antigravity Remote Control](https://open-vsx.org/vscode/item?itemName=hasugoii.antigravity-remote-control) | Control Antigravity from a phone with tunnel, QR, and real-time chat flows. | `hasugoii.antigravity-remote-control` |
| [Gemini Image Editor](https://open-vsx.org/vscode/item?itemName=Zazmic.palm-api-image-editor) | In-editor image tools for WebP conversion, resizing, and background removal. | `Zazmic.palm-api-image-editor` |
| [Antigravity Sync](https://open-vsx.org/vscode/item?itemName=samador.antigravity-settings-sync) | Sync Antigravity settings and extensions across machines using GitHub. | `samador.antigravity-settings-sync` |
| [Better Antigravity](https://open-vsx.org/vscode/item?itemName=kanezal.better-antigravity) | Community-driven fixes such as auto-run improvements and chat rename support. | `kanezal.better-antigravity` |
| [Antigravity Autopilot](https://github.com/timteh/antigravity-autopilot) | Auto-accept agent steps using OS-level accessibility on Windows. | `timteh.antigravity-autopilot` |

## System Rules

The kit operates from `.agent/` as the canonical system. Runtime-specific root files stay thin and generated where possible.

| File | Purpose |
|:---|:---|
| `.agent/rules/GEMINI.md` | System constitution, Context Guard, agent and skill loading protocol, privacy directives, and architecture overview. |
| `AGENTS.md` | Codex startup and slash-command adapter. |
| `CODEX_COMMANDS.md` | Codex command index generated from `.agent/workflows/`. |
| `CLAUDE.md` | Claude Code adapter. |
| `GEMINI.md` | Antigravity and Gemini adapter. |

The Context Guard is the operating discipline behind most workflows:

1. Batch independent reads and checks.
2. Avoid unnecessary re-reads.
3. Load only the workflow and skills needed for the task.
4. Prefer local source files over memory when exact context matters.
5. Keep durable outputs in standard kit folders so runtime switching stays lossless.

## Who This Is For

Beats PM Kit is for:

- Product managers who want an AI product management toolkit that handles real operating context.
- AI-forward PMs and product leaders building repeatable agentic product workflows.
- Founders and builders who need lightweight product operations without buying another SaaS stack.
- Teams experimenting with Codex product management workflows, Antigravity product management workflows, local-first task management, and Markdown-based knowledge systems.
- Operators who want meeting notes to tasks, product docs to action plans, and local files to become useful PM context.

## Built By Product People, For Product People

Beats PM Kit is an OfficeBeats project built from daily product work, not hypothetical prompt examples.

It is a working portfolio of AI-native product operations, context engineering, local-first task management, agentic workflow architecture, and privacy-aware PM automation.

Star this repo if it helps you turn messy PM context into clearer product work.
