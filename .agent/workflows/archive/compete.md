---
description: Generate or update a competitive analysis for a product.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /compete — Competitive Intelligence Workflow

## Prerequisites
- Load `competitive-intel` skill from `.agent/skills/competitive-intel/SKILL.md`
- Activate **Product Strategist** agent

## Steps

1. **Identify Target**: Ask user which product and which competitor(s) to analyze. Check `2. Products/[Product]/competitive/` for existing analysis.

2. **Research Phase** (Parallel):
   - Search web for competitor product updates, pricing, funding, key hires
   - Read existing company profiles in `1. Company/` if available
   - Cross-reference `5. Trackers/DECISION_LOG.md` for past competitive decisions

3. **Generate Analysis**: Use template from `.agent/templates/docs/competitive-analysis.md`:
   - Porter's Five Forces assessment
   - 7 Powers evaluation
   - Feature Parity Matrix
   - SWOT Analysis

4. **Battlecard Generation**: Create a sales-ready battlecard with:
   - Win/Loss themes
   - Objection handling
   - Trap questions for prospects

5. **Save**: Write to `2. Products/[Product]/competitive/[Competitor]-analysis-[Date].md`

6. **Update Signal Log**: If new market signals were found, append to the market signal tracker.

7. **Recommendations**: End with 3 actionable strategic recommendations.
