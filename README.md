<div align="center">

<img src="system/docs/assets/hero-banner.png" alt="Beats PM Kit - local-first agentic product management harness" width="100%"/>

# Beats Agentic PM Harness

**A local-first, cross-runtime harness for evidence-backed product-management workflows.**

<a href="https://github.com/officebeats/beats-pm-kit/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-kit?style=flat-square&logo=github" alt="GitHub Stars"/></a>
<img src="https://img.shields.io/badge/Storage-Local_First-00A651?style=flat-square" alt="Local-first storage"/>
<img src="https://img.shields.io/badge/Knowledge-Markdown-00A651?style=flat-square" alt="Markdown knowledge base"/>

</div>

---

## What It Is

Product context scatters across meetings, chat threads, email, documents, and half-finished notes. Beats PM Kit archives that evidence locally as plain Markdown, makes it searchable, and triangulates it into workstreams and tasks that an AI agent can operate on.

It is not a prompt pack. It is an agentic harness with four parts:

- A **canonical Markdown vault**: numbered folders that hold company context, product docs, meeting evidence, stakeholder notes, and task ledgers.
- A **`.agent/` contract**: the single source of truth for agents, skills, workflows, rules, and the command registry.
- **Workflows and skills**: repeatable PM playbooks (intake, meetings, planning, tracking, comms) with bounded context loading.
- **Generated runtime adapters**: thin entrypoint files so multiple AI runtimes load the same behavior from one registry.

Everything private stays on your machine. Nothing is uploaded by the kit itself.

## Core Concepts

### Numbered vault taxonomy

```text
beats-pm-kit/
+-- 0. Incoming/     # Drop zone for raw notes, screenshots, and uploads
+-- 1. Company/      # Company context and ways of working
+-- 2. Products/     # PRDs, specs, epics, and product briefs
+-- 3. Meetings/     # Transcripts, summaries, reports, and chat archives
+-- 4. People/       # Stakeholder and relationship context
+-- 5. Trackers/     # Task ledgers, workstreams, and generated hubs
+-- 6. Resources/    # Reference docs and the optional Obsidian index
+-- 6. SOPs/         # Runbooks and standard operating procedures
+-- 7. Partners/     # Partner context and integration materials
+-- 8. Clients/      # Client context and account materials
+-- .agent/          # Canonical agents, rules, skills, templates, workflows
+-- system/          # Scripts, tests, docs, and guard checks
```

`5. Trackers/tasks/` is canonical task state. Each task is a human-readable Markdown note with a stable ID, evidence links, progress, and decisions. `TASK_MASTER.md` and workstream notes are generated navigation over those files, never a second source of truth.

### Source of truth and generated adapters

`.agent/command-registry.json` owns routing, aliases, execution profiles, and runtime policy. `.agent/workflows/` owns workflow behavior; `.agent/skills/` owns reusable PM methods. Root adapter files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CODEX_COMMANDS.md`), `.omp/config.yml`, and tool ignore files (from `.agent/ignore-manifest.txt`) are generated views produced by:

```bash
python3 system/scripts/sync_cli_adapters.py
```

Edit `.agent/`, then regenerate. Hand-editing generated files gets clobbered by design.

### Command registry and promotion levels

Every slash command resolves through the registry to one workflow file and one execution profile (Fast, Balanced, or Deep). Commands carry a promotion level per runtime: promoted commands ship as native skills, guarded commands require confirmation, and the rest are dispatch-only. `CODEX_COMMANDS.md` is the generated human-readable index; `system/scripts/harness_registry.py resolve <target>` is the machine path.

### Bounded workflow context

The execution loop is `route -> load bounded context -> act with tools -> checkpoint -> verify -> persist artifact`. Initial retrieval is capped at a handful of directly relevant sources, raw evidence stays hash-addressable locally, and compacted context is always traceable back to source files.

## Supported Runtimes

| Runtime | Entrypoint |
|:---|:---|
| omp | `.omp/config.yml` |
| Claude Code | `CLAUDE.md` |
| OpenAI Codex CLI | `AGENTS.md` + `CODEX_COMMANDS.md` |
| Google Antigravity | `ANTIGRAVITY.md` (+ `.agent/`) |
| Gemini CLI | `GEMINI.md` (+ `.agent/rules/GEMINI.md`) |
| GitHub Copilot | `.github/skills/` and `.github/agents/` |
| Obsidian | Optional UI over the same vault (`/obsidian`) |

The harness uses whichever supported runtime is active and selects behavior by positively detected capabilities, not a provider hierarchy. Model defaults are inherited from the runtime; unknown capabilities fail closed. See the generated [runtime compatibility table](system/docs/runtime-compatibility.md).

## Getting Started

```bash
git clone https://github.com/officebeats/beats-pm-kit
cd beats-pm-kit
./install.sh
```

`install.sh` is a thin wrapper around the canonical bootstrap:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive
```

