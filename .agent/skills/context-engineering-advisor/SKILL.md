---
name: context-engineering-advisor
description: Diagnose and redesign bloated AI context using bounded retrieval, explicit context ownership, and phase-aware compaction.
---

# Context Engineering Advisor

Use this skill when an AI workflow is expensive, brittle, vague, retry-heavy, or overloaded with persistent instructions and source material.

## Core Contract

Treat model attention as scarce. Optimize completed-task quality per token, not prompt size in isolation.

1. Define the decision or deliverable before selecting context.
2. Persist only product identity, non-negotiable safety rules, durable preferences, and recurring constraints.
3. Retrieve episodic evidence just in time.
4. Load one workflow or skill directly; do not create a router-of-routers.
5. Preserve raw evidence outside active context and reference it by stable path or ID.
6. Compact only at completed phase boundaries and retain decisions, exact language, citations, unresolved risks, verification state, and the next action.
7. Measure the whole trajectory, including turns, retries, cache traffic, tool payloads, and output.

## Diagnostic

For every context element, ask:

- What decision does it support?
- Can retrieval replace persistence?
- Who owns its inclusion boundary?
- What concrete failure occurs if it is omitted?
- Is more context masking conflicting or poorly structured source material?

Exclude an element when no concrete failure can be named. Reconcile conflicting sources instead of passing all versions downstream.

## Architecture Pattern

Use four layers:

- Working context: the current goal, direct workflow, and up to five relevant sources.
- Addressable archive: full tool results, transcripts, and raw evidence retrievable by ID.
- Compiled knowledge: current navigation pages that cite raw sources and hashes.
- Durable state: decisions, priorities, workstreams, and open loops.

Compiled knowledge is not authoritative for exact quotes, commitments, legal language, security findings, or final citations; retrieve the raw source for those.

## Phase Cycle

`research → plan/checkpoint → reset or compact → implement → verify`

Research may be noisy. The checkpoint must be dense and structured. Implementation should start from that checkpoint plus only the evidence needed for the next phase.

## Response Profiles

- `compact_operator`: terse progress and tool narration.
- `artifact`: complete polished deliverable.
- `verbatim`: exact source or stakeholder wording.

Use `compact_operator` during execution. Do not shorten final artifacts or exact-language outputs merely to save tokens.

## Supporting Material

Read [the full facilitation and diagnostic guide](references/full-guide.md) only when running the interactive workshop or when a detailed example is required. Use [workshop-facilitation](../workshop-facilitation/SKILL.md) for interactive pacing.
