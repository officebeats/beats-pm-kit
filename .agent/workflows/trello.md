---
description: Synchronize Beats PM Tracker IDs with a Trello Board, or attach files.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# 🟦 Trello Sync Workflow

This workflow executes the bi-directional Beats PM <-> Trello integration using the built-in python bridge.

## Triggers
The user will run this via `/trello` or mention "sync trello".
They may specify `/trello sync` or `/trello attach <Task_ID> <Path>`.

## Steps

1.  **Check Configuration**:
    - **Action**: Verify `system/config/trello_config.json` exists. If missing, instruct the user to copy `trello_config.template.json` to `.json` and add their API key, token, and map their list IDs.

2.  **Execute the Bridge**:
    - **Action**: Run the python bridge via shell command.
    - **Command**: `python3 system/scripts/trello_bridge.py sync` or `python3 system/scripts/trello_bridge.py attach <TaskID> <File>`
    - **Note**: Ensure `SafeToAutoRun` is set to `true` (see `// turbo` below).

3.  **Read Outcomes**:
    - **Action**: If changes were pulled down, display a summary of tasks that updated based on their Trello state.
    - **Action**: If executing an attach action, confirm the task and target file uploaded properly. 

// turbo
```bash
python3 system/scripts/trello_bridge.py sync
```
