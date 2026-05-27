---
name: pm-decision-router
description: Classify messy PM input before workflow execution. Use for task intake, transcripts, communication refreshes, discovery, planning, prioritization, PRD creation, decision logging, and scope-boundary challenges.
priority: P0
triggers:
  - "/paste"
  - "/track"
  - "/transcript"
  - "/beats-comms"
  - "/discover"
  - "/create"
  - "/plan"
  - "/prioritize"
  - "scope"
  - "discovery"
  - "decision"
  - "prioritize"
version: 1.0.0
author: Beats PM Brain
---

# PM Decision Router

## Purpose

Classify incoming evidence before starting a heavier workflow so the kit can decide what to do inside its own system: update a task, create a task, run discovery, challenge scope, prioritize, create a document, log a decision, archive-only, or ask the user for missing intent.

The router is a preflight, not a replacement for downstream workflows. After routing, the selected workflow still owns durable writes and validation.

## Router Schema

Every routing pass returns exactly these fields:

```json
{
  "intent": "task_update | new_task | discovery | scope_challenge | prioritize | create_doc | decision_log | archive_only | ask_user",
  "routing_target": ".agent/workflows/<workflow>.md",
  "confidence": 0.0,
  "evidence": [],
  "candidate_updates": [],
  "blocking_questions": []
}
```

Use `system/scripts/pm_decision_router.py --text "<input>"` for deterministic classification when input text is available. For screenshots or binary files, extract visible text first, then route the text.

## Routing Rules

- `task_update`: existing task ID, explicit progress, blocker, owner, due-date, or status signal. Route to `/track` and update the existing task before creating anything new.
- `new_task`: actionable request without an existing task match. Route to `/track` and apply the task-manager Priority Gate before acceptance.
- `discovery`: problem-space, assumptions, user research, opportunity, experiment, or validation work. Route to `/discover`.
- `scope_challenge`: scope creep, PO-level filler, day-to-day engineering support, release ownership, legacy integration/UI work, or unclear PM ownership. Route to `/track` for Priority Gate handling, but do not create an active task until the user confirms.
- `prioritize`: ranking, scoring, cut-line, RICE, ICE, Kano, MoSCoW, or capacity allocation. Route to `/prioritize`.
- `create_doc`: PRD, spec, one-pager, six-pager, brief, or stakeholder-ready document request. Route to `/create`.
- `decision_log`: explicit decision, go/no-go, tradeoff, alignment, or option selection. Route through `/track` to `5. Trackers/DECISION_LOG.md`.
- `archive_only`: FYI, reference-only, no-action note, or evidence with no current work signal. Route to `/archive` or the relevant local evidence archive.
- `ask_user`: insufficient signal. Return concrete blocking questions instead of guessing.

## Quality Bar

For `task_update`, `new_task`, `discovery`, `prioritize`, `create_doc`, and `decision_log`, carry forward:

- outcome metric
- owner
- due date or gate date
- scope boundary
- evidence strength
- dependency
- next decision gate

If these are missing for committed work, list them in `blocking_questions` or candidate updates. Do not silently convert ambiguous work into active task state.

## Obsidian MCP

Obsidian is optional read/search context only. Use `system/scripts/obsidian_mcp_health.py` to check whether a local Obsidian MCP endpoint is configured.

- Allowed v1 behavior: search, read, list, get document map, get active file path, list tags, open a file in Obsidian.
- Disallowed v1 behavior: write, append, patch, delete, move, execute arbitrary Obsidian commands, or use Obsidian as the task source of truth.
- If Obsidian MCP is unavailable, fall back to repo-local `rg` searches over the canonical kit files.
