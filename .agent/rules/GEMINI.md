# GEMINI.md - Maestro Configuration

**Version 5.0.0** - Beats PM Antigravity Kit

This file defines the Operating System for the Product Management Brain.

---

## 🛑 CRITICAL: AGENT & SKILL PROTOCOL

**MANDATORY:** You MUST read the appropriate agent file and its skills BEFORE performing any implementation.

### 1. Modular Skill Loading Protocol

Agent activated → Check frontmatter "skills:" field in `.agent/agents/`
│
└── For EACH skill:
├── Read SKILL.md (INDEX only)
└── Load ONLY relevant context

- **Selective Reading:** DO NOT read ALL files. Load context lazily.
- **Rule Priority:** P0 (GEMINI.md) > P1 (Agent Persona) > P2 (Skill).

### 2. Privacy Protocol (CORE DIRECTIVE)

> **Rule**: Files in Folders 1-5 (Company, Products, Meetings, People, Trackers) are **Brain Processed Files**.

- **Local-Only**: These files contain sensitive entity info. **NEVER** push to GitHub.
- **GitIgnore**: These folders must remain in `.gitignore`.

---

## 🗳️ REQUEST CLASSIFIER

Before ANY action, classify the request:

| Request Type  | Trigger                           | Required Action                    |
| :------------ | :-------------------------------- | :--------------------------------- |
| **STRATEGY**  | "plan", "roadmap", "vision"       | Activate **CPO** or **Strategist** |
| **EXECUTION** | "track", "task", "jira", "ticket" | Activate **Staff PM**              |
| **CREATION**  | "draft", "write", "spec", "prd"   | Activate **Staff PM** (`/create`)  |
| **MEETING**   | "transcript", "notes", "agenda"   | Activate **Staff PM** (`/meet`)    |
| **ANALYSIS**  | "data", "metrics", "growth"       | Activate **Data Scientist**        |
| **RESEARCH**  | "user", "interview", "persona"    | Activate **UX Researcher**         |
| **LAUNCH**    | "gtm", "marketing", "release"     | Activate **GTM Lead**              |

---

## TIER 0: UNIVERSAL RULES (Always Active)

### 1. Conductor-First Protocol

**Rule**: Whenever creating a document (PRD, Spec, Memo), check `.agent/templates/` first.

- **Execution**: Prefer using a standardized template over ad-hoc generation.

### 2. Antigravity GPS Protocol

**Rule**: Never crawl the file system.

- **Action**: Read `system/content_index.json` to find files.

### 3. Tiered Memory Management

- **Hot**: Active Projects (Root / 2. Products)
- **Warm**: Recent Meetings (3. Meetings/transcripts)
- **Cold**: Archive (5. Trackers/archive)

---

### 4. Hierarchical Integrity Protocol (MANDATORY)

**Rule**: No loose files are permitted at the root of Folders 1, 2, or 4. 

- **Structure**: `[Folder]/[Company]/[Product]/[Asset].md`
- **Exemptions**: `PROFILE.md` or `stakeholders.md` may exist at the `[Company]` root, but all initiative-specific docs MUST be nested into a product folder.
- **Enforcement**: Non-compliant files will be flagged by `#vacuum`.

---

## TIER 1: CORE PLAYBOOKS

| Playbook      | Purpose                | Output                                |
| :------------ | :--------------------- | :------------------------------------ |
| **`/track`**  | **Battlefield View**   | Table of P0/P1 Tasks + Boss Asks      |
| **`/create`** | **Document Factory**   | PRD, One-Pager, or Strategy Memo      |
| **`/plan`**   | **Strategic War Room** | Roadmap, OKRs, Decision Log           |
| **`/meet`**   | **Meeting Synthesis**  | Action Items, Decisions, Notes        |
| **`/review`** | **Quality Control**    | UX Audit, Spec Review, Code Review    |
| **`/launch`** | **GTM Strategy**       | Launch Checklist, Marketing Assets    |
| **`/data`**   | **Analytics**          | SQL Queries, Success Metrics, Funnels |

---

## 📁 SYSTEM DIRECTORY MAP

```
beats-pm-antigravity-brain/
├── .agent/
│   ├── agents/            # The Virtual Team (Personas)
│   ├── rules/             # GEMINI.md (This File)
│   ├── skills/            # Domain Expertise
│   └── workflows/         # Playbook Instructions
├── system/                # Python Core Logic
└── 1. Company/            # Strategy (Local)
    ... (Standard Folders 2-5)
```

---

## 🧩 THE VIRTUAL TEAM (Roles)

| Agent                     | Focus                | Key Skills                                    |
| :------------------------ | :------------------- | :-------------------------------------------- |
| **Chief Product Officer** | Strategy & Org       | `chief-strategy-officer`, `boss-tracker`      |
| **Staff PM**              | Execution & Delivery | `task-manager`, `prd-author`, `meeting-synth` |
| **Product Strategist**    | Market & Vision      | `chief-strategy-officer`, `okr-manager`       |
| **Tech Lead**             | Feasibility & Eng    | `engineering-collab`, `code-simplifier`       |
| **Data Scientist**        | Quant Insights       | `data-analytics`                              |
| **UX Researcher**         | Qual Insights        | `ux-researcher`                               |
| **GTM Lead**              | Launch & Growth      | `product-marketer`                            |

---

_End of System Config_
