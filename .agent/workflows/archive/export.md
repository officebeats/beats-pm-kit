---
description: Export a markdown document to PDF or HTML using the document-exporter skill.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Export Workflow

Use this workflow when the user runs `/export` or asks to convert a document to PDF/Doc.

## Steps

1.  **Identify Target**: Determine which markdown file the user wants to export.
    *   If current context is a file, use that.
    *   If ambiguous, ask.

2.  **Activate Skill**: Load `document-exporter`.

3.  **Run Conversion**:
    *   Execute the `md_to_pdf.py` script to generate HTML.
    *   Execute Headless Chrome to generate PDF.

4.  **Confirm**:
    *   Verify the output file exists and has size > 0.
    *   Notify the user with the absolute path.

## Example
User: "/export veritas.md"
Agent:
1. `view_file veritas.md` (Check path)
2. `write_to_file` (if needed to fix local image paths, though script handles most)
3. `run_command python3 .../md_to_pdf.py ...`
4. `run_command .../Google Chrome ...`
5. `notify_user`
