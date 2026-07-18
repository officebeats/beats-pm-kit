# Commands Reference

This command list is generated from `.agent/command-registry.json`, the routing source of truth.

| Command | Profile | Purpose |
|:---|:---|:---|
| `/accuracy` | Deep | Implement with high accuracy and self-review (optimized for per-prompt pricing) |
| `/archive` | Fast | Canonical kit workflow. |
| `/beats-comms` | Balanced | Run scoped Slack, Teams, Outlook, Calendar, and transcript intake into local workstream/task updates without sending or mutating source systems. |
| `/beats-slack` | Balanced | Process scoped Slack messages into local Beats PM workstreams and tasks without sending or mutating Slack. |
| `/beats-teams` | Balanced | Process scoped Microsoft Teams chats or channels into local Beats PM workstreams, tasks, and searchable chat transcripts without sending or mutating Teams. |
| `/boss` | Deep | Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc. |
| `/build` | Balanced | Hand off a PRD or specification to the Engineering team agents for actual implementation. |
| `/challenge` | Deep | Internal adversarial review workflow (self mode only) |
| `/chat` | Fast | Consultative planning mode (Switchboard Operator) |
| `/context` | Fast | Query local Beats PM files and return the smallest useful context packet for a topic. |
| `/create` | Deep | Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks). |
| `/day` | Fast | Daily briefing and planning. |
| `/deck` | Balanced | Build brand-agnostic MBB-style presentation decks from a brief, sources, and optional templates. |
| `/discover` | Deep | Run a product discovery cycle with OST, assumption mapping, and experiment design. |
| `/fan-out` | Deep | Fan-out a complex PM task to multiple specialized agents in parallel, then synthesize results. |
| `/find` | Fast | Search past meetings, transcripts, chats, decisions, tasks, and product documents by full text. |
| `/handoff` | Balanced | Unified delegation and execution workflow (Default, Chat, Lead, Relay) |
| `/help` | Fast | The User Manual. Lists commands and explains the system. |
| `/improve-plan` | Deep | Deep planning, dependency checks, and adversarial review |
| `/intel` | Balanced | Capture product knowledge, competitive intelligence, and strategic context from slides, emails, or verbal notes. |
| `/interview` | Deep | Run a Socratic deep interview to clarify ambiguous requirements before planning. |
| `/maintain` | Balanced | Refresh local indexes, validate adapters, run local task triage, and report kit health without mutating source systems. |
| `/meet` | Balanced | Synthesize meeting transcripts into task-master updates, action items, decisions, and summaries. |
| `/memory` | Balanced | Perform memory reflection, consolidate facts and scenarios, update the Mermaid state graph, and clear trace logs. |
| `/obsidian` | Fast | Detect, configure, open, sync, and optionally expose the Beats PM Kit through Obsidian. |
| `/office-cli` | Fast | Check if OfficeCLI is installed and install it if not. Creates, reads, and edits Word, Excel, and PowerPoint files. |
| `/pack` | Fast | List, enable, disable, or run optional Beats PM capabilities kept dormant in this repository. |
| `/paste` | Fast | Capture clipboard content (text, screenshots/images, files) and route task signals to TASK_MASTER by default. |
| `/plan` | Deep | Create or update strategic plans, roadmaps, and OKRs. |
| `/prep` | Balanced | Prepare for an interview with research and roleplay. |
| `/prioritize` | Deep | Score and rank a backlog using RICE, ICE, MoSCoW, Kano, or weighted scoring. |
| `/regression` | Balanced | Run the full Beats PM Kit release gates to catch routing drift, privacy leaks, adapter faults, and workflow regressions. |
| `/retro` | Balanced | Run a sprint or PI retrospective with structured format and action tracking. |
| `/review` | Deep | Code review, Doc review, Release prep. |
| `/sop` | Balanced | Capture, normalize, and maintain privacy-safe SOPs and runbooks for product management and consulting workflows. |
| `/sprint` | Balanced | Generate a prioritized sprint backlog for dev team planning. |
| `/start` | Fast | First-time guided setup and agent-native bootstrap. Run on first session or manually with /start. |
| `/team` | Deep | N coordinated engineering/execution agents on a shared task list. |
| `/track` | Balanced | Capture, triangulate, and manage product work in canonical human-readable Markdown task notes. |
| `/transcript` | Balanced | Process recent or provided transcripts as task-master evidence and route durable updates. |
| `/update` | Deep | Pull the latest kit version from GitHub, run migrations, verify structure, and restore local changes. |
| `/vacuum` | Deep | Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task cleanup, hierarchical integrity auditing, or explicitly triggers /vacuum or /cleanup. |
| `/vibe` | Fast | System health and diagnostics. |
| `/week` | Balanced | Plan the current and upcoming week. |

Natural-language requests remain supported. Use slash commands when deterministic routing is useful.
