# Beats Agentic PM Harness

Beats is a local-first, cross-runtime harness for evidence-backed product-management workflows. `.agent/` is canonical; Antigravity, Codex, and Claude are primary runtimes. Gemini CLI and KiloCode are generated compatibility outputs.

## Defensible scope

The core includes:

- one-level command and skill routing;
- bounded, loss-aware context selection;
- local tool execution and durable PM state;
- approval and destructive-action gates;
- retry, recovery, checkpoint, and handoff rules;
- workflow quality evaluation and token telemetry;
- a human-approved, held-out harness optimizer;
- generated cross-runtime adapters with parity checks.

The core does not claim model hosting/training, a standalone general-purpose agent runtime, autonomous publishing, a universal second-brain UI, or hand-maintained support for every AI client. Generic skills remain directly discoverable but are not promoted into primary PM command routing without a concrete use case.

## Execution loop

```text
route
  -> load bounded context
  -> act with least-privilege tools
  -> checkpoint at a completed phase boundary when needed
  -> verify against the workflow contract and raw evidence
  -> persist artifact and trajectory trace
  -> hand off explicit state and next action
```

Resolve a command or skill:

```bash
python3 system/scripts/harness_registry.py resolve /create
python3 system/scripts/harness_registry.py resolve workshop-facilitation
python3 system/scripts/harness_registry.py doctor
```

The compact discovery registry contains all command IDs, aliases, and skill IDs. Selection opens one workflow or skill directly; selected entrypoints may point to support files, but there is no nested routing hierarchy.

Identity, safety, and routing remain a stable prompt prefix. Dynamic task evidence is appended afterward, and tool candidates use deterministic ordering so provider caches can be reused. Cold and warm trajectories are measured separately.

## Context budgets

| Surface | Maximum estimated tokens |
| --- | ---: |
| Runtime bootstrap | 1,500 |
| Complete discovery registry | 2,500 |
| Individual skill entrypoint | 2,500 |
| Initial command context before task sources | 6,000 |

The budget check uses a deterministic UTF-8 byte estimate so CI does not depend on a provider tokenizer. It is deliberately conservative and stable across runtimes.

## Loss-aware context

`context_store.py` archives full payloads under ignored `.beats/context/` with stable IDs, SHA-256, source, timestamp, producer command, byte count, and token estimate. Compact views retain high-signal lines and a deterministic retrieval command. Retrieval hash-verifies the original bytes.

`context_checkpoint.py` permits compaction only after discovery, planning, creation, or verification. A checkpoint must preserve the goal, decisions, exact stakeholder language, source IDs, artifacts, open questions, failed attempts, verification state, next action, most recent complete turn, and intact tool-call/result pairs.

Raw retrieval is mandatory before quotations, customer commitments, legal language, security findings, and final citations.

## Knowledge compiler

`knowledge_compiler.py` maintains four controlled layers:

| Layer | Authorized writer | Authority |
| --- | --- | --- |
| `raw` | source capture | authoritative evidence, immutable after capture |
| `compiled` | knowledge compiler | current topic navigation |
| `digest` | workflow digest | briefs and handoffs |
| `state` | task/status workflows | current priorities, projects, decisions, and open loops |

Compiled and digest pages require raw paths and current SHA-256 hashes. Initial retrieval is capped at five compiled sources and one direct evidence hop. `/vacuum`, explicit maintenance, or detected source change may refresh the compiler; no cloud scheduler is used.

## Response profiles

- `compact_operator`: terse progress, routine status, and tool narration.
- `artifact`: complete polished deliverables with the workflow's required structure.
- `verbatim`: exact transcript, requirement, commitment, and quotation language.

## Measurement and optimizer

`harness_telemetry.py` records uncached input, cached input, cache writes, output, tool payload, processed and estimated billable tokens, estimated cost, turns, retries, compactions, source loads, elapsed time, quality, runtime, model, effort, registry version, and cache state.

`harness_optimizer.py` changes exactly one allowlisted surface per experiment, requires matching held-out scenarios, writes an ignored ledger, and never promotes automatically. It cannot change permissions, rubrics, source requirements, workflow intent, or evaluation fixtures. A candidate must preserve quality per scenario, achieve the required median token reduction, stay within the per-scenario regression limit, and avoid turn inflation before a human may approve it.

Export completed baseline and candidate trajectory ledgers into matched runtime/cache/scenario payloads before evaluation:

```bash
python3 system/scripts/harness_telemetry.py --ledger <baseline.jsonl> export --label baseline > <baseline.json>
python3 system/scripts/harness_telemetry.py --ledger <candidate.jsonl> export --label candidate > <candidate.json>
python3 system/scripts/harness_optimizer.py --experiment <experiment.json> --baseline <baseline.json> --candidate <candidate.json>
```

Cold-cache and warm-cache runs must be compared separately. The sanitized acceptance corpus covers the eleven primary commands, source-heavy work, long-session continuation, exact wording, blocked external writes, artifact compatibility, privacy, and raw-source retrieval after compaction.
