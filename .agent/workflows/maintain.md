---
description: Refresh local indexes, validate adapters, run local task triage, and report kit health without mutating source systems.
---

> **Compatibility Directive**: The active runtime is selected by versioned capability probes. Model defaults remain inherited and explicit promotions stay local and evidence-gated.

# /maintain - Local Kit Maintenance

Use this workflow when the user asks to refresh, validate, optimize, or maintain the local Beats PM kit.

## Contract

- Local-only by default.
- Do not read or mutate Slack, Teams, Outlook, Calendar, Jira, Confluence, Trello, or email unless the user provides a named read-only source window and explicitly asks for that source.
- Generated cache/wiki outputs stay under ignored local paths.
- Report what changed, what stayed local, and which follow-up commands are useful.

## Steps

1. Refresh the deterministic context index and optional Markdown wiki:

```bash
python3 system/scripts/context_router.py build --write-wiki --json
```

2. Inspect the active runtime, supported capabilities, execution profiles, and local model overrides:

```bash
python3 system/scripts/model_policy.py status --json
```

3. Regenerate every registry-derived surface and runtime adapter, then validate integrity:

```bash
python3 system/scripts/sync_cli_adapters.py
```

```bash
python3 system/scripts/command_integrity.py --require-generated
```

4. Run the deterministic sanitized model evaluation used by CI:

```bash
python3 system/scripts/model_eval.py run --mode offline --json
```

5. Run local task triage:

```bash
python3 system/scripts/task_master_triage.py --apply
```

6. Run context health:

```bash
python3 system/scripts/context_health.py
```

7. Summarize:
   - context index status and file count
   - command integrity status
   - task triage report path and top questions
   - health warnings
   - any skipped live-source reads
   - active runtime, version, capabilities, and model-policy warnings
   - offline evaluation quality and safety-gate status

## Opt-In Live Model Comparison

Run this only when the user explicitly asks to compare a candidate. Live runs use sanitized fixtures, execute exactly three times per scenario, and keep raw output under ignored `.beats/evals/`:

```bash
python3 system/scripts/model_eval.py run --mode live --runtime <runtime> --profile <fast|balanced|deep> --model <candidate-id> --allow-live --repeats 3 --json
```

Compare matching baseline and candidate result files, saving the recommendation locally:

```bash
python3 system/scripts/model_eval.py compare --baseline <baseline.json> --candidate <candidate.json> --json > .beats/evals/comparison.json
```

Promote only when that comparison recommends the exact runtime/profile/model and every safety gate passed:

```bash
python3 system/scripts/model_policy.py promote <runtime> <profile> <candidate-id> --evaluation .beats/evals/comparison.json --json
```

Reset with a backup using `python3 system/scripts/model_policy.py reset --json`. Never automatically rewrite a skill, switch provider, or promote from unevaluated output.
