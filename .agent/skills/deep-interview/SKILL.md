---
name: deep-interview
description: Run a structured, ambiguity-gated interview that turns an underspecified request into a decision-complete brief.
---

# Deep Interview

Use this skill when implementation would otherwise require material guesses about outcome, audience, constraints, workflow, or acceptance criteria.

## Inputs

- The user request and available source material.
- The decision or artifact being prepared.
- Known constraints, stakeholders, and deadlines.

## Protocol

1. Inspect available evidence before asking questions.
2. State the current interpretation in plain language.
3. Ask one high-impact question at a time.
4. Prefer concrete choices when they represent real tradeoffs; accept free-form answers when the space is genuinely open.
5. Resolve intent first: goal, success, audience, boundaries, and constraints.
6. Resolve implementation second: interfaces, data flow, failure modes, validation, rollout, and compatibility.
7. Maintain a compact decision ledger rather than replaying the full interview.
8. Stop when the brief is decision complete and no implementer choices remain.

## Ambiguity Gate

Ask only when the answer changes scope, behavior, risk, or acceptance. Discoverable repository facts must be inspected, not asked. If a low-risk preference is unanswered, use the recommended default and record it as an assumption.

## Output

Return a concise brief containing:

- Goal and success criteria.
- Audience and scope boundaries.
- Required behavior and interfaces.
- Source and privacy requirements.
- Edge cases and recovery behavior.
- Test and acceptance criteria.
- Explicit assumptions.

## Supporting Material

Read [the complete interview playbook](references/full-guide.md) only when a specialized interview mode, extended example, or full question bank is needed. Use [workshop-facilitation](../workshop-facilitation/SKILL.md) for pacing.
