---
name: pr-review
description: Review pull requests against team standards and best practices. Use when Reviewing a pull request before merge, Providing feedback on proposed changes, or Validating PR meets project standards
---

# Pull Request Review

Use this skill to review a pull request against the repository quality bar and leave actionable feedback.

## Workflow
1. Read the PR description to understand the goal
2. Review the linked issue(s) for context
3. Check that tests are included and passing
4. Review code changes file by file
5. Verify documentation is updated if needed
6. Leave constructive feedback with specific suggestions
7. Approve, request changes, or comment based on findings

## Examples
**Approval comment:**
```
Looks good! Clean implementation with comprehensive tests.

Minor suggestion: Consider extracting the validation logic
in `UserService.ts:45` into a separate function for reusability.

Approved ✅
```

**Request changes:**
```
Good progress, but a few items need attention:

1. Missing test for error handling in `fetchUser()`
2. The new endpoint needs documentation in the API docs
3. Consider adding input validation for the email field

Please address these and I'll re-review.
```

## Quality Bar
- Start with understanding the PR's goal
- Be constructive and specific in feedback
- Distinguish between required changes and suggestions
- Test the changes locally if complex
- Check for security implications
- Verify backward compatibility
- Approve only when confident in the changes

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
