---
description: Automatically process a job application from a URL.
source_tool: antigravity
source_path: .agents\workflows\archive\apply.md
imported_at: 2026-04-25T21:29:42.706Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /apply Workflow

Use this workflow when the user wants to apply for a job.

## Steps

1.  **Ingest**:
    *   Read the Job Description URL (using `read_url_content` or `visual-processor` if blocked).
    *   Extract: Role Title, Company Name.

2.  **Infrastructure**:
    *   Create directory: `6. Career/Applications/[Company]/`.
    *   Save JD as `job_description.md`.

3.  **Draft Assets**:
    *   Run `cover-letter-writer` skill (Input: JD + Resume).
    *   Save draft to `6. Career/Applications/[Company]/cover_letter_draft.md`.

4.  **Log**:
    *   Add a row to `6. Career/JOB_HUNT_DB.md`.
    *   Status: `Drafting`.

5.  **Notify**:
    *   Inform user that assets are ready for review.
