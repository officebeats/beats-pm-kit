---
name: deck-builder
description: Build brand-agnostic MBB-style (McKinsey, BCG, Bain) presentation decks from source briefs, notes, and optional templates. Generates executive-grade 16:9 presentations, ghost decks, and strategic narratives optimized for C-suite decision making.
---

# MBB Consulting Deck Builder

Use this skill to produce authentic, top-tier **MBB-grade (McKinsey, BCG, Bain)** presentations that are brand-neutral by default, logically airtight, data-dense, and built specifically for executive and board-level decision-making.

---

## 1. Operating Contract: Executive Rigor vs. Consumer Hype

```text
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ ❌ STUPID CONSUMER / AI HYPE (BANNED)         │ ✅ AUTHENTIC MBB CONSULTING RIGOR (REQUIRED) │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ Decorative emojis (🚀, 💡, 🔥, ✨) in titles │ Zero emojis. Professional monochrome & rules│
│ Vague marketing fluff ("Revolutionizing...") │ Concrete financial metrics ($ ARR, bps, LTV) │
│ Floating rounded pastel cards & gradients    │ High-contrast clean 16:9 grid alignment      │
│ Wall-of-bullets that merely restate title    │ 1 Dominant Hero Proof Object (70%+ canvas)   │
│ Label headings ("Overview", "Next Steps")    │ Complete declarative Action Titles (So What?)│
│ Generic stock icons (gears, puzzle pieces)   │ Harvey Balls, Waterfalls, 2x2s, Issue Trees  │
│ Unverifiable claims without attribution      │ Mandatory bottom Source Footnote on all slides│
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

### The Pyramid Principle & SCQA Structure
1. **Governing Thought**: Every deck opens with the central thesis and recommendation in the first 60 seconds (Slide 1 Executive BLUF).
2. **SCQA Narrative Spine**:
   - **Situation**: Uncontroversial current context agreed upon by leadership.
   - **Complication**: The internal friction, structural bottleneck, or external market shift creating urgency.
   - **Question**: The core strategic choice facing leadership.
   - **Answer**: The quantified, prioritized recommendation and business impact.
3. **Horizontal Logic**: Reading only the slide Action Titles across the deck forms an unbroken, logically airtight executive briefing memo.
4. **Vertical Logic**: Within each slide:
   - **Action Title** = The Claim (complete declarative sentence).
   - **Lead-In** = The Warrant (1 bold sentence explaining *why* the claim holds true).
   - **Hero Proof Object** = The Empirical Evidence (the table, chart, matrix, or issue tree).
   - **Footnote** = The Grounded Citation (source, methodology, sample size).

---

## 2. The 6 Core MBB Layout Archetypes

Every slide must feature **exactly ONE dominant hero proof object** taking up 70%+ of the visual canvas:

### Archetype 1: Harvey Balls Evaluation Matrix
Used for capability assessments, vendor selections, and architectural trade-offs:
- Columns: Criteria (e.g. Speed to Value, Engineering Effort, Operational Risk, 3-Yr NPV).
- Rows: Strategic Options (Option A, Option B, Option C).
- Indicators:
  - `●` (Full / Superior): Complete capability with minimal friction.
  - `◐` (Half / Moderate): Acceptable capability with manageable trade-offs.
  - `○` (Empty / Inadequate): Missing capability or high structural risk.
- Explicit recommendation column highlighting the dominant pathway.

### Archetype 2: Financial Waterfall (Bridge Chart)
Used to bridge baseline financial state to target business outcome:
- Starting bar: Baseline ARR / Margin / Operating Costs.
- Step bars: Quantified positive drivers (e.g. +$3.2M self-serve expansion) and negative frictions (e.g. -$1.0M churn).
- Ending bar: Target ARR / Net Projected Impact with YoY % growth.

### Archetype 3: 2x2 Strategic Prioritization Matrix
Used for portfolio triage and capital allocation:
- Horizontal Axis: Strategic Value / Defensibility (7 Powers).
- Vertical Axis: Execution Complexity / Time-to-Impact.
- Four named quadrants (e.g. "Core Bets", "Quick Wins", "Selective Experiments", "Do Not Pursue").
- Explicitly plots initiatives as numbered nodes with callout keys.

### Archetype 4: 3-Column Structured Synthesis
Used for diagnostic root-cause and strategic alignment:
- **Column 1 (Root Cause / Context)**: The observed structural failure and empirical data.
- **Column 2 (Strategic Intervention)**: The proposed policy, system, or architectural change.
- **Column 3 (Quantified Business Outcome)**: Direct financial return, SLA improvement, or risk reduction.

### Archetype 5: Horizontal Stage-Gated Process Chevrons
Used for executive execution roadmaps and governance:
- Sequential phases with clear time horizons (e.g., Weeks 1–6, Weeks 7–14, Weeks 15–22).
- Explicit **Go / No-Go Exit Criteria** per stage gate.
- Assigned **Single-Threaded Executive Owners**.

### Archetype 6: MECE Issue Tree
Used for comprehensive diagnostic decomposition:
- Root problem branch breaking down into mutually exclusive, collectively exhaustive sub-drivers.
- Percentage allocation or metric weight per branch summing to 100%.

---

## 3. Universal Portability & Execution Protocol

Never assume proprietary software, specific desktop operating systems, or heavy external Python libraries (`python-pptx`, `office-cli`, `libreoffice`) are pre-installed.

### Step 1: Ingest & Formulate Hypothesis
1. Read user briefs, notes, PRDs, and financial models.
2. Draft the slide spine in `storyboard.md` using the MBB Ghost Deck standard (`.agent/templates/decks/mbb-ghost-deck.md`).
3. Audit every Action Title against the "So What?" test.

### Step 2: Compile Self-Contained 16:9 Presentation Package
Run the zero-dependency deterministic MBB deck engine:

```bash
python3 system/scripts/mbb_deck_engine.py \
  0. Incoming/<deck-slug>/storyboard.md \
  --output 0. Incoming/<deck-slug>/deck.html \
  --title "<Executive Title>"
