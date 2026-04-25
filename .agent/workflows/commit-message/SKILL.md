---
name: commit-message
description: Generate commit messages that follow conventional commits and repository scope conventions. Use when Creating git commits after code changes, Writing commit messages for staged changes, or Following conventional commit format for the project
---

# Commit Message

Use this skill to turn a concrete set of staged changes into a clean conventional commit message.

## Workflow
1. Review the staged changes using `git diff --staged`
2. Identify the type of change (feat, fix, docs, style, refactor, test, chore)
3. Determine the scope (component, module, or area affected)
4. Write a concise subject line (50 chars max, imperative mood)
5. Add body if needed to explain "why" not "what"
6. Reference issue numbers if applicable

## Examples
**Feature commit:**
```
feat(auth): add password reset functionality

Implement forgot password flow with email verification.
Users can now reset their password via email link.

Closes #123
```

**Bug fix commit:**
```
fix(api): handle null response in user lookup

Previously threw TypeError when user not found.
Now returns 404 with appropriate error message.

Fixes #456
```

## Quality Bar
- Use imperative mood: "add" not "added" or "adds"
- Keep subject line under 50 characters
- Separate subject from body with blank line
- Use body to explain why, not what (code shows what)
- Reference issues with "Closes #X" or "Fixes #X"
- One logical change per commit
- Don't end subject line with period

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
