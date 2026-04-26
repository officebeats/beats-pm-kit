---
name: security-audit
description: Review code and infrastructure for security weaknesses. Use when Reviewing code for security vulnerabilities, Assessing authentication/authorization, or Checking for OWASP top 10 issues
---

# Security Audit

Use this skill to review code and integrations for security weaknesses and rank the findings by severity.

## Workflow
1. Review authentication implementation
2. Check authorization on all endpoints
3. Look for injection vulnerabilities
4. Verify input validation and sanitization
5. Check for sensitive data exposure
6. Review dependency security
7. Document findings with severity

## Examples
**Security audit findings:**
```
## Security Audit Report

### Critical
1. SQL Injection in UserController.ts:45
   - Query constructed with string concatenation
   - Fix: Use parameterized queries

### High
2. Missing authentication on /api/admin/*
   - Admin routes accessible without auth
   - Fix: Add auth middleware

### Medium
3. Sensitive data in logs
   - Passwords logged in debug mode
   - Fix: Sanitize logs, remove sensitive fields

### Recommendations
- Enable security headers (HSTS, CSP)
- Implement rate limiting
- Add input validation middleware
```

## Quality Bar
- Check OWASP top 10 vulnerabilities
- Never trust user input
- Review authentication carefully
- Verify authorization on all routes
- Check for sensitive data exposure
- Scan dependencies for known vulnerabilities
- Document findings with clear severity levels

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
