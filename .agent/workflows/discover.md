---
description: Run a product discovery cycle with OST, assumption mapping, and experiment design.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /discover — Product Discovery Workflow

## Prerequisites
- Load `discovery-coach` skill from `.agent/skills/discovery-coach/SKILL.md`
- Activate **Staff PM** agent

## Steps

1. **Define Outcome**: Ask user for the desired outcome (business metric + user outcome). Verify it aligns with OKRs in `SETTINGS.md`.

2. **Check Existing Work**: Search `2. Products/[Product]/discovery/` for prior discovery briefs on this topic.

3. **Build Discovery Brief**: Use template from `.agent/templates/docs/discovery-brief.md`:
   - Problem Space (Who, What, Evidence, Impact)
   - Desired Outcomes
   - Initial Opportunity Solution Tree
   - Top 5 Assumptions with risk classification

4. **Assumption Mapping**:
   - Plot assumptions on Certainty × Criticality matrix
   - Identify the #1 riskiest assumption (Unknown + High Criticality)
   - Recommend cheapest experiment to test it

5. **Experiment Design**: For the top assumption, create an experiment card:
   - Method (interview, fake door, prototype test, A/B test)
   - Success/failure criteria
   - Duration and owner

6. **Stakeholder Alignment**: Generate a summary for the sponsor with the discovery plan and gate date.

7. **Save**: Write to `2. Products/[Product]/discovery/DISCOVERY-[Initiative].md`

8. **Track**: Add discovery tasks to `5. Trackers/TASK_MASTER.md` with `[DISCOVERY]` tag.
