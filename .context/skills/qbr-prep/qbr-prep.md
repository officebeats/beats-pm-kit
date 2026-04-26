---
description: Automated Quarterly Business Review (QBR) prep. Chains OKR grading -> Task Summarization -> Strategic Narrative.
source_tool: antigravity
source_path: .agents\workflows\archive\qbr-prep.md
imported_at: 2026-04-25T21:29:42.796Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# QBR Prep Workflow (`/qbr`)

This workflow automates the heavy lifting of gathering data for your Quarterly Business Review.

## Steps

1.  **Grade OKRs**
    - **Agent**: `okr-manager`
    - **Command**: `/okr "Grade the [Quarter] Internal OKRs. Calculate completion % and confidence scores."`
    - **Output**: `1. Company/OKRs/FY[Year]-[Quarter]_Review.md`

2.  **Summarize Shipments**
    - **Agent**: `task-manager`
    - **Command**: `/task "Summarize all [Quarter] completed tasks labeled 'P0' or 'BigRock'"`
    - **Input**: `[OUTPUT_MANIFEST].quarter_id` from Step 1
    - **Output**: `5. Trackers/reports/[Quarter]_Shipments.md`

3.  **Draft Strategic Narrative**
    - **Agent**: `strategy-synthesizer`
    - **Command**: `/strategy "Draft the QBR Executive Summary: Wins, Misses, and Learnings."`
    - **Input**: `[OUTPUT_MANIFEST]` (Consolidated from Steps 1 & 2)
    - **Output**: `1. Company/STRATEGY/QBR_[Quarter].md`

## Usage

```bash
/qbr "FY26 Q1"
```
