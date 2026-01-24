---
description: Code review, Doc review, Release prep.
---

# 🔎 Review Playbook

This workflow guides the **Tech Lead** or **Staff PM** to enforce quality.

## Steps

1.  **Select Target**:
    - **Code**: "Review this PR" or "Check this script".
    - **Doc**: "Proofread this PRD".
    - **Release**: "Prep for version bump".

2.  **Code Review**:
    - Run `code-simplifier` (#simplify).
    - Run `python system/scripts/vibe_check.py` to ensure no regressions.
    - Check for PII violations (Privacy Rule).

3.  **Doc Review**:
    - Check against `1. Company/PROFILE.md` for tone alignment.
    - Ensure "Next Steps" are clear.

4.  **Output**:
    - A list of `[Fixes]` or an approval.
