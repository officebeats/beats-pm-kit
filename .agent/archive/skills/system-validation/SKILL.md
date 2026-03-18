---
name: system-validation
description: Validates the three-tier mgechev architecture constraints of the Antigravity OS running tests against all directories, preventing systemic feature drift.
---

# Skill Description

**Purpose**: Execute regression CI/CD tests on the local Antigravity `.agent` folder configuration.
**When to trigger**: Called automatically during the `/regression` workflow.

# Instructions

To run the regression validation on the entire agent mesh:

1. Identify the operating system and find the python executable command (e.g., `python` or `python3`).
2. Run the `test_system_integrity.py` file found inside this skill's `scripts/` directory natively.
   - `cd .agent/skills/system-validation/scripts`
   - `python test_system_integrity.py`
3. Analyze the exact output string.
4. Report back the test matrix pass rate and what the system reported regarding directory counts (e.g. "✅ ALL TESTS PASSED").
5. If failures occurred, list the specific errors from the script's output and pause for user guidance.
