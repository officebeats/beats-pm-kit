---
name: deck-builder
description: Build brand-agnostic MBB-style PPTX/PDF/static web presentation decks from source briefs, notes, and optional templates. Use for `/deck` or when a user wants a polished presentation package without company-specific private branding baked into the kit.
---

# Deck Builder

Use this skill for repeatable, high-polish deck creation that is brand-neutral by default and can inherit a user-provided template.

## Operating Contract

- Build from the user's sources, not from invented details.
- Produce an MBB-style narrative: one slide claim, one dominant proof object, concise support.
- Keep all company/private specifics in the generated output workspace, never in this skill.
- Use exact source schemas or API payloads only when provided. Otherwise use conceptual checklists, tables, or responsibility matrices.
- Never create fake logos or approximate brand identity assets.

## Default Deliverables

Unless the user specifies otherwise:

- editable PPTX
- print-ready PDF
- static responsive presentation website
- source notes, template audit, deviation log
- rendered previews, contact sheet, responsive checks, and final stats

Default final location: `0. Incoming/<deck-slug>/`.
Default scratch workspace: `${TMPDIR:-/tmp}/codex-presentations/<thread-or-manual-id>/<deck-slug>/`.

## Workflow

1. **Ground in sources**
   - Read all provided briefs, URLs, files, and reference decks.
   - Capture provenance in `source-notes.txt`.
   - If a template deck is provided, extract its visual grammar into `template-audit.txt`.

2. **Write the slide spine**
   - Produce a slide list with `kicker`, `title`, `support`, `proof object`, and `notes/source`.
   - Keep main narrative concise; move dense matrices, caveats, terms, and schemas to appendix.
   - Use a strong executive arc: thesis, stakes, operating model, architecture/workflow, capability, roadmap/path, risk/guardrails, proof, close.

3. **Lock visual grammar**
   - Inherit template typography, palette, footer treatment, image rules, and spacing if provided.
   - If no template exists, use a restrained consulting system: white field, one primary color, one accent color, gray rules, Arial/system sans, precise grids.
   - Avoid generic card spam; vary proof objects across diagrams, tables, timelines, equations, matrices, and checklists.

4. **Build with artifact-tool**
   - Use the bundled presentation runtime when available.
   - Generate editable PPTX first, then render previews.
   - Build the website from the same slide spine so PDF and web stay consistent.
   - Use `100svh`, locked 16:9 frames, keyboard navigation, hash links, and print CSS.

5. **Verify**
   - Render every slide to PNG and create a contact sheet.
   - Validate the PPTX as a zip/package.
   - Verify the PDF page count.
   - Run responsive checks for desktop, tablet, and mobile.
   - Scan generated text for user-specified forbidden terms and accidental private placeholders.

## Completion Response

Return links to final PPTX, PDF, website entrypoint, and any important verification notes. Mention any source uncertainty that was intentionally handled with checklist/table language instead of fabricated detail.
