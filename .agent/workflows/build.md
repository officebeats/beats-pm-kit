---
description: Hand off a PRD or specification to the Engineering team agents for actual implementation.
---

> **Compatibility Directive**: This component requires the Antigravity execution mesh or Claude Code, as it spawns actual code execution agents.

# /build — Engineering Execution Workflow

**Trigger**: `/build [path/to/PRD.md]` or when a concrete spec is ready to be implemented in code.

> **Capability**: This workflow passes a finalized product spec to the Engineering persona agents (Architect, Planner, Executor), effectively bridging Product Management to Software Engineering.

---

## Execution Protocol

### Step 1: Pre-Execution Consensus (`engineering-planner`)

The PRD is first passed to the `engineering-planner` skill to validate technical feasibility:

1. **Planner Agent** reviews the PRD and drafts an implementation plan.
2. **Architect Agent** verifies the architectural soundness of the plan.
3. **Critic Agent** validates quality, testability, and edge cases.
4. *Loop until consensus* (max 5 iterations).
5. Output: A technical `consensus-plan.md` ready for coding.

### Step 2: Autonomous Delivery (`autopilot` or `team-orchestrator`)

Based on task magnitude:

- **Large/Complex**: Spawns `/team [size]:executor` to execute in parallel.
- **Medium/Standard**: Invokes `autopilot` to run the execution loop (Code -> QA -> Fix) autonomously.

### Step 3: Validation and Handoff

When execution completes, the QA Engineer and Verifier examine the PRs/commits. 
Run `/review` to accept the changes.
