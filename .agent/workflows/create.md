---
description: Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks).
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.



# ✍️ Creation Playbook

This workflow guides the **Staff PM** to turn chaos (notes/transcripts) into order (files).

## Steps

0.  **PM Decision Router Preflight**:
    - Load `.agent/skills/pm-decision-router/SKILL.md`.
    - Classify the request or source notes with `python3 system/scripts/pm_decision_router.py --text "<input>"`.
    - Continue when the router returns `create_doc` or the user explicitly invoked `/create`.
    - If the router returns `discovery`, `prioritize`, `decision_log`, or `scope_challenge`, call that out and route through the matching kit workflow instead of forcing a PRD/spec.

1.  **Intent Classification**:
    - **PRD/Spec**: "Write a spec for feature X".
    - **One-Pager**: "Brief for the leadership team".
    - **Bug Report**: "Formalize this issue".

2.  **Context Mining & Guardrails**:
    - **Action**: ALWAYS read `1. Company/Company-Profile.md` and related `2. Products/` docs.
    - **Synthesis**: Summarize relevant points, specifically evaluating the concept against "North Star Metrics" and "Strategic Defensibility" guardrails before writing.
    - **PM Bar**: Carry outcome metric, owner, due date or gate, scope boundary, evidence strength, dependency, and next decision gate into the document or open questions.

3.  **Template Application**:
    - Select the matching template from `.agent/templates/`.
    - **Rule**: Check `templates/system/` first if you are starting a new implementation plan.

4.  **Drafting & Visuals (Stitch-First)**:
    - **Stitch Check**: Ask if the user wants a UI mockup generated alongside the PRD.
    - **Action**: If yes, invoke `/stitch` after drafting the document.
    - **Location**: Write the file to `2. Products/[Product]/features/`.
    - Emit the preview link for the drafted document: `python3 system/scripts/preview_link.py <file> --open --json`.

5.  **Task Connection (State Transition)**:
    - Call `task_boundary` to mark completion of the drafting phase.
    - Ask: "Should I add a task to track this doc's completion?"
    - If yes -> Trigger `/track`.
