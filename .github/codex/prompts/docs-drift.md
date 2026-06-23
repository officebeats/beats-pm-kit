# Codex Docs Drift Check

Compare public docs against the generated inventory and command registry.

Check:
- README counts match `system/scripts/feature_inventory.py --json`
- `system/docs/codex.md` reflects Codex-first behavior
- no stale Antigravity-first claims remain in public Codex docs
- privacy language is local-first, not absolute cloud/privacy claims

Return findings only. Do not modify files.
