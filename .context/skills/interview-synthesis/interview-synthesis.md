---
description: Synthesize user interviews. Chains Transcript Cleaning -> Insight Extraction -> Feature Linking.
source_tool: antigravity
source_path: .agents\workflows\archive\interview-synthesis.md
imported_at: 2026-04-25T21:29:42.767Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Interview Synthesis Workflow

This workflow transforms raw transcripts into actionable product insights.

## Steps

1.  **Process Transcript**
    - **Agent**: `meeting-synthesizer`
    - **Command**: `/transcript "Process the interview at [TranscriptPath]"`
    - **Output**: `3. Meetings/reports/[Date]_Interview.md`

2.  **Extract Insights (JTBD)**
    - **Agent**: `ux-collaborator`
    - **Command**: `/ux "Extract top 3 Pains and Gains from [PreviousOutput]"`
    - **Input**: `[OUTPUT_MANIFEST].meeting_note` from Step 1
    - **Output**: `2. Products/Research/Insights_Log.md`

3.  **Map to Roadmap**
    - **Agent**: `strategy-synthesizer`
    - **Command**: `/strategy "Map these insights to our Q1 Roadmap"`
    - **Input**: `[OUTPUT_MANIFEST].insights` from Step 2
    - **Output**: `1. Company/ROADMAP.md` (Updated)

## Usage

```bash
/interview "path/to/recording.mp3"
```
