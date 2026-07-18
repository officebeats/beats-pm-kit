---
description: Run a product discovery cycle with OST, assumption mapping, and experiment design.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.



# /discover — Product Discovery Workflow

## Prerequisites
- Load `pm-decision-router` skill from `.agent/skills/pm-decision-router/SKILL.md`
- Load `discovery-engine` skill from `.agent/skills/discovery-engine/SKILL.md`
- Activate **Staff PM** agent

## Steps

0. **PM Decision Router Preflight**: Classify the user's input with `python3 system/scripts/pm_decision_router.py --text "<input>"`. Continue only when the router returns `discovery` or the user explicitly invoked `/discover`. If it returns `scope_challenge`, resolve the scope boundary before building a discovery brief.

1. **Define Outcome**: Ask user for the desired outcome (business metric + user outcome). Verify it aligns with OKRs in `SETTINGS.md`.

2. **Check Existing Work**: Search `2. Products/[Product]/discovery/` for prior discovery briefs on this topic.

3. **Build Discovery Brief**: Use template from `.agent/templates/docs/discovery-brief.md`:
   - Problem Space (Who, What, Evidence, Impact)
   - Desired Outcomes
   - Scope Boundary (in scope, out of scope, decision owner)
   - Initial Opportunity Solution Tree
   - Top 5 Assumptions with risk classification
   - Evidence Strength and Dependencies

4. **Assumption Mapping**:
   - Plot assumptions on Certainty × Criticality matrix
   - Identify the #1 riskiest assumption (Unknown + High Criticality)
   - Recommend cheapest experiment to test it

5. **Experiment Design**: For the top assumption, create an experiment card:
   - Method (interview, fake door, prototype test, A/B test)
   - Success/failure criteria
   - Duration and owner
   - Next decision gate

6. **Stakeholder Alignment**: Generate a summary for the sponsor with the discovery plan and gate date.

7. **Save**: Write to `2. Products/[Product]/discovery/DISCOVERY-[Initiative].md`

8. **Track**: Add discovery tasks to `5. Trackers/TASK_MASTER.md` with `[DISCOVERY]` tag.
