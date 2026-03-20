# Unified Routing Table

> **Single Source of Truth** for all command → agent → skill mappings.
> Referenced by GEMINI.md, intelligent-routing, and ARCHITECTURE.md.

> [!CAUTION]
> All workflows in this table are **PROTECTED CORE**. Never remove, archive, or rename any workflow file during updates, vacuums, or migrations.

---

## Core PM Playbooks

| Command | Purpose | Agent | Primary Skill | Priority |
|:--|:--|:--|:--|:--|
| `/boss` | Friday 1:1 prep | CPO | `boss-tracker` | P0 |
| `/day` | Daily briefing | CPO | `daily-synth` | P0 |
| `/track` | Battlefield View | Staff PM | `task-manager` | P0 |
| `/meet` | Transcript → Action Items | Staff PM | `meeting-synth` | P0 |
| `/create` | Document Factory | Staff PM | `prd-author` | P0 |
| `/plan` | Strategic War Room | Strategist | `okr-manager` | P1 |
| `/retro` | Sprint Retrospective | Program Manager | `retrospective` | P1 |
| `/vacuum` | System Optimization | CPO | `vacuum-protocol` | P1 |
| `/fan-out` | Parallel Agent Dispatch | CPO | Orchestrator | P1 |
| `/sprint` | Sprint Plan Generation | Program Manager | `sprint-plan` | P1 |
| `/discover` | Product Discovery & OST | Staff PM | `discovery-coach` | P1 |
| `/prioritize` | Backlog Scoring (RICE) | Staff PM | `prioritization-engine` | P1 |
| `/paste` | Clipboard → Triage | Staff PM | `inbox-processor` | P0 |
| `/review` | Quality Control | Tech Lead | — | P1 |
| `/regression` | CI Tests | QA Engineer | `system-validation` | P2 |
| `/help` | User Manual | System | — | P2 |
| `/update` | Pull Latest Kit Version | System | `core-utility` | P0 |

## Alias Map (Antigravity ↔ Slash)

| Hash Command | Slash Equivalent |
|:--|:--|
| `#paste` | `/paste` |
| `#transcript` | `/meet` |
| `#day` | `/day` |
| `#plan` | `/plan` |
| `#meet` | `/meet` |
| `#review` | `/review` |

## Legacy Aliases (from root GEMINI.md)

| Legacy Command | Maps To | Skill |
|:--|:--|:--|
| `/vibe` | `/vacuum` | `core-utility` |
| `/bug` | `/track` | `bug-chaser` |
| `/task` | `/track` | `task-manager` |
| `/transcript` | `/meet` | `meeting-synth` |
| `/prd` | `/create` | `prd-author` |
| `/strategy` | `/plan` | `chief-strategy-officer` |
| `/weekly` | `/day` | `weekly-synth` |
| `/simplify` | `/review` | `code-simplifier` |
| `/refactor` | `/review` | `code-simplifier` |
| `/cleanup` | `/vacuum` | `vacuum-protocol` |

---

_Last updated: 2026-03-18 | Version 10.0.1_
