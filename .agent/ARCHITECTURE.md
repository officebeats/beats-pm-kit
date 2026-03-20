# Antigravity Kit Architecture

> Comprehensive AI Agent Capability Expansion Toolkit

---

## 📋 Overview

Antigravity Kit is a modular system consisting of:

- **24 Specialist Agents** - Role-based AI personas
- **50 Skills** - Domain-specific knowledge modules
- **16 Workflows** - Slash command procedures

> **Routing:** See [ROUTING.md](rules/ROUTING.md) for the unified command → agent → skill mapping.
> **Manifest:** See [MANIFEST.json](MANIFEST.json) for the machine-readable index with token budgets.

---

## 🏗️ Directory Structure

```plaintext
.agent/
├── ARCHITECTURE.md          # This file
├── MANIFEST.json            # Machine-readable skill/agent index
├── agents/                  # 24 Specialist Agents
├── skills/                  # 50 Skills (P0/P1/P2 tiered)
├── workflows/               # 16 Slash Commands
├── rules/                   # Global Rules + ROUTING.md
│   ├── GEMINI.md            # Canonical system config
│   └── ROUTING.md           # Unified routing table (SSOT)
├── templates/               # Document templates (JIT loaded)
└── scripts/                 # Validation scripts
```

> **Note:** `.agents/` is a symlink to `.agent/` for backward compatibility.

---

## 🤖 Agents (24)

### PM Core (P0 — loaded eagerly)

| Agent | Focus | Key Skills |
|:--|:--|:--|
| `orchestrator` | Multi-agent coordination | parallel-agents, behavioral-modes |
| `cpo` | Strategy & Org | chief-strategy-officer, boss-tracker, vacuum-protocol |
| `staff-pm` | Execution & Delivery | task-manager, prd-author, meeting-synth |

### PM Extended (P1 — loaded on demand)

| Agent | Focus | Key Skills |
|:--|:--|:--|
| `strategist` | Market & Vision | chief-strategy-officer, okr-manager |
| `program-manager` | Governance & Releases | dependency-tracker, retrospective |
| `tech-lead` | Feasibility & Eng | engineering-collab, code-simplifier |
| `data-scientist` | Quant Insights | data-analytics |
| `ux-researcher` | Qual Insights | ux-researcher |
| `gtm-lead` | Launch & Growth | product-marketer |
| `qa-engineer` | Quality Assurance | system-validation |
| `career-coach` | PM Career Growth | leadership-career-coach |

### Engineering Specialists (P2 — loaded only when triggered)

| Agent | Focus |
|:--|:--|
| `frontend-specialist` | Web UI/UX |
| `backend-specialist` | API & Business Logic |
| `database-architect` | Schema & SQL |
| `mobile-developer` | iOS/Android/RN |
| `devops-engineer` | CI/CD & Docker |
| `security-auditor` | Security Compliance |
| `penetration-tester` | Offensive Security |
| `debugger` | Root Cause Analysis |
| `performance-optimizer` | Speed & Web Vitals |
| `seo-specialist` | Ranking & Visibility |
| `documentation-writer` | Docs & Manuals |
| `code-archaeologist` | Legacy & Refactoring |
| `explorer-agent` | Codebase Analysis |

---

## 🧩 Skills (50) — Priority Tiered

Skills are loaded **Just-In-Time** based on priority tier:

- **P0 (Core):** 9 skills — loaded eagerly for daily PM workflows
- **P1 (Extended):** 19 skills — loaded on command invocation
- **P2 (Specialist):** 22 skills — loaded only when explicitly triggered

> See [MANIFEST.json](MANIFEST.json) for complete skill registry with byte sizes and token budgets.

### Top Skills by Usage

| Skill | Size | Tier | When Used |
|:--|:--|:--|:--|
| `task-manager` | 2.3KB | P0 | `/track`, `/task` |
| `daily-synth` | 1.7KB | P0 | `/day` |
| `boss-tracker` | 2.6KB | P0 | `/boss` |
| `inbox-processor` | 6.1KB | P0 | `/paste` |
| `prd-author` | 1.8KB | P0 | `/create` |
| `intelligent-routing` | 10.6KB | P0 | Auto-routing |

---

## 🎯 Skill Loading Protocol

```plaintext
User Request → ROUTING.md lookup → Agent file → SKILL.md (index only) → JIT templates
                                                    ↓
                                            Read references/ (only if needed)
                                                    ↓
                                            Read scripts/ (only if needed)
```

### Key Principles

1. **Index, don't inline** — SKILL.md is an index; templates live in `assets/`
2. **Single source of truth** — One routing table (`ROUTING.md`), one manifest (`MANIFEST.json`)
3. **JIT everything** — Templates, references, and scripts load only when skill executes
4. **Priority tiering** — P0 eager, P1/P2 lazy

### Skill Structure

```plaintext
skill-name/
├── SKILL.md           # (Required) Metadata & instructions (<500 lines ideal)
├── assets/            # (Optional) Templates (JIT loaded)
├── scripts/           # (Optional) Python/Bash scripts
└── references/        # (Optional) Docs, schemas
```

---

## 📊 Statistics

| Metric | Value |
|:--|:--|
| **Total Agents** | 24 |
| **Total Skills** | 50 |
| **Total Workflows** | 16 |
| **Total Skill Surface** | ~391KB |
| **P0 Core Surface** | ~33KB |
| **Architecture Version** | 10.0.0 |

---

_Last updated: 2026-03-18_
