---
name: cover-letter-writer
description: Generates tailored, narrative-driven cover letters based on Resume and Job Description.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Cover Letter Writer Skill

Use this skill when the user needs to apply for a role. Do not use generic templates.

## Input
1.  **Resume**: The user's current CV (loaded via `view_file` or context).
2.  **Job Description**: The target role (loaded via `read_url_content` or text).

## Process
1.  **Gap Analysis**: Identify the top 3 requirements in the JD and map them to the user's specific achievements.
2.  **Structural Framework**:
    *   **The Hook**: Open with a strong belief statement or a specific connection to the company's recent news. "I've been following [Company]'s shift to..."
    *   **The Story**: Pick ONE major achievement from the resume that proves you can solve their biggest problem. Tell it as a STAR story.
    *   **The Close**: Confident call to action.

## Rules
*   **Tone**: Professional but human. Avoid "To Whom It May Concern".
*   **Length**: Max 300 words.
*   **Format**: Markdown (exportable to PDF).
