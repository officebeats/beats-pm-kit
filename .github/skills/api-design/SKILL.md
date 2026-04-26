---
name: api-design
description: Design RESTful APIs following best practices. Use when Designing new API endpoints, Restructuring existing APIs, or Planning API versioning strategy
---

# API Design

Use this skill to design API resources, payloads, and failure modes with consistent conventions.

## Workflow
1. Define the resources and their relationships
2. Choose appropriate HTTP methods
3. Design URL structure following REST conventions
4. Define request/response schemas
5. Plan error handling and status codes
6. Consider pagination, filtering, sorting
7. Document the API specification

## Examples
**RESTful API design:**
```
# Users API

GET    /api/v1/users          # List users (paginated)
POST   /api/v1/users          # Create user
GET    /api/v1/users/:id      # Get user by ID
PUT    /api/v1/users/:id      # Update user
DELETE /api/v1/users/:id      # Delete user

# Nested resources
GET    /api/v1/users/:id/posts    # Get user's posts

# Response format
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}

# Error format
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [...]
  }
}
```

## Quality Bar
- Use nouns for resources, not verbs
- Use proper HTTP methods and status codes
- Version your API from the start
- Be consistent in naming and structure
- Provide clear error messages
- Document all endpoints
- Consider rate limiting and caching

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.
