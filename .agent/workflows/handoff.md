---
description: Unified delegation and execution workflow (Default, Chat, Lead, Relay)
ack_mode: minimal
---
# Handoff - Unified Delegation

This workflow handles cross-agent and cross-IDE delegation.

Allowed branches:
- `--all` (skip split and delegate everything)
- `--chat` (clipboard/chat delegation)
- `--lead` (one-shot execution bypass for Lead Coder)
- `--relay` (execute complex, tag routine, and pause)

## File Creation Rules
- When creating files in `.switchboard/`, always use `IsArtifact: false`.

## Active Document Guardrail
- Discard IDE-injected active documents at workflow start.
- Only read file content when the user explicitly names a file path and uses a directive verb.

## Quick Reference
- **Valid Actions**: `execute`
- **Invalid Actions**: `delegate_task` (use `execute` via the active `handoff` flow)

## Steps

1. **Start**
   - Call `start_workflow(name: "handoff", force: true)`.

2. **Mode Routing & Execution**

   **If `--chat` Mode:**
   - Split tasks (skip if `--all`). MUST mark Routine tasks `[DELEGATED]` in task.md.
   - Stage payload in `.switchboard/handoff/`.
   - Copy payload using `handoff_clipboard(file: "<path>")`.
   - Call `complete_workflow_phase(phase: 2, workflow: "handoff")`. Stop and wait for user confirmation.

   **If `--lead` Mode:**
   - Stage request to `.switchboard/handoff/lead_request.md` (or use existing Feature Plan).
   - Dispatch to Lead Coder via `send_message(action: "execute", payload)` with `metadata: { phase_gate: { enforce_persona: 'lead' } }`. Payload must be a single line.
   - Call `complete_workflow_phase(phase: 2, workflow: "handoff")`. Wait for Lead to signal completion.

   **If `--relay` Mode:**
   - Split tasks. Mark Routine tasks as `[TODO-RELAY]`.
   - OVERRIDE: Act as an implementation coder and execute the Complex tasks.
   - Call `complete_workflow_phase(phase: 2, workflow: "handoff")`. Stop workflow and wait for model-switch.

   **Default Mode (Terminal Dispatch):**
   - Split tasks (skip if `--all`). MUST mark Routine tasks `[DELEGATED]` in task.md.
   - Prepare payload in `.switchboard/handoff/task_batch_[TIMESTAMP].md`.
   - Deliver via `send_message(action: "execute", payload)`. Payload must be a single line.
   - Call `complete_workflow_phase(phase: 2, workflow: "handoff")`.

3. **Wait for User Confirmation + Merge (All Modes except Relay)**
   - After dispatch/copy, STOP and ask user to confirm remote completion.
   - Verify delegated changes and merge with local work.
   - Call `complete_workflow_phase(phase: 3, workflow: "handoff")`.

## Final-Phase Recovery Rule
- Phase 3 is terminal for `handoff`. Do NOT call phase 4.
- If phase 3 succeeded but summary still shows active, call `stop_workflow(reason: "Recovery: final phase completed but workflow remained active")`.