```

The engine automatically compiles:
- Vector SVG Harvey Balls, Waterfalls, and structured tables.
- Locked 16:9 widescreen canvas (1280x720 screen / 16in x 9in print-to-PDF).
- Keyboard presentation navigation (Left, Right, Space, and `F` for full screen).
- Zero external CDN or font dependencies (offline-ready on any machine).

### Step 3: Optional PPTX Generation (When Available)
If `python-pptx` or `office_cli` is positively detected in the environment:
- Compile `.pptx` slides following the identical 16:9 layout grid.
- Otherwise, deliver the standalone executive HTML package and notify the user that the presentation is ready for presentation or print-to-PDF.

---

## 4. Mandatory Self-Enforcing Visual Inspection Gate

An agent **MUST NEVER** mark a deck task complete or assume a deck is done without executing this two-stage visual inspection gate:

### Stage 1: Automated Structural & Semantic Validation
Execute the deterministic validator CLI:

```bash
python3 system/scripts/mbb_deck_engine.py --validate 0. Incoming/<deck-slug>/storyboard.md
```

The validator enforces zero-tolerance gates:
- **Action Title Quality**: Rejects titles shorter than 5 words (labels) or longer than 135 characters (risk of 3-line wrap).
- **Context Lead-in**: Rejects slides missing the 1-sentence bold context bridge.
- **Source Footnote**: Rejects slides without an explicit empirical source attribution.
- **Zero Consumer AI Hype**: Rejects banned marketing buzzwords ("revolutionizing", "disruptive", "supercharge", "unleash", "game-changer", etc.).
- **Zero Janky Lines & Arrows**: Rejects ASCII art arrows (`-->`, `──>`, `==>`).
- **Zero Emojis**: Rejects decorative emojis in titles, headers, or bullet points.

### Stage 2: Visual Frame & Symmetry Verification
- Open the compiled `deck.html` via browser automation or local viewer.
- Capture screenshots of the rendered slides and inspect them visually against consulting quality criteria:
  1. **Symmetry & Gutters**: Left and right margins must strictly match (64px / 64px). Header divider rules and footer baselines must align at identical vertical coordinates across every slide.
  2. **Typography Scale**: Strict hierarchy (21px bold title, 13px bold lead-in, 12.5px body, 10.5px source footnote).
  3. **Vector Cleanliness**: All process chevrons, waterfall bars, and matrix crosshairs must render as crisp SVG/CSS shapes—never ragged text approximations.
  4. **Zero Text Overflow**: Ensure no card body clips, wraps unexpectedly, or bleeds outside container boundaries.

---

## 5. Deliverable Package Structure

Always emit the deliverable inside `0. Incoming/[date-]deck-topic-slug/`:

```text
0. Incoming/2026-09-09-enterprise-expansion-strategy/
├── storyboard.md       # Markdown Ghost Deck (Action Titles, Lead-ins, Proof Objects, Citations)
├── deck.html           # Self-contained 16:9 executive slide presentation (Printable to PDF)
├── source-notes.md     # Empirical data provenance, calculations, and interview citations
└── deck.pptx           # Editable presentation (when python-pptx is available)
```

Return clickable preview links to `storyboard.md` and `deck.html` upon completion.
