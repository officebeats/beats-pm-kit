# Codex Release Readiness

Check whether this Beats PM Kit branch is ready to release.

Verify:
- `python system/scripts/feature_inventory.py --json`
- `python system/scripts/adapter_guard.py --mode check`
- Codex-first docs mention runtime priority, compatibility runtimes, local-first privacy, and promoted command count
- generated adapters are current

Return a concise pass/fail report with evidence. Do not modify files.
