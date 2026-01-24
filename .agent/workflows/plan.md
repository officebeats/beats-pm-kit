---
description: Create or update strategic plans, roadmaps, and OKRs.
---

# 🗺️ Strategy & Planning Playbook

This workflow guides the **Product Strategist** to define the "What" and "Why".

## Steps

1.  **Task Boundary (Deep Work)**:
    - **Control**: Call `task_boundary(Mode="PLANNING", TaskName="Strategic Planning")`.
    - **Goal**: Establish the state for complex reasoning.

2.  **Parallel Context Loading**:
    - **Action**: In a SINGLE turn:
      - Scan `1. Company/` for existing strategy docs.
      - Read `5. Trackers/okr_tracking.md`.
      - Check `2. Products/` for recent PRDs.
    - **Synthesis**: Build a context map before asking user questions.

3.  **Framework Selection**:
    - Ask the user which framework to apply:
      - **7 Powers** (Moats)
      - **Driscoll** (What? So What? Now What?)
      - **Amazon Working Backwards** (Press Release)

4.  **Drafting (Visual Excellence)**:
    - **Action**: Use `chief-strategy-officer` skill.
    - **Requirement**: Must include at least one **Mermaid Diagram** (Strategy House or Roadmap).
    - **Template**: Use `templates/system/implementation_plan.md` for execution-focused plans.

5.  **Output**:
    - Save to `2. Products/[Product]/STRATEGY.md` or `1. Company/STRATEGY_FY26.md`.
