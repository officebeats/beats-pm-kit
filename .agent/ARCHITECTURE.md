# Beats PM Kit Architecture

> Generated from `.agent/command-registry.json` and the canonical `.agent/` tree.

## Current Surface

| Surface | Count | Canonical location |
| --- | ---: | --- |
| Agents | 22 | `.agent/agents/` |
| Skills | 74 | `.agent/skills/` |
| Workflows | 44 | `.agent/workflows/` |
| Runtime adapters | 5 | Generated from the registry |

## Source Boundaries

- `.agent/command-registry.json` owns routing, aliases, execution profiles, escalation signals, and runtime policy.
- `.agent/workflows/` owns workflow behavior.
- `.agent/skills/` owns reusable PM methods.
- `MANIFEST.json`, `rules/ROUTING.md`, `CODEX_COMMANDS.md`, runtime adapters, and compatibility documentation are generated views.
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
  -> workflow and execution profile
  -> minimum required skills and evidence
  -> active runtime capability probe
  -> inherited model or explicit local promotion
  -> validation and durable Markdown output
```

Unknown capabilities are denied. The kit does not silently switch providers, rewrite skills, or persist model output outside ignored local evaluation storage.
