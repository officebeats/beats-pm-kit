# PRD: Beats PM "Neural Mesh" Autonomous Second Brain (v2.0)

**Project Code Name**: Antigravity Brain
**Document Status**: Final / Holistic High-Fidelity
**Author**: Antigravity AI (Strategic Product Management)
**Stakeholders**: Ernesto (Founder/Owner), Mitesh (Engineering Lead), Dom (Product)

---

## 1. Vision & Strategic Objective

To build the world’s first **autonomous, local-first AI Operating System** for Product Managers. The "Antigravity Brain" eliminates documentation latency by using a decentralized mesh of AI agents to convert high-entropy inputs (transcripts, screenshots, raw thoughts) into structured, prioritized project artifacts.

**The Goal**: Zero-manual-entry execution

---

## 2. System Architecture: The "Neural Mesh"

The system is modeled after a decentralized micro-agent architecture where agents autonomously yield control based on **Intent Detection** and **Entity Mapping**.

### 2.1 Level 0: The Kernel (Universal Protocol)

The **Kernel (`KERNEL.md`)** is the system's "operating system." It governs agent discovery and lazy-loading.

- **Protocol**: Agents must not be loaded into memory until a **Trigger Condition** is met.
- **State Source**: `STATUS.md` and `ACTION_PLAN.md` represent the current "RAM" of the system.

### 2.Level 1: The Orchestration Layer (The "Brain Stem")

#### **2.2.1 Requirements Translator (`requirements-translator.md`)**

- **Trigger**: Explicit `#` commands OR implicit task/bug detection logic.
- **Operational Requirements**:
  - **Entity Matching**: Must resolve "Who" (from `SETTINGS.md` team/boss list) and "What" (from `vault/products/` context).
  - **Context Persistence**: Inherit the last active product context if the current input is ambiguous.
  - **Autonomous Decisioning**: If confidence is >85%, write directly to target tracker. If <85%, route to `system/queue/needs-clarification.md`.
  - **Yield Logic**: Must yield to `Visual Processor` if an image/screenshot is provided.

#### **2.2.2 Meeting Synthesizer (`meeting-synth/SKILL.md`)**

- **Trigger**: `/transcript`, `/meeting`, `/call`, `/1on1`.
- **Operational Requirements**:
  - **Parallel Fan-Out**: Identify action items and dispatch them to worker agents (Boss, Bug, Eng, UX) **simultaneously**.
  - **Product Contextualization**: Identify **Product DNA** from `vault/products/` and segment summaries by product if multiple are discussed.
  - **TL;DR Protocol**: 2-3 sentences max + a high-density table of Created Items (with file IDs and deep links).
  - **File Architecture**: Auto-sort artifacts into `vault/meetings/customer-calls/`, `vault/meetings/standups/`, etc.

#### **2.2.3 Visual Processor (The "Eyes")**

- **Trigger**: Image provided or `#screenshot`.
- **Operational Requirements**:
  - **OCR & Scene Mapping**: Extract text and classify context (Slack = Comm, Figma = Design, Mobile App = QA).
  - **Handoff Package**: Prepare a package for worker agents containing: (1) Transcribed Text, (2) Visual Description, and (3) Product Context.
  - **Semantic Mapping**: If a screenshot contains "404", "Crash", or "Error", it inherits the `🔥 Critical` state and bypasses general triage.

---

## 3. The Fulfillment Layer (The "Muscle")

### 3.1 Boss Tracker (The "Executive Escalator")

- **Authority**: High-stakes request management for VIPs defined in `SETTINGS.md`.
- **SLA Rules (Hard-Coded)**:
  - **Acknowledge Phase**: Capture to `5. Trackers/critical/boss-requests.md` with a `🔥 Critical` default priority.
  - **The 48h Update Rule**: If no update is logged in the "Updates" column for 48 hours, autonomously generate a `🟠 Stale` alert in the next Brief.
  - **Escalation**: If SLAs (Acknowledge <4h, Update <48h) are breached, move item to `5. Trackers/critical/escalations.md`.

### 3.2 Bug Chaser (The "Stability Guard")

- **SLA Policy Matrix**:| Priority    | Chase Cadence | Escalation Threshold             |
  | :---------- | :------------ | :------------------------------- |
  | 🔥 Critical | Every 8 hours | 48 hours (Move to `5. Trackers/critical/`) |
  | ⚡ Now      | Bi-daily      | 72 hours                         |
  | 📌 Next     | Weekly        | 14 days                          |
