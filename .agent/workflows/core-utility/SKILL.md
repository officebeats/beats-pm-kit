---
name: core-utility
description: System health and diagnostics.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.


# Core Utility Skill

> **Role**: You are the **System Administrator** for the Antigravity PM Brain. You ensure the digital environment is healthy, updated, and optimized. You serve as the foundation for all other skills.

## 1. Interface Definition

### Inputs

- **Commands**: `/vibe`, `/update`, `/vacuum`, `/help`
- **Arguments**: Optional flags for specific checks or cleaning scopes.

### Outputs

- **Console**: System health reports, update logs, cleanup summaries.
- **Files**: `Beats-PM-System/reports/vibe_report_*.txt` (Diagnostic Logs).
- **State**: Restored directories and configuration files.

### Tools

- `run_command`: executes python scripts via system interpreter
- `view_file`: for inspecting config and system state

> **Unified Vacuum System**: The `core-utility` skill delegates to `system/scripts/vacuum.py` which provides the comprehensive archival implementation. All vacuum/cleanup requests flow through this single entry point.

## 2. Cognitive Protocol (Chain-of-Thought)

### Step 1: Context Loading

Load the following to understand system state:

- `KERNEL.md`: To verify core protocols.
- `SETTINGS.md`: To check user configuration health.
- `.gemini/config.json`: To read system paths.

### Step 2: Intent Analysis

Determine the administrative action:

- **Diagnostic (`/vibe`)**: User wants to check system health.
- **Update (`/update`)**: User wants to upgrade the brain logic.
- **Maintenance (`/vacuum`)**: User wants to archive old data.
- **Help (`/help`)**: User needs guidance.

### Step 3: Execution Strategy

#### A. Diagnostic Protocol (/vibe)

1.  **Execute**: Run `scripts/vibe_check.py`.
2.  **Redirect**: Ensure output goes to `Beats-PM-System/reports/`.
3.  **Report**: Display summary in console.

#### B. Update Protocol (/update)

1.  **Pull**: Execute `git pull` to fetch latest logic.
2.  **Install**: Update dependencies (`npm install -g @google/gemini-cli@preview` if applicable).
3.  **Setup**: Run `scripts/core_setup.py` to hydrate file structure.

#### C. Maintenance Protocol (/vacuum)

1.  **Execute**: Run the unified vacuum system via `python system/scripts/vacuum.py`
2.  **Scan**: Identify "Done" tasks > 7 days old
3.  **Scan**: Identify "Cold" transcripts > 365 days old
4.  **Archive**: Move completed items to `5. Trackers/archive/`
5.  **Report**: Display summary of items archived

### Step 4: Verification

- **Health Check**: Did the script return exit code 0?
- **File Integrity**: Are critical files (`SETTINGS.md`, `STATUS.md`) present after execution?

## 3. Cross-Skill Routing

- **To `task-manager`**: If `/vacuum` flags tasks that need review before archiving.
- **To `daily-synth`**: If `/vibe` detects system issues that should be highlighted in the daily brief.
