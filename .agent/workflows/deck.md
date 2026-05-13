---
description: Build brand-agnostic MBB-style presentation decks from a brief, sources, and optional templates.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# /deck - MBB-Style Deck Builder

**Trigger**: `/deck`

Use this workflow when the user asks for a high-polish presentation, slide deck, PowerPoint, PDF, or presentation website that should be reusable for any company or brand.

## Inputs

Collect or infer:

- source brief, notes, transcript, URL, or files
- intended audience and decision the deck should drive
- output directory and deck name
- optional brand/template/reference decks
- required outputs: PPTX, PDF, static website, or a subset

Default output location is `0. Incoming/<deck-slug>/` unless the user provides another path.

## Workflow

1. **Source and template read**
   - Read the user's brief and source files.
   - If a template/reference deck is provided, inspect it for visual grammar and content constraints.
   - Record source notes, asset provenance, and template audit in the run workspace.

2. **Claim spine**
   - Convert the material into an MBB-style story: one sharp claim per slide, one dominant proof object, concise support text.
   - Separate main narrative slides from appendix/detail slides.
   - Do not invent facts, metrics, schemas, contracts, or customer claims.

3. **Design system**
   - Use the supplied brand/template when available.
   - If no brand is supplied, create a neutral executive style with restrained color, Arial or system sans typography, clear rules, and disciplined whitespace.
   - Do not create fake logos or approximated brand marks.

4. **Build artifacts**
   - Use the `deck-builder` skill.
   - Prefer artifact-tool for editable PPTX generation.
   - Generate PDF from a print-stable source.
   - Generate a static responsive website when requested, with locked 16:9 slide frames, keyboard navigation, hash links, and print CSS.

5. **Quality gates**
   - Render slide previews and a contact sheet.
   - Verify PPTX package integrity, PDF page count, and website responsive fold checks.
   - Scan text for forbidden/private terms named by the user.
   - Replace uncertain payloads, schemas, or implementation details with checklist/table formats unless the source provides exact contracts.

## Safety

- Keep source-specific confidential material in ignored output folders, not in `.agent/` templates.
- Public kit files for this workflow must remain brand-agnostic.
- Never overwrite source templates.
