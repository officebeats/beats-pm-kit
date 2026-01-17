# Gemini CLI Conductor - Style Guide

> Defines coding style and documentation conventions for this project.

## Markdown Formatting

- Use **GitHub Flavored Markdown** (GFM).
- Use headers (`#`, `##`, `###`) to organize content.
- Use tables for structured data.
- Use blockquotes (`>`) for context or notes.
- Use emojis sparingly for visual scanning (e.g., 🔥 for critical, ⚡ for now).

## File Naming

- Use lowercase with hyphens for new files: `my-new-file.md`
- Use `YYYY-MM-DD` prefix for dated files: `2026-01-03-afternoon.md`

## Agent Prompt Style

- Each agent file should have a clear **Purpose** section.
- Include a **Commands** table for trigger keywords.
- Include a **Priority Order** section if applicable.
- Define **Output Location** for generated files.

## Tracker Conventions

| Column | Example |
| :--- | :--- |
| ID | `BUG-01`, `BR-05`, `P-03` |
| Priority | 🔥 Critical, ⚡ Now, 📌 Next, 📋 Later |
| Status | 🟢 On Track, 🟡 At Risk, 🔴 Blocked, ⏸️ Paused |

## Comments in Code (TypeScript/JS)

- Use JSDoc-style comments for functions.
- Use `// TODO:` for pending work.
- Use `// FIXME:` for known issues.
