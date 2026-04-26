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
| `/track`    | `staff-pm` | `task-manager`     | P0   |
| `/meet`     | `staff-pm` | `meeting-synth`    | P0   |
| `/create`   | `staff-pm` | `prd-author`       | P0   |
| `/plan`     | `staff-pm` | `roadmapping-suite` | P0   |
| `/paste`    | `staff-pm` | `inbox-processor`  | P0   |
| `/help`     | `orchestrator` | `core-utility` | P0   |

---

## 🚀 P1 — Strategic & Execution Commands (On-Demand)

| Command     | Agent      | Primary Skill      | Tier |
|:------------|:-----------|:-------------------|:-----|
| `/discover` | `strategist` | `discovery-engine` | P1   |
| `/prioritize` | `strategist` | `business-strategy-suite` | P1   |
| `/retro`    | `program-manager` | `retrospective` | P1   |
| `/vacuum`   | `cpo`      | `vacuum-protocol`  | P1   |
| `/review`   | `qa-engineer` | `test-scenarios`   | P1   |
| `/vibe`     | `orchestrator` | `system-validation` | P1   |

---

## 🛠️ P2 — Specialist Commands (Triggered)

| Command       | Agent      | Primary Skill      | Tier |
|:--------------|:-----------|:-------------------|:-----|
| `/transcript` | `ux-researcher` | `summarize-interview` | P2   |
| `/metrics`    | `data-scientist` | `metrics-finance-suite` | P2   |
| `/growth`     | `gtm-lead` | `growth-engine`    | P2   |
| `/coach`      | `career-coach` | `leadership-career-coach` | P2   |

---

_Last Sync: 2026-03-29_
