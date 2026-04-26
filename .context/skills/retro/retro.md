---
description: Run a sprint or PI retrospective with structured format and action tracking.
source_tool: antigravity
source_path: .agents\workflows\retro.md
imported_at: 2026-04-25T21:29:42.801Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /retro — Retrospective Workflow

## Prerequisites
- Load `retrospective` skill from `.agent/skills/retrospective/SKILL.md`
- Activate **Program Manager** agent

## Steps

1. **Ask Format**: Ask the user which retro format they prefer:
   - 4Ls (Liked/Learned/Lacked/Longed For) — *default*
   - Start-Stop-Continue
   - Sailboat
   - Mad-Sad-Glad
   - 5 Whys (for incident postmortems)

2. **Gather Context**: Read `5. Trackers/TASK_MASTER.md` to summarize what was delivered this sprint/PI.

3. **Capture Input**: 
   - If user provides a transcript → extract retro items automatically
   - If no transcript → prompt for items in each category

4. **Generate Retro Report**: 
   - Use template from `.agent/templates/meetings/retrospective.md`
   - Identify top 3 themes
   - Define maximum 3 action items with Owner + Due Date + DoD

5. **Pattern Detection**: Scan `3. Meetings/retros/` for recurring themes from previous retros.

6. **Route Actions**: 
   - Append action items to `5. Trackers/TASK_MASTER.md` with `[RETRO]` tag
   - Log any process decisions to `5. Trackers/DECISION_LOG.md`

7. **Save**: Write retro to `3. Meetings/retros/YYYY-MM-DD_[Sprint/PI]_retro.md`

8. **Memory Consolidation**: 
   - Execute the `memory-consolidator` skill, specifically searching for trends that survived across multiple sprints by comparing this retro with past retros in `3. Meetings/retros/`.
   - Update `STATUS.md` and `STRATEGIC_INSIGHTS.md` following the consolidator template rules.
