---
name: deck-builder
description: Build brand-agnostic MBB-style PPTX/PDF/static web presentation decks from source briefs, notes, and optional templates. Use for `/deck` or when a user wants a polished presentation package without company-specific private branding baked into the kit.
---

# MBB Consulting Deck Builder

Use this skill for repeatable, top-tier MBB-style (McKinsey, BCG, Bain) presentation deck creation that is brand-neutral by default, mathematically and logically structured, and optimized for executive decision-making.

## Operating Contract & Consulting Rigor

1. **Pyramid Principle & SCQA Storyline**:
   - Start with the **Governing Thought** (the single core recommendation).
   - Structure the executive narrative using **SCQA**: Situation (context), Complication (bottleneck/threat), Question (strategic choice), Answer (quantified solution).
   - Write **Action Titles**: Every slide title must be a complete declarative sentence delivering the "So What?" (e.g., *"Enterprise self-serve onboarding reduces customer acquisition cost by 35% within 6 months"*, never a label like *"Onboarding Overview"*).
   - Include a 1-sentence **bold context lead-in** bridging the title to the proof object.

2. **Zero AI Fingerprint Guarantee**:
   - Strictly ban generic AI presentation tropes: NO floating card grids with decorative emojis/icons, NO random gradient backdrops, NO empty filler bullet points.
   - Every slide must feature **exactly ONE dominant hero proof object** taking up 70%+ of the visual slide canvas.

3. **Consulting Layout Archetype Library (70+ Patterns)**:
   - **3-Column Structured Synthesis**: Context / Root Cause -> Strategic Lever -> Quantified Business Impact.
   - **2x2 Prioritization Matrix**: Impact vs. Effort / Urgency vs. Importance with named quadrants.
   - **Harvey Balls Evaluation Table**: Capability comparison across vendors or architectural options with filled/half/empty circle indicators.
   - **Waterfall / Bridge Chart**: Visual bridge from Baseline Revenue -> Levers -> Target Revenue.
   - **Horizontal Process Chevrons**: Milestone progression with stage gates, owners, and deliverables.
   - **MECE Issue Tree**: Mutually Exclusive, Collectively Exhaustive diagnostic branch.

4. **Human-Readable Output Workspace**:
   - Always output into a descriptive kebab-case folder: `0. Incoming/[date-]deck-topic-slug/` (e.g. `0. Incoming/2026-08-26-q3-growth-strategy-deck/`).

## Default Deliverables

Unless specified otherwise:
- **Editable PPTX** (validated OpenXML via `python-pptx` / `office_cli`)
- **Print-ready PDF** (16:9 widescreen)
- **Standalone Responsive HTML Contact Sheet / Web Slide Viewer**
- **Markdown Ghost Deck / Slide Spine** (`storyboard.md`) with kicker, action title, lead-in, hero proof, and citation
- **Source Notes & Provenance** (`source-notes.md`)

## End-to-End Workflow

1. **Phase 1: Source Ingestion & Hypothesis Formation**
   - Read all provided briefs, strategy notes, metrics, and PRDs.
   - Formulate the governing hypothesis and validate against the source evidence.

2. **Phase 2: Storylining & Ghost Deck (Markdown First)**
   - Write the slide spine in `storyboard.md` before generating slide layouts.
   - Check each slide against the "So What?" test: Does the action title communicate a decisive insight without reading the body?

3. **Phase 3: Visual Grammar & Proof Object Construction**
   - Widescreen 16:9 canvas with precise grid alignment.
   - High-contrast executive color system: Canvas (Pure White `#FFFFFF`), Primary Anchor (Deep Navy `#0A192F` or Slate `#1E293B`), Intentional Accent (Amber `#D97706` or Emerald `#059669`), Structural Dividers (0.5pt Neutral Gray `#E2E8F0`).
   - Typography: Clean sans-serif (Calibri / Arial / Inter), 20–24pt bold action title, 12–14pt lead-in, 10–12pt data callouts, 8–9pt bottom citation.

4. **Phase 4: Deterministic Generation & Validation**
   - Generate the `.pptx` file using `python-pptx` or `office_cli`.
   - Render slide previews, contact sheet, and confirm XML integrity.
   - Verify that all data points, citations, and source references are grounded.

## Completion Response

Return clickable hyperlinks to the final PPTX, PDF, HTML viewer, and the Markdown storyboard.

