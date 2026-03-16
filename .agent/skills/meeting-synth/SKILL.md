---
name: meeting-synth
description: "Synthesize a single meeting transcript into structured action items, decisions, and follow-ups. Use when processing a meeting recording, cleaning up transcript notes, or extracting commitments from a conversation."
triggers:
  - "/meet"
  - "/transcript"
version: 3.0.0 (Native Optimized)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Meeting Synthesizer Skill

> **Role**: Extract signal from noise. One meeting → structured output.

## 1. Native Interface

- **Inputs**: `/meet`, `/transcript`. Raw transcript text or file path.
- **Tools**: `view_file` (transcript files), `grep_search`, `run_command`.

## 2. Cognitive Protocol

1. **Ingest**: Read the transcript from `3. Meetings/transcripts/` or `0. Incoming/`.
2. **Extract**:
   - **Decisions Made**: What was agreed on.
   - **Action Items**: Who does what by when (`Owner + Due Date`).
   - **Open Questions**: Unresolved topics needing follow-up.
   - **Key Quotes**: Verbatim stakeholder statements worth preserving.
3. **Route**: Write action items to `5. Trackers/TASK_MASTER.md`. Flag Boss Asks to `5. Trackers/critical/boss-requests.md`.
4. **Archive**: Move processed transcript to `3. Meetings/summaries/`.

## 3. Output Format

``> **Formatting Instructions**: Read the template found at assets/template_1.md and format your output exactly as shown.``

## Boundary

- **This skill handles**: Single meeting transcript → structured summary with action items.
- **NOT for**: Daily tactical planning (use `daily-synth`). Weekly/monthly rollups across multiple meetings (use `weekly-synth`).
