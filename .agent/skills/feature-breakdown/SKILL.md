---
name: feature-breakdown
description: Break down features into implementable tasks. Use when Planning new feature implementation, Breaking large tasks into smaller pieces, or Creating implementation roadmap
---

# Feature Breakdown

Use this skill to decompose a feature into small, testable tasks with explicit dependencies and acceptance criteria.

## Workflow
1. Understand the full feature requirements
2. Identify the main components needed
3. Break into independent, testable tasks
4. Identify dependencies between tasks
5. Order tasks by dependency and priority
6. Add acceptance criteria to each task
7. Flag any unknowns or risks

## Examples
**Feature breakdown example:**
```
## Feature: User Authentication

### Task 1: Database schema
- Add users table with email, password_hash, created_at
- Add sessions table with user_id, token, expires_at
- Acceptance: Migrations run successfully

### Task 2: Registration endpoint
- POST /api/auth/register
- Validate email format and password strength
- Hash password before storing
- Acceptance: Can create user, returns 201

### Task 3: Login endpoint
- POST /api/auth/login
- Verify credentials, create session
- Return JWT token
- Acceptance: Can login, receive valid token

### Dependencies:
Task 2 requires Task 1
Task 3 requires Task 1
```

## Quality Bar
- Each task should be independently testable
- Tasks should be small enough to complete in a day
- Clearly state acceptance criteria
- Identify and document dependencies
- Flag technical risks or unknowns early
- Consider parallel work opportunities

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
