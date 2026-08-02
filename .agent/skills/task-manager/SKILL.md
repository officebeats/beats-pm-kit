---
title: Product Management Task Manager
name: task-manager
description: Turn daily product evidence into readable Markdown tasks and generated workstream views.
priority: P0
maxTokens: 2600
triggers:
  - /task
  - /track
  - /triage
  - /paste
  - /transcript
  - task manager
version: 5.0.0
author: Beats PM Kit
---

# Product Management Task Manager

The task note is the source of truth. `TASK_MASTER.md`, workstream summaries, dashboards, Obsidian, and optional packs are views over the Markdown notes in `5. Trackers/tasks/`.

## Core contract

- Create one descriptive Markdown file per task, such as `confirm-beta-customer-list.md`.
- Put the stable internal ID in `task_id` frontmatter, never in the filename or visible H1 for new tasks.
- Require a readable `title` in frontmatter and the same human-readable H1.
- Preserve evidence links, decisions, progress, completed checklist items, dates, and source provenance.
- Treat `5. Trackers/TASK_MASTER.md` as generated navigation. Do not edit its managed task table as primary state.
- Rebuild it with `python3 system/scripts/task_store.py rebuild` after task-note changes.
- Do not read or synchronize optional packs during normal task management. Packs run only through an explicit `/pack` request.

## Fast capture

For one pasted email, chat, transcript excerpt, or screenshot transcription, run:

```bash
python3 system/scripts/task_intake_fast.py --text "<raw evidence>" --source "<source label>"
```

The fast path must:

1. Save the raw evidence before interpretation.
2. Match and update an existing task note when evidence is strong.
3. Otherwise create a readable candidate note with `status: needs-triage`.
4. Mark inferred owner, date, or workstream fields clearly instead of dropping the task.
5. Rebuild Task Master from the resulting task notes.
6. Defer broad health analysis unless the user asks for it.

## Daily evidence triangulation

Granola, Quill, Outlook, Teams, Slack, local transcripts, and existing Markdown notes are the core evidence loop.

- Use only named or configured read-only source windows; never broad-scan an account or workspace.
- Archive source material locally before routing durable task changes.
- Match evidence against existing tasks and workstreams before creating new ones.
- Consolidate repeated signals from multiple sources under one workstream.
- Record both the initial source and latest confirming source.
- Treat explicit completion evidence as completion; treat implied completion as a confirmation question.
- When historical context is missing or contradictory, run one bounded `/find` query. Its optional semantic recall is only a lead; link the dated Markdown evidence that confirms the task change.
- `/day`, `/week`, and `/boss` use `critical_commitment_refresh.py` to refresh configured sources before ranking work.
- TWG is optional enrichment for an explicitly requested live refresh, never no-context snapshot input. If enabled and healthy, use it only under `.agent/rules/TWG_READ_ONLY.md`; exact Jira/Confluence evidence stays Rovo/native-first.
- If a source fails, label the gap and use cached local evidence for that source while retaining fresh results from successful sources.

## Task note format

```yaml
---
title: Confirm beta customer list
task_id: BPM-0123
status: next
lane: Next
owner: Product
due: 2026-07-24
workstream: Search beta
source_refs:
  - 3. Meetings/transcripts/2026-07-18-product-council.md
inferred_fields:
  - owner
created: 2026-07-18
updated: 2026-07-18
---
```

The body uses these readable sections:

- `# <Task title>`
- `## Summary`
- `## Context`
- `## Success and scope`
- `## Next actions`
- `## Evidence`
- `## Progress`
- `## Decisions`

Keep open actions to three when possible. Retain completed actions with completion date and evidence.

## Priority and quality gate

- Check for a duplicate task or workstream before creating new state.
- Use local `1. Company/ways-of-working.md` when it exists; do not bake one user's reporting structure or scope rules into the public kit.
- Infer missing fields when the evidence reasonably supports them and list those fields in `inferred_fields`.
- For consequential ambiguity, record the task as `needs-triage` and ask one concrete question.
- `Today` and `Next` work should have an owner, date or decision gate, intended outcome, and known dependency.
- Never silently mark a task complete, change source-system state, or discard raw evidence.

## Workstream output

Lead recurring task output with readable workstreams:

```markdown
### Search beta readiness
- Latest outcome: Beta cohort criteria agreed
  - Evidence: Product council on July 18; confirmed in Teams on July 19
- Completed: Instrumentation owner confirmed
  - Completed: July 19 from Teams
- Open items: 2
  - Product — confirm customer list by July 24
- Recommended next 3:
  - Confirm customer list
  - Resolve analytics dependency
  - Prepare go/no-go decision
```

IDs belong in metadata, links, and agent references—not headings or status prose.

## Upgrade safety

Before converting an existing kit, run `python3 system/scripts/upgrade_compat.py --json`. The migration adds safe titles in place, keeps legacy filenames stable, backs up every changed file, and refuses ambiguous or broken task state.

## Optional Obsidian view

After a full `/track` update, run `python3 system/scripts/obsidian_bridge.py guide --json`. Offer the exact kit and task paths when `should_prompt` is true, but never block Markdown task work on Obsidian.
