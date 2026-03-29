---
description: N coordinated engineering/execution agents on a shared task list.
---

> **Compatibility Directive**: Requires Claude Code's native teams or Antigravity's parallel fan-out.

# /team — Autonomous Execution Team Workflow

**Trigger**: `/team [N]:[agent-type] [task description]`

> **Capability**: Spawns a structured pipeline of specialized agents (team-plan -> team-prd -> team-exec -> team-verify -> team-fix) without locking the main thread.

---

## Execution Protocol

### Step 1: Decomposition
 `explore` and `planner` agents decompose the high-level task into N specific, executable sub-tasks with tracked dependencies.

### Step 2: Spawning (`team-exec`)
Spawns N workers based on the requested agent type (e.g. `executor`, `designer`, `debugger`). They work in parallel, managing state via the native team task ledger.

### Step 3: Verification & Fix Loop (`team-verify` -> `team-fix`)
1. Review passes via `verifier` and `code-reviewer`.
2. Any regressions trigger `team-fix` with `debugger`.
3. Cycles until completion or terminal failure.

### Step 4: Shutdown
All workers auto-terminate. The leader synthesizes the final pull request or system changes.
