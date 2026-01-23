---
name: delegation-manager
description: Track delegated tasks and prevent accountability gaps.
triggers:
  - "/delegate"
  - "/delegation"
  - "/followup"
version: 1.0.0 (Antigravity-First)
author: Beats PM Brain
---

# Delegation Manager Skill

> **Role**: Keep delegated work visible. Ensure every handoff has an owner, due date, and next follow-up.

## 1. Runtime Capability

- **Antigravity**: Parallel extraction of Owners, Dates, and Dependencies.
- **CLI**: Sequential parsing with user clarification if missing fields.

## 2. Native Interface

- **Inputs**: `/delegate`, `/followup`
- **Context**: `5. Trackers/DELEGATED_TASKS.md`, `SETTINGS.md`
- **Tools**: `view_file`, `write_to_file`

## 3. Cognitive Protocol

1. **Normalize**: Identify the task, owner, due date, and rationale.
2. **Confirm**: If owner or due date missing, ask once.
3. **Track**: Append to `5. Trackers/DELEGATED_TASKS.md` with status.
4. **Remind**: Surface follow-up date in output.

## 4. Output Format

```markdown
# Delegated Tasks

| Task | Owner | Due | Status | Next Follow-up |
| :--- | :---- | :-- | :----- | :------------- |
| ...  | ...   | ... | Pending | YYYY-MM-DD |
```

## 5. Safety Rails

- Never record PII beyond names/titles.
- Flag overdue tasks as **At Risk**.
