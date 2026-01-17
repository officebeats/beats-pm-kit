# Beats PM Antigravity Brain

> Instructional Memory for Gemini CLI. This file is read automatically on every session.

## System Overview

You are assisting with the **Beats PM Antigravity Brain**, a file-based knowledge management system for Product Managers. All data is stored in Markdown files.

## Folder Structure (0-5 Standard)

| Folder         | Purpose                               |
| :------------- | :------------------------------------ |
| `0. Incoming/` | Raw intake (screenshots, clipboard)   |
| `1. Company/`  | Company profiles, strategy            |
| `2. Products/` | PRDs, initiatives, product bugs       |
| `3. Meetings/` | Daily briefs, meeting notes           |
| `4. People/`   | Stakeholder directory                 |
| `5. Trackers/` | All tracking files (Flattened Ledger) |

## Key Files

- **KERNEL.md**: Universal orchestration rules (v4.7.0 - Skills Protocol).
- **SETTINGS.md**: User preferences (boss, team, products).
- **STATUS.md**: Current state dashboard.

## Agent Capabilities (Skills-Based)

The system uses **Gemini CLI Agent Skills**. Expertise is activated on-demand from `.agent/skills/`.

| Command        | Action                              |
| :------------- | :---------------------------------- |
| `#vibe`        | Activate `core-utility` diagnostics |
| `#vacuum`      | Activate `core-utility` cleanup     |
| `#day`         | Activate `daily-synth` brief        |
| `#boss`        | Activate `boss-tracker`             |
| `#bug`         | Activate `bug-chaser`               |
| `#task`        | Activate `task-manager`             |
| `#transcript`  | Activate `meeting-synth`            |
| `#prd`         | Activate `prd-author`               |
| `#strategy`    | Activate `strategy-synth`           |
| `#weekly`      | Activate `weekly-synth`             |
| `#eng`         | Activate `engineering-collab`       |
| `#ux`          | Activate `ux-collab`                |
| `#delegate`    | Activate `delegation-manager`       |
| `#stakeholder` | Activate `stakeholder-mgr`          |
| `#1on1`        | Activate `crm` sync prep            |
| `#simplify`    | Activate `code-simplifier`          |
| `#refactor`    | Activate `code-simplifier`          |
| `#cleanup`     | Activate `code-simplifier`          |
| `#update`      | Upgrade brain & latest gemini-cli   |

## Behavior Rules

1.  **Lazy-Load**: Only read `KERNEL.md`, `SETTINGS.md`, `STATUS.md` on startup. Load skills and data on-demand.
2.  **Parallel Execution**: Run multiple tools/skills simultaneously using `waitForPreviousTools: false`.
3.  **Succinct Output**: Tables over prose. No fluff.
4.  **Source Preservation**: Always preserve raw source text when extracting insights.
5.  **Parking Lot**: Log unclear input to `BRAIN_DUMP.md`.
6.  **Access Override (CRITICAL)**: Files in Folders 1-5 and configs are gitignored but **fully readable**.
    - **FALLBACK**: If `view_file` fails, IMMEDIATELY use `run_command` (e.g., `cat`) to read it.
    - **PROACTIVE**: Do not ask for permission; do not explain the error; just execute the fallback.
7.  **User Persona**: The "Defacto AI PM" (Consumer Focus). Prioritize AI solutions.
8.  **Formatting**: Use sub-bullets for detail.
9.  **Leadership resonance**: Check SETTINGS for stakeholder industry context.

## Privacy

- Files in Folders 1-5 are **local only**—never push to GitHub.
- Use `.gitkeep` files to preserve folder structure.

## Conductor Integration

Use hierarchical templates in `.agent/templates/` (e.g., `/conductor:docs/prd`).
