---
description: Promotion / Performance Review Packet Generator. Chains Task Filtering -> Praise Extraction -> Impact Statement.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Promo Packet Workflow (`/promo`)

This workflow gathers the evidence needed to justify your promotion or high performance rating.

## Steps

1.  **Filter High-Impact Work**
    - **Agent**: `task-manager`
    - **Command**: `/task "List all P0/P1 tasks completed in the last 6 months. Group by Product."`
    - **Output**: `4. People/Self-Review/Evidence_Log.md`

2.  **Extract Praise & Feedback**
    - **Agent**: `meeting-synthesizer`
    - **Command**: `/transcript "Scan all 1:1 notes from the last 6 months for 'praise', 'grade', or 'feedback'."`
    - **Output**: `4. People/Self-Review/Praise_Log.md`

3.  **Draft Impact Statement**
    - **Agent**: `boss-tracker`
    - **Command**: `/boss "Draft a 1-page Self-Review highlighting 'Business Impact' and 'Leadership'."`
    - **Input**: `[OUTPUT_MANIFEST]` (Evidence + Praise)
    - **Output**: `4. People/Self-Review/Draft_Packet.md`

## Usage

```bash
/promo "L5 to L6"
```
