---
name: markitdown
description: Convert local files into token-efficient Markdown with Microsoft MarkItDown. Use when the user asks to convert, extract, normalize, read, or ingest PDF, Word, PowerPoint, Excel, Outlook, HTML, CSV, JSON, XML, EPUB, ZIP, image, or audio content as Markdown, and by default when supported non-Markdown files enter the Beats PM intake staging lane.
---

# MarkItDown Intake

Use the repo wrapper so conversion stays local, repeatable, and bounded:

```bash
python3 system/scripts/markdown_intake.py "<input-file>" --output "<output-file>.md"
```

## Workflow

1. Preserve the source file. Accept local files only; never pass an untrusted
   URL or enable remote fetching.
2. Run `python3 system/scripts/markdown_intake.py --check`. If MarkItDown is
   unavailable, explain that Python 3.10+ is required and ask before installing
   `system/requirements-markitdown.txt`.
3. Convert supported staged files to a sibling `.md` file unless the user names
   another local destination. Never overwrite an existing file without the
   user's explicit instruction.
4. Verify that the Markdown file exists and is non-empty, then use that file as
   the primary extraction and reasoning input. Keep the original as evidence.
5. Report scanned PDFs, image-only pages, complex tables, or unsupported media
   as conversion limitations. Do not enable plugins, LLM vision, Azure services,
   or other billable/networked processing without explicit approval.

## Intake Defaults

- Automatically convert `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.xls`, `.msg`,
  `.html`, `.htm`, `.csv`, `.json`, `.xml`, and `.epub` files during file intake.
- Keep screenshots and pasted images on the existing visual-extraction path
  unless the user explicitly requests Markdown conversion.
- Convert ZIP, image, or audio files only when explicitly requested because
  expansion, OCR, or transcription may be expensive or incomplete.
- Treat existing `.md` files as ready. Convert `.txt` only when normalization is
  requested.
- Reject inputs larger than the wrapper's safety limit instead of silently
  consuming them.

MarkItDown output is optimized for LLM analysis and structure preservation, not
pixel-perfect reproduction. Prefer the original file for visual or formatting
QA.
