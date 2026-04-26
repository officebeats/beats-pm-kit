---
name: document-exporter
description: Convert Markdown documents into PDF, DOCX, PPTX, or XLSX formats. Routes Office formats to OfficeCLI, PDF via Chrome.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Document Exporter Skill

Use this skill when the user requests a PDF, Word Doc, PowerPoint, Excel export, or "Export" of a markdown file.

## Capabilities

1.  **Markdown → HTML → PDF**: Creates a self-contained HTML file, then uses Headless Chrome to print to PDF.
2.  **Markdown → DOCX** (via OfficeCLI): Creates a real Word document with proper formatting.
3.  **Markdown → PPTX** (via OfficeCLI): Creates a PowerPoint presentation from structured content.
4.  **Markdown → XLSX** (via OfficeCLI): Creates an Excel workbook from tabular data.

## Format Selection

| User Says | Action |
|-----------|--------|
| "PDF", "print" | Use existing HTML/PDF pipeline (Steps 1-4 below) |
| "Word", "DOCX", "document" | Delegate to `office-cli` skill |
| "PowerPoint", "PPTX", "deck", "presentation", "slides" | Delegate to `office-cli` skill |
| "Excel", "XLSX", "spreadsheet", "tracker" | Delegate to `office-cli` skill |
| "export" (no format specified) | Ask user; default PPTX for presentations, DOCX for docs, PDF for reports |

## PDF Pipeline Instructions

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
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --print-to-pdf="[OUTPUT_PDF]" "[OUTPUT_HTML]"

# Windows
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --print-to-pdf="[OUTPUT_PDF]" "[OUTPUT_HTML]"
```

### 4. Verify & Notify
-   Check the file size of the PDF (should be > 100KB if images are included).
-   Notify user with the file path.

## Office Format Instructions

For DOCX, PPTX, or XLSX exports, load and follow the `office-cli` skill:

```
.agent/skills/office-cli/SKILL.md
```

The `office-cli` skill has complete workflows for:
- Creating PowerPoint decks with slides, shapes, tables, charts, and images
- Creating Word documents with paragraphs, styles, tables, and images
- Creating Excel workbooks with data, formulas, charts, and pivot tables

### Quick Delegation Example

```bash
# User wants a PowerPoint from a markdown outline:
# 1. Parse the markdown headings as slide titles
# 2. Parse bullet points as slide content
# 3. Use officecli batch mode for performance

officecli create output.pptx
officecli batch output.pptx --commands '[
  {"command":"add","parent":"/","type":"slide","props":{"title":"Slide Title from H1"}},
  {"command":"add","parent":"/slide[1]","type":"shape","props":{"text":"Content from bullets","x":"2cm","y":"5cm","w":"22cm","h":"12cm","font":"Arial","size":"18"}}
]' --json
```
