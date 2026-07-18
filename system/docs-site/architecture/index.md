# Architecture

Beats PM Kit keeps routing and private PM state deliberately separate.

```text
Evidence from meetings, transcripts, chat, and mail
                         |
                         v
              Retrieval and context guard
                         |
                         v
        .agent/command-registry.json (routing)
                         |
                         v
       workflow -> focused skills -> validation
                         |
                         v
       local Markdown tasks, decisions, and notes
```

## Canonical Surfaces

| Surface | Responsibility |
|:---|:---|
| `.agent/command-registry.json` | Commands, execution profiles, runtime policy, and adapter routing |
| `.agent/workflows/` | Human-readable execution playbooks |
| `.agent/skills/` | Focused product-management capabilities |
| `system/scripts/` | Deterministic retrieval, migration, privacy, evaluation, and task tooling |
| `5. Trackers/` | Ignored local task state and workstream detail |

Generated manifests, routing tables, runtime adapters, and compatibility documentation are checked against the registry so they cannot drift silently.

## Execution Profiles

| Profile | Intended work |
|:---|:---|
| Fast | Retrieval, capture, help, and routine status |
| Balanced | Task reconciliation, meetings, transcripts, weekly synthesis, and communication intake |
| Deep | Strategy, consequential decisions, critical review, security, migration, and release work |

Profiles inherit the active runtime's model. Local model promotions require sanitized evaluation evidence and never change providers silently.
