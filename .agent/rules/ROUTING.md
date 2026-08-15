# Beats PM Kit Routing

> Generated from `.agent/command-registry.json` by `system/scripts/generate_registry_docs.py`.
> Edit the registry, never this file.

The registry is the only routing source of truth. Runtime adapters and this human-readable table are derived views.

| Command | Profile | Aliases | Runtime adapter |
| --- | --- | --- | --- |
| `/accuracy` | Deep | — | Dispatch only |
| `/archive` | Fast | — | Dispatch only |
| `/beats-comms` | Balanced | — | Skill `beats-comms` |
| `/beats-slack` | Balanced | — | Skill `beats-slack` |
| `/beats-teams` | Balanced | — | Skill `beats-teams` |
| `/boss` | Deep | — | Skill `beats-boss` |
| `/build` | Balanced | — | Dispatch only |
| `/challenge` | Deep | — | Dispatch only |
| `/chat` | Fast | — | Dispatch only |
| `/context` | Fast | — | Dispatch only |
| `/create` | Deep | — | Skill `beats-create` |
| `/day` | Fast | `/status`, `/morning`, `/brief`, `/now` | Skill `beats-day` |
| `/deck` | Balanced | — | Skill `beats-deck` |
| `/discover` | Deep | — | Dispatch only |
| `/fan-out` | Deep | — | Dispatch only |
| `/find` | Fast | — | Skill `beats-find` |
| `/handoff` | Balanced | — | Dispatch only |
| `/help` | Fast | — | Dispatch only |
| `/improve-plan` | Deep | — | Dispatch only |
| `/intel` | Balanced | — | Dispatch only |
| `/interview` | Deep | — | Dispatch only |
| `/maintain` | Balanced | — | Dispatch only |
| `/meet` | Balanced | — | Skill `beats-meet` |
| `/memory` | Balanced | `/reflect` | Skill `beats-memory` |
| `/obsidian` | Fast | — | Skill `beats-obsidian` |
| `/office-cli` | Fast | — | Skill `beats-office-cli` |
| `/pack` | Fast | — | Skill `beats-pack` |
| `/manager-weekly-update` | Deep | — | Dispatch only |
| `/paste` | Fast | — | Skill `beats-paste` |
| `/plan` | Deep | — | Skill `beats-plan` |
| `/prep` | Balanced | — | Dispatch only |
| `/prioritize` | Deep | — | Dispatch only |
| `/regression` | Balanced | — | Dispatch only |
| `/retro` | Balanced | — | Dispatch only |
| `/review` | Deep | — | Skill `beats-review` |
| `/sop` | Balanced | — | Skill `beats-sop` |
| `/sprint` | Balanced | — | Dispatch only |
| `/start` | Fast | — | Dispatch only |
| `/team` | Deep | — | Dispatch only |
| `/track` | Balanced | — | Skill `beats-track` |
| `/transcript` | Balanced | — | Skill `beats-transcript` |
| `/update` | Deep | — | Skill `beats-update` |
| `/vacuum` | Deep | `/cleanup` | Skill `beats-vacuum` |
| `/vibe` | Fast | — | Skill `beats-vibe` |
| `/week` | Balanced | — | Skill `beats-week` |

## Escalation

Conflicting evidence, high-stakes decisions, external mutations, broad changes, and failed validation escalate to Deep. Runtime model defaults remain inherited; explicit promotions stay local and evidence-gated.
