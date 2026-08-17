# Beats PM Kit Routing

> Generated from `.agent/command-registry.json` by `system/scripts/generate_registry_docs.py`.
> Edit the registry, never this file.

The registry is the only routing source of truth. Runtime adapters and this human-readable table are derived views.

| Command | Profile | Aliases | Runtime adapter |
| --- | --- | --- | --- |
| `/beats-comms` | Balanced | — | Skill `beats-comms` |
| `/beats-slack` | Balanced | — | Skill `beats-slack` |
| `/beats-teams` | Balanced | — | Skill `beats-teams` |
| `/boss` | Deep | — | Skill `beats-boss` |
| `/challenge` | Deep | — | Dispatch only |
| `/create` | Deep | — | Skill `beats-create` |
| `/day` | Fast | `/status`, `/morning`, `/brief`, `/now` | Skill `beats-day` |
| `/deck` | Balanced | — | Skill `beats-deck` |
| `/find` | Fast | — | Skill `beats-find` |
| `/help` | Fast | — | Dispatch only |
| `/meet` | Balanced | — | Skill `beats-meet` |
| `/memory` | Balanced | `/reflect` | Skill `beats-memory` |
| `/obsidian` | Fast | — | Skill `beats-obsidian` |
| `/office-cli` | Fast | — | Skill `beats-office-cli` |
| `/pack` | Fast | — | Skill `beats-pack` |
| `/paste` | Fast | — | Skill `beats-paste` |
| `/plan` | Deep | — | Skill `beats-plan` |
| `/review` | Deep | — | Skill `beats-review` |
| `/sop` | Balanced | — | Skill `beats-sop` |
| `/track` | Balanced | — | Skill `beats-track` |
| `/transcript` | Balanced | — | Skill `beats-transcript` |
| `/update` | Deep | — | Skill `beats-update` |
| `/vacuum` | Deep | `/cleanup` | Skill `beats-vacuum` |
| `/vibe` | Fast | — | Skill `beats-vibe` |
| `/week` | Balanced | — | Skill `beats-week` |

## Escalation

Conflicting evidence, high-stakes decisions, external mutations, broad changes, and failed validation escalate to Deep. Runtime model defaults remain inherited; explicit promotions stay local and evidence-gated.

## Hidden / Legacy Commands

Decluttered from the discovery table above because they are dispatch-only utilities superseded by the Diamond 6 workflow. They are not deleted: each workflow file still exists under `.agent/workflows/` and resolves normally when a user types the exact command.

`/accuracy`, `/archive`, `/build`, `/chat`, `/context`, `/discover`, `/fan-out`, `/handoff`, `/improve-plan`, `/intel`, `/interview`, `/maintain`, `/prep`, `/prioritize`, `/regression`, `/retro`, `/sprint`, `/start`, `/team`
