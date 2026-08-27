# 📐 Obsidian Graph, Human-Readable Naming & MBB Deck Standards

> **Scope**: System-wide governance for all markdown artifact creation, vault organization, and presentation outputs.  
> **Source of Truth**: `.agent/rules/OBSIDIAN_AND_NAMING_STANDARDS.md`

---

## 1. Human-Readable Filename Policy

Every Markdown file created by workflows, skills, scripts, or agents **MUST** have a descriptive, search-friendly, human-readable `kebab-case` filename.

### ❌ Strictly Prohibited
- Pure ID-only filenames: `TASK-001.md`, `PLAN-042.md`, `PRD-123.md`, `BUG-99.md`, `TRANSCRIPT-20260826.md`
- Hash or UUID filenames: `a1b2c3d4e5f6.md`, `rec_1724689201.md`
- Ambiguous names: `notes.md`, `temp.md`, `output.md`, `doc.md`

### ✅ Mandatory Standard
- **Format**: `[optional-date-]descriptive-topic-slug.md`
- **Examples**:
  - `2. Products/specs/real-time-notification-center.md`
  - `2. Products/specs/stripe-billing-v2-migration.md`
  - `3. Meetings/transcripts/2026-08-26-executive-sync-q3-pricing.md`
  - `3. Meetings/notes/2026-08-26-customer-interview-sarah-chen.md`
  - `5. Trackers/tasks/migrate-stripe-webhook-handler.md`
  - `5. Trackers/bugs/auth-token-refresh-infinite-loop.md`
  - `1. Company/strategy-fy26-expansion.md`

### Stable Machine IDs
If a machine ID is required for cross-system indexing or tracking (e.g. `TASK-042` or `PRD-012`), store it in the YAML frontmatter `id:` property, **never** as the sole filename.

---

## 2. Obsidian Vault & Graph Optimization Standard

To ensure Obsidian graph views remain clean, navigable, and cluster properly over time without forming unreadable "hairballs" or orphan clutter:

### A. Standardized YAML Frontmatter
Every generated note must include standardized frontmatter properties compatible with Obsidian Properties and Dataview:

```yaml
---
title: "Real-time Notification Center"
id: "PRD-042"
type: "prd" # prd | spec | strategy | meeting | task | bug | decision | person | research
status: "in-progress" # draft | in-progress | active | review | done | blocked | archived
tags:
  - type/prd
  - status/in-progress
  - area/notifications
  - priority/p0
owner: "Sarah Chen"
date: 2026-08-26
up: "[[MOC_Products]]"
aliases:
  - "Notification Center Spec"
  - "In-App Alerts PRD"
---
```

### B. Maps of Content (MOC) Star-Topology
Every document must link upward to its canonical Category MOC via the `up:` property or a breadcrumb header:
- `1. Company/MOC_Company.md`
- `2. Products/MOC_Products.md`
- `3. Meetings/MOC_Meetings.md`
- `4. People/MOC_People.md`
- `5. Trackers/MOC_Trackers.md`

This organizes the Obsidian Graph View into beautiful, organic solar-system clusters centered around key hub nodes.

### C. Hierarchical Tag Taxonomy
Use nested tags instead of flat tags to enable precise graph filtering:
- `#type/...`: `#type/prd`, `#type/strategy`, `#type/meeting`, `#type/task`, `#type/decision`
- `#status/...`: `#status/draft`, `#status/in-progress`, `#status/blocked`, `#status/done`
- `#area/...`: `#area/billing`, `#area/onboarding`, `#area/infra`, `#area/growth`
- `#priority/...`: `#priority/p0`, `#priority/p1`, `#priority/p2`

---

## 3. MBB Quality Deck Creation Standards

To produce authentic McKinsey, BCG, and Bain-caliber presentations and completely avoid the generic "AI fingerprint" (3 random cards with floating icons and gradient backgrounds):

### A. Top-Down Pyramid Principle & SCQA
1. **Governing Thought**: The single overarching takeaway of the presentation.
2. **SCQA Narrative Spine**:
   - **Situation**: Current market or company context.
   - **Complication**: The disruptive threat, bottleneck, or opportunity.
   - **Question**: What strategic path resolves this complication?
   - **Answer**: The definitive recommendation with quantified impact.
3. **Action Titles**:
   - Every slide title must be a **complete, declarative sentence** delivering the "So What?".
   - *Example*: *"Enterprise expansion requires self-serve SSO to reduce sales cycles by 40%"* (NOT *"SSO Feature Overview"*).
   - Followed by a 1-sentence **bold context lead-in**.

### B. Single Dominant Proof Object
Every slide must feature **one primary hero visual** chosen from the 70+ consulting layout archetypes:
- **3-Column Waterfall**: Root cause -> Strategic lever -> Quantified outcome.
- **2x2 Prioritization Matrix**: Impact vs. Effort with strategic quadrants.
- **Harvey Balls Comparison Table**: Capability evaluation across vendors or internal options.
- **Horizontal Process Chevrons**: Milestone progression with stage gates and owners.
- **MECE Issue Tree**: Structured hypothesis breakdown covering all mutually exclusive possibilities.

### C. Two-Stage Generation Workflow
1. **Stage 1 (Markdown Ghost Deck)**: Define the slide spine (`kicker`, `action_title`, `lead_in`, `hero_proof_object`, `source_citation`).
2. **Stage 2 (Validated PPTX / PDF Output)**: Programmatically render via `python-pptx` or `office_cli` with strict visual tokens:
   - 16:9 widescreen layout.
   - High contrast: White canvas, one deep primary tone (Navy/Slate), one deliberate accent (Amber/Emerald), neutral 0.5pt structural rules.
   - Restrained typography: Sans-serif (Arial / Inter / Calibri), 20–24pt action titles, 11–13pt body, 9pt citations.
