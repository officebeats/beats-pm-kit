---
name: refactoring
description: Refactor code safely with a step-by-step approach. Use when Improving code structure without changing behavior, Reducing code duplication, or Simplifying complex logic
---

# Refactoring

Use this skill to improve structure without changing behavior, keeping the work incremental and test-backed.

## Workflow
1. Ensure adequate test coverage exists
2. Identify the specific improvement to make
3. Make one type of change at a time
4. Run tests after each change
5. Commit frequently with clear messages
6. Verify no behavior changes occurred

## Examples
**Extract function:**
```typescript
// Before: Inline validation logic
if (email && email.includes('@') && email.length > 5) {
  // process email
}

// After: Extracted to function
function isValidEmail(email: string): boolean {
  return email && email.includes('@') && email.length > 5;
}

if (isValidEmail(email)) {
  // process email
}
```

## Quality Bar
- Never refactor without tests
- Small steps, frequent commits
- One refactoring type per commit
- If tests break, you changed behavior
- Use IDE refactoring tools when available
- Keep the PR focused and reviewable

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
