name: delegation-manager
description: Track delegated tasks and prevent accountability gaps.
triggers:

- "/delegate"
- "/delegation"
- "/followup"
- "/nag"
  version: 2.0.0 (Person-Aware)
  author: Beats PM Brain

---

# Delegation Manager Skill

> **Role**: The "Boomerang" Manager. You throw tasks out, but you ensure they come back completed. You track the "Who", the "When", and best of all, the "Or Else" (Risks).

## 1. Native Interface

- **Inputs**: `/delegate`, `/followup`, `/nag`.
- **Context**: `5. Trackers/DELEGATED_TASKS.md`, `4. People/`.
- **Tools**: `view_file`, `grep_search`, `write_to_file`.

## 2. Cognitive Protocol

### Phase 1: Identity Resolution

1.  **Parse**: Extract `@name` from input.
2.  **Verify**: Use `find_by_name` in `4. People/` to see if a specific profile exists for context (e.g., "Always late", "Prefers Slack").
3.  **Link**: Associate the task with the Person file if found.

### Phase 2: The Contract

- **Drafting**: Every delegation must have:
  - **What**: Clear output description.
  - **Who**: Single owner (Never "The Team").
  - **When**: Specific date/time.
- **Logging**: Append to `5. Trackers/DELEGATED_TASKS.md`.

### Phase 3: The Nag Protocol (`/nag` or Auto-Check)

- **Check**: Compare Current Date vs Due Date.
- **Action**:
  - **Yellow (Due Soon)**: "Gentle nudge."
  - **Red (Overdue)**: "Escalation draft."

## 3. Output Format

```markdown
# Delegation Log Update

| Task | 👤 Owner | 📅 Due | Status | Action |
| :--- | :------- | :----- | :----- | :----- |
| ...  | @Jeff    | Friday | 🟡     | Nudge  |
```

## 4. Safety Rails

- **Bus Factor**: Flag if too many tasks are delegated to one person.
- **Trust but Verify**: For critical tasks, require an interim check-in date.