Bootstrap verifies the repo, runs the upgrade-compatibility gate on existing workspaces, creates the ignored local workspace folders, seeds templates, syncs runtime adapters, installs git hooks when possible, and runs privacy and adapter health checks. Agent-first setup also works: give a supported CLI agent the repo URL and let it run the same command.

Then open the folder in your runtime and run `/start` for first-time profile setup, or `/help` for the workflow catalog.

## Key Workflows

Natural language always works; slash commands exist for deterministic routing.

| Category | Commands |
|:---|:---|
| Intake and evidence | `/paste`, `/find`, `/memory`, `/context`, `/chat`, `/beats-comms`, `/beats-slack`, `/beats-teams` |
| Meetings | `/meet`, `/transcript`, `/prep`, `/boss` |
| Planning and strategy | `/plan`, `/create`, `/deck`, `/discover`, `/interview`, `/intel`, `/prioritize`, `/sprint`, `/retro` |
| Tracking | `/track`, `/day`, `/week`, `/handoff` |
| Comms and docs | `/sop`, `/office-cli`, `/review`, `/challenge`, `/improve-plan` |
| Quality and maintenance | `/accuracy`, `/regression`, `/build`, `/vibe`, `/maintain`, `/update`, `/vacuum`, `/archive` |
| Setup and orchestration | `/start`, `/help`, `/obsidian`, `/pack`, `/team`, `/fan-out` |

Each command maps to a file in `.agent/workflows/`; the generated [Codex command table](CODEX_COMMANDS.md) lists the profile and promotion status per command.

## Local Utilities

Workflows delegate repeatable work to small stdlib-only Python scripts in `system/scripts/`, including:

| Utility | Responsibility |
|:---|:---|
| `vault_query.py` | Bounded read-only queries over tasks, labels, and quotes in the vault. |
| `context_router.py` | Indexed full-text retrieval across local PM evidence folders. |
| `task_store.py` / `task_intake_fast.py` | Canonical task-note writes and fast single-signal intake. |
| `transcript_pipeline.py` | Prepare, validate, and process meeting transcripts. |
| `pm_decision_router.py` | Classify messy PM input before workflow execution. |
| `obsidian_bridge.py` | Configure or open the kit folder as a direct Obsidian vault. |
| `pack_manager.py` | Enable dormant optional capabilities under `packs/` (e.g. Trello). |
| `upgrade_compat.py` | Preflight and reversibly migrate legacy kit configurations. |
| `privacy_guard.py` / `adapter_guard.py` | Block private-content leakage and generated-adapter drift. |

Example bounded query:

```bash
python3 system/scripts/vault_query.py tasks --status "In Progress" --text onboarding --limit 10
```

Run `python3 system/scripts/feature_inventory.py --json` for the current machine-readable inventory.

## Privacy Posture

- **Local-first by default.** Personal vault folders are gitignored and tracked only through skeleton `.gitkeep` files. Local runtime state lives in ignored `.beats/`.
- **Guard scripts.** `privacy_guard.py --tree` and `adapter_guard.py --mode check` block private content, personal paths, token-like strings, transcripts, and adapter drift from entering shared commits.
- **Advisor rules.** `WATCHDOG.md` defines review priorities for agent output: no fabricated quotes, IDs, or dates; drafting is fine but outbound sends require explicit user approval; sensitive and client-confidential material never leaves the vault; task state stays in the canonical trackers.
- **Honest caveat.** The kit never syncs your files to a cloud service, but your chosen AI runtime processes prompts and tool outputs according to that provider's own settings.

## Testing

Tests live in `system/tests/` (pytest style, `test_*.py`) and cover the harness registry, adapters, task store, transcript pipeline, privacy and adapter guards, upgrade compatibility, and structural invariants of the vault.

## Credits

Beats PM Kit is an OfficeBeats project built from daily product work. The action-first output policy is an independently worded approach inspired by the MIT-licensed [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) project; no upstream plugin or hook code is bundled.

Star this repo if it helps you turn messy PM context into clearer product work.
