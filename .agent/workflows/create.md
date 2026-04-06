---
description: Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks).
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# ✍️ Creation Playbook

This workflow guides the **Staff PM** to turn chaos (notes/transcripts) into order (files).

## Steps

1.  **Intent Classification**:
    - **PRD/Spec**: "Write a spec for feature X".
    - **One-Pager**: "Brief for the leadership team".
    - **Bug Report**: "Formalize this issue".

2.  **Context Mining & Guardrails**:
    - **Action**: ALWAYS read `1. Company/Company-Profile.md` and related `2. Products/` docs.
    - **Synthesis**: Summarize relevant points, specifically evaluating the concept against "North Star Metrics" and "Strategic Defensibility" guardrails before writing.

3.  **Template Application**:
    - Select the matching template from `.agent/templates/`.
    - **Rule**: Check `templates/system/` first if you are starting a new implementation plan.

4.  **Drafting & Visuals (Stitch-First)**:
    - **Stitch Check**: Ask if the user wants a UI mockup generated alongside the PRD.
    - **Action**: If yes, invoke `/stitch` after drafting the document.
    - **Location**: Write the file to `2. Products/[Product]/features/`.

5.  **Task Connection (State Transition)**:
    - Call `task_boundary` to mark completion of the drafting phase.
    - Ask: "Should I add a task to track this doc's completion?"
    - If yes -> Trigger `/track`.
