---
name: requirements-translator
description: Translate raw input into structured requirements and route to correct artifacts.
triggers:
  - "/requirements"
  - "/translate"
  - "/specify"
version: 1.0.0 (Antigravity-First)
author: Beats PM Brain
---

# Requirements Translator Skill

> **Role**: Turn ambiguous asks into testable requirements and route to the right artifact (PRD, bug, task).

## 1. Runtime Capability

- **Antigravity**: Parallel extraction of problem, user, acceptance criteria, and risks.
- **CLI**: Sequential prompts for missing fields.

## 2. Native Interface

- **Inputs**: `/requirements`, `/translate`
- **Context**: `SETTINGS.md`, `5. Trackers/TASK_MASTER.md`
- **Tools**: `view_file`, `write_to_file`

## 3. Cognitive Protocol

1. **Classify**: Bug vs Feature vs Task.
2. **Extract**: Problem, user, success metric, acceptance criteria.
3. **Route**:
   - Feature → `prd-author`
   - Bug → `bug-chaser`
   - Task → `task-manager`
4. **Log**: Add a short requirements summary to the chosen artifact.

## 4. Output Format

```markdown
## Requirements Summary
- **Problem**: ...
- **User**: ...
- **Success Metric**: ...
- **Acceptance Criteria**: ...
```

## 5. Safety Rails

- Ask once if a required field is missing; do not guess.
