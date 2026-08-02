---
name: engineering-planner
description: Convert a validated request into a decision-complete, testable implementation plan grounded in the actual repository.
---

# Engineering Planner

Use this skill after inspecting the current implementation and before broad or high-risk changes.

## Planning Contract

1. Establish repository state, relevant entrypoints, existing contracts, and tests.
2. Describe the desired behavior and quality bar without inventing unnecessary infrastructure.
3. Choose one implementation approach and make interfaces, ownership, compatibility, and migration behavior explicit.
4. Cover data flow, failure handling, privacy, approvals, and rollback or recovery.
5. Define tests that prove behavior and prevent regressions.
6. Sequence changes so each slice is independently testable.

## Required Output

- Outcome and acceptance criteria.
- Current-state constraints.
- Implementation changes grouped by subsystem.
- Public interfaces or schemas that change.
- Migration and compatibility behavior.
- Test cases, rollout, and monitoring.
- Assumptions that an implementer must not reinterpret.

## Context Discipline

Use a compact plan as the implementation source of truth. Keep research traces and failed hypotheses out of the implementation context unless they explain a live constraint. At a completed planning boundary, create a checkpoint containing decisions, source paths, unresolved risks, and the next action.

## Safety

Do not plan destructive changes against unresolved targets. Preserve user-owned dirty changes, avoid silent external mutation, and keep model-specific adapters generated from canonical sources.

## Supporting Material

Read [the complete engineering-planning guide](references/full-guide.md) only for extended planning modes or examples. Use the repository's active plan and workflow contracts as higher-priority context.
