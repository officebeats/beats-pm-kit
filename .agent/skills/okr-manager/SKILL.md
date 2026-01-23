---
name: okr-manager
description: Define, track, and review OKRs with Antigravity-first planning.
triggers:
  - "/okr"
  - "/goal"
  - "/objective"
version: 1.0.0 (Antigravity-First)
author: Beats PM Brain
---

# OKR Manager Skill

> **Role**: Align objectives to measurable outcomes. Keep focus on impact and avoid vanity goals.

## 1. Runtime Capability

- **Antigravity**: Parallel fan-out across Objectives, Key Results, and Dependencies.
- **CLI**: Sequential drafting; request missing context from user.

## 2. Native Interface

- **Inputs**: `/okr`, `/goal`, `/objective`
- **Context**: `SETTINGS.md`, `5. Trackers/DECISION_LOG.md`, `STATUS.md`
- **Tools**: `view_file`, `write_to_file`

## 3. Cognitive Protocol

1. **Align**: Verify objective ties to company or product strategy.
2. **Define**: Each Objective needs 2–4 measurable Key Results.
3. **Validate**: KRs must be numeric, time-bound, and owner-assigned.
4. **Log**: Save to `1. Company/OKR_TRACKING.md` or `2. Products/[Product]/OKR.md`.

## 4. Output Format

```markdown
# OKRs — [Quarter]

## Objective 1: [Outcome]
| Key Result | Owner | Baseline | Target | Due |
| :--------- | :---- | :------- | :----- | :-- |
| KR1        | @name | X        | Y      | Date |
```

## 5. Safety Rails

- Avoid output metrics that are not controllable by the team.
- Flag missing ownership or missing baselines.
