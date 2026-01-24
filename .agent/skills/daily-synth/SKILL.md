---
name: daily-synth
description: Daily briefing and planning.
triggers:
  - "/day"
  - "/status"
  - "/morning"
  - "/lunch"
  - "/eod"
  - "/brief"
version: 3.2.0 (Native Optimized)
author: Beats PM Brain
---

# Daily Synthesizer Skill

> **Role**: Chief of Staff per `KERNEL.md`. Ingest signal -> Present tactical battle plan.

## 1. Native Interface

- **Inputs**: `/day`, `/status`, `/morning`. System Time. Daisy-Chain Manifests.
- **Tools**: `view_file` (`STATUS.md`, Trackers), `run_command` (`date`), `find_by_name`.

## 2. Cognitive Protocol

1.  **Hydrate**: Read `STATUS.md`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/critical/boss-requests.md`, `5. Trackers/bugs/bugs-master.md`.
2.  **Phase Logic**:
    - **Morning (<12:00)**: Define **"Big Rocks"** (Top 3 Absolutes). Temporal Logic: Focus on output.
    - **Midday**: Pivot check.
    - **EOD (>16:00)**: Audit shipped items. Update `STATUS.md`.
3.  **Context Grouping**:
    - 📓 **Journal**: `3. Meetings/` + `0. Incoming/`.
    - 🔨 **Work**: `2. Products/` + `5. Trackers/`.
4.  **Routing**:
    - `STATUS.md` stale (>24h)? -> Suggest `/update`.
    - Boss Ask Red? -> Suggest `/boss` update.

## 3. Output Format

```markdown
# 📅 [Date] Daily Briefing

> **Focus**: [Theme]

## 🚨 Blocking / Risk

- [ ] [Critical Item]

## 🪨 Big Rocks (Top 3)

| Priority | Task   | Status | Output |
| :------- | :----- | :----- | :----- |
| P0       | [Task] | ⏳     | [Link] |

## 📅 Schedule

- [Time]: [Event]

## 🧭 Exec Snapshot (FAANG/BCG)

- **Metric Movement**: [Metric → Delta]
- **Top Risk**: [Risk + mitigation]
- **Decision Needed**: [Decision + owner]
```
