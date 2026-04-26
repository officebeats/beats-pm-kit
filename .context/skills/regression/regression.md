---
description: >-
  Run full continuous integration (CI) tests on the Antigravity Kit architecture to ensure no template bloat, agent mapping faults, or skill corruption exists.
source_tool: antigravity
source_path: .agents\workflows\regression.md
imported_at: 2026-04-25T21:29:42.799Z
ai_context_version: 0.9.2
---

# Setup Requirements

> The assistant MUST adopt the **QA Engineer** role before proceeding.

# Instructions

1. Load the `system-validation` skill.
2. Execute the python validation script located in the skill's `scripts/` directory to scan the `.agent/` architecture.
3. Determine if the 3-Tier architecture constraints are intact.
4. Output a summary report of exactly how many Agents, Workflows, and Skills exist, with a pass/fail grade.
