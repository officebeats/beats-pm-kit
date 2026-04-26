---
name: teams
description: Capture Teams chat context and update the Task Master.
agent: staff-pm
skills: ["inbox-processor", "task-manager"]
---

# /teams — Teams Context Sync

Use this workflow to ingest the latest discussion context from Microsoft Teams.

## 1. Context Capture (Admin or Manual)
- **Automatic**: If you have Accessibility permissions, it scrapes the active window.
- **Manual (Non-Admin)**: Since you don't have admin access, simply **CMD+A, CMD+C** in Teams to copy the chat, and the bridge will read it from your clipboard using `pbpaste`.
- // turbo
- `python3 system/scripts/beats.py teams --args "--json"`

## 2. Intelligence Synthesis (Staff PM)
- Analyze the captured chat fragments.
- Filter for:
    - Decisions made.
    - New dates or deadlines discussed.
    - Action items assigned to the user.
    - Status updates relevant to existing tasks (e.g., **BOSS-001**).

## 3. Atomic Updates
- **Update Boss Tracker**: If the chat is with your manager or leadership, append a "Teams Sync" entry to the relevant `Progress Log` in `5. Trackers/tasks/`.
- **Stakeholder Stream**: Update the corresponding profile in `4. People/` with a summary of the interaction.
- **New Signal**: If new tasks are identified, route to `inbox-processor` for creation.

## 4. Confirmation
- Display a summary of what was synced (e.g., "Updated BOSS-001: Discussion on Q3 roadmap dates").
