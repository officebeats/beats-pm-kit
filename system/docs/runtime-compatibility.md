# Runtime and Model Compatibility

> Generated from `.agent/command-registry.json`. Edit the registry, not this table.

| Runtime | Adapter entrypoint | Profiles | Default model | Explicit promotion |
| --- | --- | --- | --- | --- |
| Antigravity | `.agent/rules/GEMINI.md` | Fast, Balanced, Deep | `inherit` | `.beats/model-policy.json` |
| Codex | `AGENTS.md` | Fast, Balanced, Deep | `inherit` | `.beats/model-policy.json` |
| Claude | `CLAUDE.md` | Fast, Balanced, Deep | `inherit` | `.beats/model-policy.json` |
| Gemini | `GEMINI.md` | Fast, Balanced, Deep | `inherit` | `.beats/model-policy.json` |

Active-runtime probes determine capabilities and versions. An unavailable or ambiguous runtime fails closed. Missing Deep support retains the active runtime's inherited model and emits a downgrade warning; it never causes a silent provider switch.
