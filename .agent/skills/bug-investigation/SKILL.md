---
name: bug-investigation
description: Investigate bugs systematically and perform root cause analysis. Use when Investigating reported bugs, Diagnosing unexpected behavior, or Finding the root cause of issues
---

# Bug Investigation

Use this skill to reproduce a bug, narrow the failure surface, and document a defensible root cause.

## Workflow
1. Reproduce the bug consistently
2. Gather information (logs, stack traces, steps)
3. Identify when the bug was introduced (git bisect)
4. Form a hypothesis about the cause
5. Verify hypothesis with debugging
6. Document the root cause
7. Plan the fix approach

## Examples
**Bug investigation notes:**
```
## Bug: User profile fails to load

### Reproduction:
1. Log in as any user
2. Navigate to /profile
3. Error: "Cannot read property 'name' of undefined"

### Investigation:
- Stack trace points to ProfilePage.tsx:25
- API returns 200 but empty body when session expired
- Bug introduced in commit abc123 (session refactor)

### Root cause:
Session middleware not checking token expiration correctly.
Returns empty response instead of 401.

### Fix approach:
Update session middleware to return 401 when token expired.
```

## Quality Bar
- Always reproduce before investigating
- Check recent changes that might relate
- Use debugger and logging strategically
- Document your findings
- Consider if bug exists elsewhere
- Write a regression test with the fix

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
