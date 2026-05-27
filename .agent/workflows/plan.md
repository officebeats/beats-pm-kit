---
description: Create or update strategic plans, roadmaps, and OKRs.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# 🗺️ Strategy & Planning Playbook

This workflow guides the **Product Strategist** to define the "What" and "Why".

## Steps

0.  **PM Decision Router Preflight**:
    - Load `.agent/skills/pm-decision-router/SKILL.md`.
    - Classify the input with `python3 system/scripts/pm_decision_router.py --text "<input>"`.
    - Continue when the router returns `create_doc`, `prioritize`, `discovery`, `decision_log`, or the user explicitly invoked `/plan`.
    - If the router returns `scope_challenge` or `ask_user`, resolve the scope/decision question before writing a plan.

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
    - **Action**: Use `roadmapping-suite` for roadmap/OKR/capacity planning and `product-strategy-suite` for strategy canvas, options, and decision tradeoffs.
    - **Requirement**: Must include at least one **Mermaid Diagram** (Strategy House or Roadmap).
    - **Template**: Use `templates/system/implementation_plan.md` for execution-focused plans.
    - **PM Bar**: Explicitly state outcome metric, owner, scope boundary, evidence strength, dependencies, and next decision gate.

5.  **Output**:
    - Save to `2. Products/[Product]/STRATEGY.md` or `1. Company/STRATEGY_FY26.md`.
