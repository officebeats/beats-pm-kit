---
name: company-profiler
description: Conducts deep-dive research to create a strategic dossier on a target company.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Company Profiler Skill

Use this skill when the user wants to research a company (`/prep` or "tell me about [Company]").

## Process
1.  **Search Strategy**:
    *   Find "Investor Relations" or "About Us" for core mission.
    *   Search `[Company] strategy 2026` or `[Company] roadmap`.
    *   Search `[Company] competitors` and `[Company] employee reviews`.
    *   Search for recent CMS rulings affecting the company, EHR vendor moves, and competitor AI funding rounds (e.g. Cohere Health).

2.  **Synthesis (The Dossier)**:
    *   Create a markdown file in `6. Career/Intel/[Company]_Dossier.md`.
    *   **Sections**:
        *   **Mission & Vision**: What do they *say* they do?
        *   **The Reality**: What do the financials/reviews say?
        *   **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats.
        *   **Strategic Alignment**: How does the user's background fit their current pain points?

## Output
*   Path to the generated Dossier.
*   Summary of 3 key talking points for an interview.
