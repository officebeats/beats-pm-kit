---
name: code-review
description: Review code quality, patterns, and best practices. Use when Reviewing code changes for quality, Checking adherence to coding standards, or Identifying potential bugs or issues
---

# Code Review

Use this skill to inspect code for correctness, maintainability, and higher-order risks before changes move forward.

## Workflow
1. Understand the context and purpose of the code
2. Check for correctness and logic errors
3. Evaluate code structure and organization
4. Look for potential performance issues
5. Check for security vulnerabilities
6. Verify error handling is appropriate
7. Assess readability and maintainability

## Examples
**Code quality feedback:**
```
// Before: Nested callbacks
fetchUser(id, (user) => {
  fetchPosts(user.id, (posts) => {
    render(posts);
  });
});

// Suggestion: Use async/await
const user = await fetchUser(id);
const posts = await fetchPosts(user.id);
render(posts);
```

**Security feedback:**
```
// Issue: SQL injection vulnerability
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Fix: Use parameterized query
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

## Quality Bar
- Focus on the most impactful issues first
- Explain why something is a problem
- Provide concrete suggestions for improvement
- Consider the developer's experience level
- Balance thoroughness with pragmatism
- Praise good patterns when you see them

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
