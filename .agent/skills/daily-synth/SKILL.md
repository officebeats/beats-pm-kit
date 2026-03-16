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

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


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

``> **Formatting Instructions**: Read the template found at ssets/template_1.md and format your output exactly as shown.``

## Boundary

- **This skill handles**: Single-day tactical planning — morning priorities, midday pivots, EOD audits.
- **NOT for**: Weekly/monthly rollups (use `weekly-synth`). Meeting transcript synthesis (use `meeting-synth`).
