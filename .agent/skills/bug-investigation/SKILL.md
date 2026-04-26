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

## PM Bug Triage & SLA Protocols

### Phase 1: The Inquisition (Triage)
Reject any report that lacks the **Triad of Truth**:
1.  **Steps**: How do I break it?
2.  **Expected**: What should happen?
3.  **Actual**: What did happen?
_If missing, prompt the user immediately._

### Phase 2: Severity Mapping (SLA Enforcement)
Consult `SETTINGS.md` logic:
- **P0 (Critical)**: Data Loss, Security, Global Outage. (Fix: 4h).
- **P1 (High)**: Core features broken. (Fix: 24h).
- **P2 (Med)**: Broken but workaround exists. (Fix: Sprint).
- **P3 (Low)**: Cosmetic. (Fix: Backlog).

### Phase 3: The Log Protocol
1.  **Master Log**: Append to `5. Trackers/bugs/bugs-master.md`.
    - Format: `| ID | Title | P-Level | Owner | Status |`
2.  **Deep Dive**: If complex, create `2. Products/[Product]/bugs/BUG-[ID].md`.
    - Use "Bug Report" Template.

### Phase 4: Routing & Handoff
- **To Eng**: Assign to specific Engineering Partner based on `SETTINGS.md`.
- **To Task**: Create matching task in `TASK_MASTER.md`.
- **To Visual**: If `#screenshot` provided, route to visual-processor.

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
