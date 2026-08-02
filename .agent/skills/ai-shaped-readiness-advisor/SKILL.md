---
name: ai-shaped-readiness-advisor
description: Assess whether a product team is ready to use AI through evidence, bounded workflows, human judgment, and measurable operating loops.
---

# AI-Shaped Readiness Advisor

Use this skill for an evidence-backed readiness assessment, not generic AI enthusiasm.

## Assessment Contract

Evaluate the team across these competencies:

1. Context design: relevant evidence is retrievable without stuffing every source into every prompt.
2. Outcome acceleration: AI shortens learning or delivery loops with measurable results.
3. Judgment: humans own ambiguous, high-stakes, and external decisions.
4. Workflow design: repeatable inputs, outputs, tools, boundaries, and failure handling exist.
5. Validation: quality, safety, and efficiency are tested on realistic tasks.

Rate each competency from observed evidence. Separate current proof, inferred capability, and proposed improvement. Do not award readiness for tool access alone.

## Workflow

1. Identify the audience, workflow, desired outcome, and current evidence.
2. Check for context stuffing, normalized retries, unclear ownership, unbounded automation, or unverified outputs.
3. Score each competency and name the evidence supporting it.
4. Identify the smallest operating change that closes the highest-risk gap.
5. Define an acceptance test with quality, safety, cycle-time, and token measures.
6. Return a concise maturity summary, prioritized actions, owners, and proof required.

## Boundaries

- Do not recommend autonomous external mutation without explicit approval gates.
- Do not confuse model capability with team capability.
- Do not hide missing evidence behind an aggregate score.
- Preserve privacy and local-first source handling.
- Use the context-engineering advisor when the main failure is bloated or conflicting context.

## Supporting Material

Read [the complete readiness workshop](references/full-guide.md) only for a facilitated assessment, detailed scoring examples, or maturity-level calibration. Use [workshop-facilitation](../workshop-facilitation/SKILL.md) for interactive pacing.
