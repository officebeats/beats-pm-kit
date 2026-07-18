---
description: Score and rank a backlog using RICE, ICE, MoSCoW, Kano, or weighted scoring.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.



# /prioritize — Backlog Prioritization Workflow

## Prerequisites
- Load `pm-decision-router` skill from `.agent/skills/pm-decision-router/SKILL.md`
- Load `roadmapping-suite` skill from `.agent/skills/roadmapping-suite/SKILL.md`
- Activate **Staff PM** agent

## Steps

0. **PM Decision Router Preflight**: Classify the user's input with `python3 system/scripts/pm_decision_router.py --text "<input>"`. Continue when the router returns `prioritize` or the user explicitly invoked `/prioritize`. If it returns `scope_challenge`, resolve scope ownership before scoring.

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
   - Include owner, dependency, evidence strength, and next decision gate for each item above the cut line.

7. **Save**: Write to `2. Products/[Product]/backlog-score.md` or present inline.

8. **Stakeholder Output**: Format the scored backlog as a presentable table for planning meetings.
