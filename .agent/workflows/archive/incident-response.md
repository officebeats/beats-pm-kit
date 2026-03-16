---
description: Incident Post-Mortem. Chains Timeline Gathering -> Root Cause Analysis -> Remediation Tasks.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Incident Response Workflow (`/incident`)

This workflow brings order to chaos after a Sev-1 or Sev-2 incident.

## Steps

1.  **Gather Timeline & Artifacts**
    - **Agent**: `bug-chaser`
    - **Command**: `/bug "Compile a timeline for Incident [IncidentID] using recent logs and transcripts."`
    - **Output**: `5. Trackers/bugs/incidents/[Date]_[ID]_Timeline.md`

2.  **Root Cause Analysis (5 Whys)**
    - **Agent**: `decision-maker`
    - **Command**: `/decide "Perform a 5-Whys Root Cause Analysis on [IncidentID]."`
    - **Input**: `[OUTPUT_MANIFEST]` from Step 1
    - **Output**: `5. Trackers/bugs/incidents/[Date]_[ID]_RCA.md`

3.  **Assign Remediation Tasks**
    - **Agent**: `task-manager`
    - **Command**: `/task "Create P0 tickets for the 'Preventative Actions' identified in the RCA."`
    - **Input**: `[OUTPUT_MANIFEST].action_items` from Step 2
    - **Output**: `5. Trackers/TASK_MASTER.md` (Updated)

## Usage

```bash
/incident "INC-1234 Data Outage"
```
