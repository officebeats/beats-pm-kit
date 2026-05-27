---
source: .agents\rules\ROUTING.md
type: antigravity
---

# ROUTING.md — Unified Agent & Skill Routing Table (SSOT)

> **Source of Truth** for command → agent → skill mapping.
> All agents (Gemini CLI, Antigravity, Claude Code, Codex) MUST respect this routing.

---

## 🚫 GLOBAL SKILL FILTER

**CRITICAL RULE:** Only use skills related to **Software Development**, **Product Management**, or **Task Management**. 
Disregard and ignore ALL scientific, medical, or other unrelated global skills (e.g., bioRxiv, PubChem, clinical-reports, etc.).

---

## 🏗️ P0 — Core PM Commands (Eager Load)

| Command     | Agent      | Primary Skill      | Tier |
|:------------|:-----------|:-------------------|:-----|
| `/boss`     | `cpo`      | `boss-tracker`     | P0   |
| `/day`      | `staff-pm` | `daily-synth`      | P0   |
| `/track`    | `staff-pm` | `pm-decision-router` -> `task-manager` | P0   |
| `/meet`     | `staff-pm` | `meeting-synth`    | P0   |
| `/create`   | `staff-pm` | `pm-decision-router` -> `prd-author` | P0   |
| `/plan`     | `staff-pm` | `pm-decision-router` -> `roadmapping-suite` / `product-strategy-suite` | P0   |
| `/paste`    | `staff-pm` | `pm-decision-router` -> `inbox-processor` -> `task-manager` | P0   |
| `/help`     | `orchestrator` | `core-utility` | P0   |

---

## 🚀 P1 — Strategic & Execution Commands (On-Demand)

| Command     | Agent      | Primary Skill      | Tier |
|:------------|:-----------|:-------------------|:-----|
| `/discover` | `strategist` | `pm-decision-router` -> `discovery-engine` | P1   |
| `/prioritize` | `strategist` | `pm-decision-router` -> `roadmapping-suite` | P1   |
| `/retro`    | `program-manager` | `retrospective` | P1   |
| `/vacuum`   | `cpo`      | `vacuum-protocol`  | P1   |
| `/review`   | `qa-engineer` | `test-scenarios`   | P1   |
| `/beats-comms` | `staff-pm` | `pm-decision-router` -> `chat-transcript-archive` | P1 |
| `/vibe`     | `orchestrator` | `system-validation` | P1   |

---

## 🛠️ P2 — Specialist Commands (Triggered)

| Command       | Agent      | Primary Skill      | Tier |
|:--------------|:-----------|:-------------------|:-----|
| `/transcript` | `staff-pm` | `pm-decision-router` -> `meeting-synth` -> `task-manager` | P2   |
| `/metrics`    | `data-scientist` | `metrics-finance-suite` | P2   |
| `/growth`     | `gtm-lead` | `growth-engine`    | P2   |
| `/coach`      | `career-coach` | `leadership-career-coach` | P2   |

---

_Last Sync: 2026-03-29_
