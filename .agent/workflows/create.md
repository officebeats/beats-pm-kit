---
description: Draft PRDs, Specs, and One-Pagers from context (Transcripts/Tasks).
---

# ✍️ Creation Playbook

This workflow guides the **Staff PM** to turn chaos (notes/transcripts) into order (files).

## Steps

1.  **Intent Classification**:
    - **PRD/Spec**: "Write a spec for feature X".
    - **One-Pager**: "Brief for the leadership team".
    - **Bug Report**: "Formalize this issue".

2.  **Context Mining (Parallel Fan-out)**:
    - **Action**: In a single turn, run `grep_search` on `3. Meetings/transcripts/` AND `view_file` on related `2. Products/` docs.
    - **Synthesis**: Summarize relevant points from the transcripts _before_ writing.

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
