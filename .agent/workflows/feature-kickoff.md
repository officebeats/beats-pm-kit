---
description: Kickoff a new feature. Chains PRD creation -> Task Breakdown -> Sprint Planning.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Feature Kickoff Workflow

This workflow automates the "Idea to Execution" pipeline using the Daisy-Chain Protocol.

## Steps

1.  **Draft the Spec**
    - **Agent**: `prd-author`
    - **Command**: `/prd "Draft a PRD for [FeatureName]. Context: [Context]"`
    - **Output**: `2. Products/[Product]/[Feature]/PRD.md`

2.  **Break Down Tasks**
    - **Agent**: `task-manager`
    - **Command**: `/task "Break down the PRD at [PreviousOutput] into engineering tasks"`
    - **Input**: `[OUTPUT_MANIFEST].primary` from Step 1
    - **Output**: `5. Trackers/TASK_MASTER.md` (Updated)

3.  **Identify Risks (Pre-Mortem)**
    - **Agent**: `decision-maker`
    - **Command**: `/decide "Analyze risks for [FeatureName] rollout"`
    - **Input**: `[OUTPUT_MANIFEST].new_tasks` from Step 2
    - **Output**: `5. Trackers/DECISION_LOG.md` (Updated)

## Usage

```bash
/feature "Mobile Dark Mode"
```
