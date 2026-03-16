---
name: document-exporter
description: Convert standard Markdown documents into high-fidelity PDF, HTML, or DOCX formats with embedded assets.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Document Exporter Skill

Use this skill when the user requests a PDF, Word Doc, or "Export" of a markdown file.

## capabilities

1.  **Markdown to HTML (with Base64 Images)**: Creates a self-contained HTML file that can be opened anywhere.
2.  **HTML to PDF**: Uses Headless Chrome to "Print to PDF" preserving layout and images.

## Instructions

### 1. Locate the Markdown File
Ensure you have the absolute path to the `.md` file.

### 2. Generate HTML (Intermediate Step)
Run the `md_to_pdf.py` script located in `scripts/`.

```bash
python3 .agent/skills/document-exporter/scripts/md_to_pdf.py [INPUT_MD] [OUTPUT_HTML]
```

### 3. Convert to PDF (Final Step)
Use Headless Chrome to convert the HTML to PDF.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --print-to-pdf="[OUTPUT_PDF]" "[OUTPUT_HTML]"
```

### 4. Verify & Notify
-   Check the file size of the PDF (should be > 100KB if images are included).
-   Notify user with the file path.
