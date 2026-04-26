---
name: epic-breakdown-advisor
description: Complete Epic advisory suite. Frame epics as hypotheses, break them down via Humanizing Work patterns, and decompose features into implementable tasks.
---

# Epic Breakdown Advisor

This suite helps you manage the entire lifecycle of an Epic from Hypothesis framing to Technical Task decomposition.

## Phase 1: Epic Hypothesis Framing
Use this when defining a major initiative before roadmap, discovery, or delivery planning.

**If/Then Hypothesis Structure:**
- **If we** [action or solution on behalf of target persona]
- **for** [target persona]
- **Then we will** [attain or achieve a desirable outcome or job-to-be-done]

**Validation Measures:**
- **We know our hypothesis is valid if within** [timeframe]
- **we observe:** [Quantitative / Qualitative measurable outcome]

## Phase 2: Epic Splitting (Humanizing Work)
Break down epics into user stories using Richard Lawrence's complete Humanizing Work methodology—a systematic, flowchart-driven approach that applies 9 splitting patterns sequentially. 

**Pre-Split Validation:**
Verify INVEST criteria: Independent, Negotiable, Valuable, Estimable, Testable.

**The 9 Splitting Patterns (In Order)**
1. **Workflow Steps** — Thin end-to-end slices, not step-by-step
2. **Operations (CRUD)** — Create, Read, Update, Delete as separate stories
3. **Business Rule Variations** — Different rules = different stories
4. **Data Variations** — Different data types/structures
5. **Data Entry Methods** — Simple UI first, fancy UI later
6. **Major Effort** — "Implement one + add remaining"
7. **Simple/Complex** — Core simplest version first, variations later
8. **Defer Performance** — "Make it work" before "make it fast"
9. **Break Out a Spike** — Time-box investigation when uncertainty blocks splitting

## Phase 3: Feature to Task Decomposition
Use this skill to decompose a feature into small, testable technical tasks with explicit dependencies and acceptance criteria.

**Workflow:**
1. Understand the full feature requirements
2. Identify the main components needed
3. Break into independent, testable tasks
4. Identify dependencies between tasks
5. Order tasks by dependency and priority
6. Add acceptance criteria to each task
7. Flag any unknowns or risks

**Example Task:**
```
### Task 1: Database schema
- Add users table with email, password_hash, created_at
- Add sessions table with user_id, token, expires_at
- Acceptance: Migrations run successfully
```