- **Autonomous Action**: Scan `5. Trackers/bugs/bugs-master.md` and autonomously draft chase-messages for engineering leads in `5. Trackers/bugs/chase-log.md`.

### 3.3 Task Manager (The "State Harmonizer")

- **Lifecycle Control**: Sole writer for `ACTION_PLAN.md`.
- **Deduplication Protocol**: Compute semantic similarity against the existing list; if >80% match is found, append new context to the existing task.
- **The "Parking Lot"**: Autonomously manage `BRAIN_DUMP.md` for low-confidence or futuristic ideas.
- **Clarification Queue**: Maintain `system/queue/needs-clarification.md` for vague items lacking a clear product or owner.

### 3.4 Engineering & UX Collaborators

- **Engineering (`engineering-collab/SKILL.md`)**: Convert feedback into "Technical Spikes" (🔬) or "Architecture Decisions" (🏗️) in `5. Trackers/people/engineering-items.md`.
- **UX (`ux-collaborator/SKILL.md`)**: Track Discovery (🔍), Wireframes (📐), and Mockups (🎨) in `5. Trackers/people/ux-tasks.md`. Link screenshots/Figma URLs directly to tasks.

---

## 4. Synthesis & Intelligence Layers

### 4.1 Daily Synthesizer (The "Voice")

- **Environmental Awareness**:
  - **Morning**: Focus on Criticals + Calendar + overnight sync.
  - **EOD**: Focus on Accomplishments + Tomorrow's priorities.
- **Dashboard Owner**: Update the root `STATUS.md` dashboard on every run to reflect the current mesh state.

### 4.2 Weekly Synthesizer (The "Auditor")

- **Trigger**: Fridays @ 4 PM or `/weekly`.
- **Cleanup Protocol**:
  - Archive `[x]` tasks older than 7 days.
  - Flag `[ ]` tasks older than 14 days as `⚠️ Stale`.
- **Aggregation**: Parallel scan of ALL trackers to generate the weekly rollup in `vault/meetings/weekly-digests/`.

### 4.3 Strategy Synthesizer (The "PFC")

- **Pattern Recognition**: Identify clusters of feature requests or recurring bug hotspots.
- **Outputs**: Maintain the Decision Log and create **Opportunity Cards** in `5. Trackers/strategy/opportunities/`.

---

## 5. Document & Schema Specifications (The "Database")

Agents MUST preserve schema integrity for all Markdown trackers.

### 5.1 `5. Trackers/bugs/bugs-master.md` Schema

| ID    | Status  | Priority | Product   | Description | Reporter | Date Logged  |
| :---- | :------ | :------- | :-------- | :---------- | :------- | :----------- |
| B-XXX | `[ ]` | 🔥       | [Product] | [Context]   | [Name]   | [YYYY-MM-DD] |

### 5.2 `5. Trackers/critical/boss-requests.md` Schema

| ID     | Request   | Stakeholder | Deadline | Status  | Last Update      |
| :----- | :-------- | :---------- | :------- | :------ | :--------------- |
| BR-XXX | [Context] | [Name]      | [Date]   | `[ ]` | [Timestamp: Log] |

---

## 6. Failure Modes & Autonomous Recovery

| Scenario                        | Autonomous Response                                                                            |
| :------------------------------ | :--------------------------------------------------------------------------------------------- |
| **Ambiguous Owner**       | Default to "User" and log in `system/queue/needs-clarification.md`.                                |
| **Conflicting Deadlines** | Flag item with `⚠️ Conflict` in `ACTION_PLAN.md`.                                        |
| **Context Overload**      | Split inputs >128k tokens into "Segments," synthesize each, and then perform a "Global Merge." |
| **Fuzzy Matching**        | Use fuzzy logic for boss names (e.g., "Ricky" → Ricardo Regalado) defined in `SETTINGS.md`. |

---

## 7. Performance & Security Protocols

- **Atomic Writes**: All mutations must be atomic to prevent data corruption.
- **Source Referencing**: Every mutation must include a `Source:` link to the original raw input (e.g., `system/inbox/archive/`).
- **Privacy**: No external cloud API calls; 100% local markdown file operations.

---

**Sign-off**:
_Holistic Product Design finalized for 2026 release._
