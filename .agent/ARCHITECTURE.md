# Beats PM Kit Architecture

> Generated from `.agent/command-registry.json` and the canonical `.agent/` tree.

## Current Surface

| Surface | Count | Canonical location |
| --- | ---: | --- |
| Agents | 26 | `.agent/agents/` |
| Skills | 69 | `.agent/skills/` |
| Workflows | 44 | `.agent/workflows/` |
| Runtime adapters | 4 | Generated from the registry |

## Source Boundaries

- `.agent/command-registry.json` owns the schema-v3 harness contract, routing, aliases, execution profiles, escalation signals, and runtime policy.
- `.agent/workflows/` owns workflow behavior.
- `.agent/skills/` owns reusable PM methods.
- `MANIFEST.json`, `command-registry.lite.json`, `rules/ROUTING.md`, `CODEX_COMMANDS.md`, runtime adapters, and compatibility documentation are generated views.
- `.beats/model-policy.json` is ignored local state for explicit, evaluated model promotions.

## Execution Profiles

| Profile | Intent | Default model |
| --- | --- | --- |
| Fast | Retrieval, capture, help, and routine daily status with the minimum sufficient evidence. | `inherit` |
| Balanced | Task reconciliation, meetings, transcripts, weekly synthesis, and communication intake. | `inherit` |
| Deep | Strategy, PRDs, consequential decisions, critical review, security, and release work. | `inherit` |

## Loading Flow

```text
User request
  -> command registry
  -> one workflow and execution profile
  -> at most 5 directly relevant sources
  -> active runtime capability probe
  -> inherited model or explicit local promotion
  -> validation and durable Markdown output
```

Unknown capabilities are denied. The kit does not silently switch providers, rewrite skills, or persist model output outside ignored local evaluation storage.

## Harness Contract

- Product name: **Beats Agentic PM Harness**
- Primary runtimes: Antigravity, Codex, and Claude
- Compatibility runtimes: Gemini CLI and KiloCode
- Response profiles: `compact_operator`, `artifact`, and `verbatim`
- Context checkpoint: completed phase boundary at 65% context, or before the next phase will not fit; checkpoints append `## Checkpoint <ISO8601>` anchors and never rewrite earlier anchors
- Evidence rule: compacted context remains addressable; raw evidence is authoritative
- Optimizer rule: one change per held-out trial and human approval before promotion
