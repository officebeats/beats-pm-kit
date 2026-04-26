---
description: Score and rank a backlog using RICE, ICE, MoSCoW, Kano, or weighted scoring.
source_tool: antigravity
source_path: .agents\workflows\prioritize.md
imported_at: 2026-04-25T21:29:42.791Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /prioritize — Backlog Prioritization Workflow

## Prerequisites
- Load `prioritization-engine` skill from `.agent/skills/prioritization-engine/SKILL.md`
- Activate **Staff PM** agent

## Steps

1. **Identify Backlog**: Ask user for the backlog source:
   - `5. Trackers/TASK_MASTER.md` (full backlog)
   - A specific product backlog in `2. Products/[Product]/`
   - Manual list of items

2. **Select Framework**: Ask user which framework to use:
   - **RICE** — *default for mixed backlogs*
   - **ICE** — for quick triage
   - **MoSCoW** — for scope negotiation
   - **Kano** — for customer-facing features
   - **Weighted Scoring** — for strategic initiatives

3. **Define Criteria** (if Weighted Scoring):
   - Ask user for 3-5 scoring dimensions
   - Get weight allocation (must sum to 100%)
   - Get stakeholder agreement on weights BEFORE scoring

4. **Score Items**: 
   - For RICE/ICE: Score each item on all dimensions
   - For MoSCoW: Classify each item with capacity validation
   - For Kano: Classify by customer impact type

5. **Generate Scorecard**: Use template from `.agent/templates/docs/prioritization-scorecard.md`:
   - Scored and ranked table
   - Cut line based on available capacity
   - Decision notes explaining key ranking choices

6. **Capacity Check**: Validate that committed items fit within available resources.

7. **Save**: Write to `2. Products/[Product]/backlog-score.md` or present inline.

8. **Stakeholder Output**: Format the scored backlog as a presentable table for planning meetings.
