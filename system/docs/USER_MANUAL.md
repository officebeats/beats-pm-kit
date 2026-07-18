# Beats PM Kit User Manual

Beats PM Kit is a local-first product-management workspace for finding past evidence and turning it into current decisions, tasks, plans, and follow-ups. Markdown is canonical. Obsidian is optional. External task boards are optional packs.

## Core Flow

Use the kit when product context is scattered across Granola, Quill, Outlook, Teams, Slack, meeting transcripts, screenshots, and local notes.

1. Capture or archive a bounded source window.
2. Search past meetings, chats, decisions, tasks, and product documents.
3. Triangulate new evidence against existing workstreams and tasks.
4. Update one human-readable Markdown task note.
5. Regenerate Task Master and workstream navigation.
6. Surface conflicts, missing sources, duplicates, blockers, and open decisions instead of guessing.

## Install Or Upgrade

```bash
git clone https://github.com/officebeats/beats-pm-kit
cd beats-pm-kit
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url https://github.com/officebeats/beats-pm-kit
```

Before changing an existing kit:

```bash
python3 system/scripts/upgrade_compat.py --json
```

The gate identifies unsafe Markdown titles, duplicate task IDs, broken links, source-setup gaps, and legacy model pins. It does not rename files. Apply safe migrations with:

```bash
python3 system/scripts/upgrade_compat.py --apply
```

Backups stay under ignored `.beats/backups/`. Legacy model choices move into ignored `.beats/model-policy.json`; newer evaluated choices are preserved.

## Start A Work Session

Open the repository root in Antigravity, Codex, Claude Code, Gemini CLI, or KiloCode. The kit detects the active runtime without applying a permanent brand hierarchy.

Start with `/start`, then use:

| Workflow | Purpose |
| --- | --- |
| `/find` | Search past meetings, transcripts, chats, decisions, tasks, and documents. |
| `/paste` | Capture copied text, screenshots, or visible evidence. |
| `/track` | Reconcile tasks, blockers, owners, dates, and workstreams. |
| `/meet` | Synthesize one meeting into decisions and commitments. |
| `/transcript` | Process transcript evidence into durable local artifacts. |
| `/day` | Build a current daily brief from evidence and task state. |
| `/week` | Synthesize progress, risks, and next-week focus. |
| `/create` | Draft a PRD, brief, spec, or one-pager. |
| `/plan` | Build a roadmap, strategy, or delivery plan. |
| `/obsidian` | Configure or open the kit as a direct Obsidian vault. |
| `/maintain` | Refresh indexes, validate adapters, evaluate models, and report health. |

## Find Past Evidence

Markdown remains the source of truth. The local SQLite full-text index is disposable:

```bash
python3 system/scripts/context_router.py build --write-wiki --json
```

Use `/find` with a decision, product, person, ticket, task, phrase, or time window. Results should include readable titles, excerpts, exact paths, source types, and confidence. Read complete files only after selecting the best matches.

When sources disagree, preserve the conflict and escalate. Do not flatten Granola, Quill, Outlook, Teams, and Slack into an invented consensus.

## Manage Tasks In Markdown

Task notes under `5. Trackers/tasks/` are canonical. Each note should have a descriptive filename, human-readable title and H1, stable internal ID, source evidence, and only supported owner/date/status fields.

`5. Trackers/TASK_MASTER.md` and `5. Trackers/WORKSTREAMS.md` are generated navigation, not a second task database.

Before creating a task:

1. Search for the task, workstream, ticket, owner, and relevant decision.
2. Compare the new evidence with existing task notes.
3. Update the existing task when the commitment is the same.
4. Create a task only when the commitment is distinct and actionable.
5. Mark uncertain fields as open instead of inventing them.

## Use Obsidian Without Duplicating Data

The repository can be opened directly as an Obsidian vault:

```bash
python3 system/scripts/obsidian_bridge.py guide --json
```

Or run `/obsidian configure`. The workflow points to the current kit folder, Task Master, tracker folder, and guide. It does not create another repository or mirrored task store.

## Use Optional Packs

Packs live under `packs/` and are dormant by default. `/pack enable <name>` changes only ignored `.beats/packs.json`; it does not download a repository or silently mutate an external service. Markdown remains canonical.

## Runtime And Model Policy

`.agent/command-registry.json` is the only routing source of truth.

| Profile | Use |
| --- | --- |
| Fast | Retrieval, capture, help, and routine daily status. |
| Balanced | Task reconciliation, meetings, transcripts, weekly synthesis, and communication intake. |
| Deep | Strategy, PRDs, consequential decisions, critical review, security, and release work. |

Models default to `inherit`, allowing provider improvements to flow through automatically. Conflicting evidence, high-stakes decisions, external mutations, broad changes, or failed validation escalate to Deep. Missing Deep support produces a warning and retains the active runtime's inherited model; it never silently changes providers.

```bash
python3 system/scripts/model_policy.py status --json
python3 system/scripts/model_policy.py resolve track --signal conflicting_evidence --json
```

Local promotions require matching evaluation evidence and are backed up:

```bash
python3 system/scripts/model_policy.py promote <runtime> <profile> <model-id> --evaluation .beats/evals/comparison.json --json
python3 system/scripts/model_policy.py reset --json
```

## Evaluate Models Safely

```bash
python3 system/scripts/model_eval.py run --mode offline --json
```

Live evaluation is local and explicit. It uses only sanitized fixtures, runs exactly three times per scenario, and stores raw outputs only under ignored `.beats/evals/`:

```bash
python3 system/scripts/model_eval.py run --mode live --runtime <runtime> --profile <profile> --model <model-id> --allow-live --repeats 3 --json
```

A candidate must pass every safety gate and either improve aggregate quality by at least two points without scenario regressions, or improve latency by at least 20 percent while staying within one quality point.

## Privacy And Safety

Private operating folders, task state, transcripts, local adapters, model policy, and evaluation outputs are gitignored.

```bash
python3 system/scripts/privacy_guard.py --tree
```

The kit does not upload PM content to a kit cloud service. The active AI runtime may still process prompts, attachments, or tool output according to its own settings. Reading a source for task triangulation does not authorize sending, reacting, editing, deleting, or changing unread state.

## Maintenance

Use `/maintain` or run:

```bash
python3 system/scripts/sync_cli_adapters.py
python3 system/scripts/command_integrity.py --require-generated
python3 system/scripts/model_eval.py run --mode offline --json
python3 system/scripts/context_health.py
```

Generated `MANIFEST.json`, `ROUTING.md`, architecture counts, runtime adapters, and compatibility documentation should never be edited by hand.
