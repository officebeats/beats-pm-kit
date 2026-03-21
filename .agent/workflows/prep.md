---
description: Prepare for an interview with research and roleplay.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /prep Workflow

Use this workflow when the user has an upcoming interview.

## Steps

1.  **Context**:
    *   Identify target Company and Role.
    *   Check `6. Career/Intel/[Company]_Dossier.md`. If missing, run `company-profiler`.

2.  **Strategy**:
    *   Read the Dossier.
    *   Identify "3 Key Talking Points" that align user's background to company pain points.

3.  **The Cheat Sheet (Enrichment)**:
    *   Run `interview-simulator` (Part 1).
    *   **Action**: Append a `# ⚡ Interview Cheat Sheet` section to the existing Dossier.
    *   **Content**: 12 Predicted Questions + Quick Tips + succinct STAR answers.

4.  **Simulation**:
    *   Run `interview-simulator` (Part 2 - Interaction).
    *   Focus on the specific Role's challenges.

5.  **Debrief**:
    *   Summarize performance.
    *   Update `6. Career/JOB_HUNT_DB.md` status to `Interview Prep Complete`.
