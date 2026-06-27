---
description: Bootstrap, synchronize, inspect, and attach files for the Beats PM Trello board.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Trello Sync Workflow

This workflow executes the Beats PM <-> Trello integration through `system/scripts/trello_bridge.py`.

## Triggers

Use this workflow when the user runs `/trello`, asks to sync Trello, asks for Trello status, or asks to attach a local artifact to a Trello card.

## Commands

```bash
python3 system/scripts/trello_bridge.py status
python3 system/scripts/trello_bridge.py bootstrap --dry-run
python3 system/scripts/trello_bridge.py bootstrap --apply
python3 system/scripts/trello_bridge.py sync --dry-run
python3 system/scripts/trello_bridge.py sync --apply
python3 system/scripts/trello_bridge.py attach <TASK_OR_CARD_ID> <PATH>
python3 system/scripts/trello_bridge.py install-agent
python3 system/scripts/trello_bridge.py uninstall-agent
```

## Steps

1. **Check configuration**
   - Verify `system/config/trello_config.json` exists and is gitignored.
   - Use `lists` if list IDs need to be refreshed.

2. **Bootstrap before recurring sync**
   - Run `bootstrap --dry-run` first.
   - Review the classification counts and cards marked `needs_review`.
   - Run `bootstrap --apply` only when obvious matches are acceptable.

3. **Recurring sync**
   - Use `sync --dry-run` before a risky run.
   - Use `sync --apply` for normal operation.
   - The bridge mirrors workstreams first. Trello card titles should be plain-English workstream titles of 9 words or fewer, with Task Master IDs and other source IDs kept inside managed card bodies, comments, links, or attachments.
   - The bridge keeps Trello titles clean and writes a Trello-safe working brief into the managed card-description block.
   - The managed brief should include latest outcomes, completed outcomes, open items, recommended next 3 actions, and internal agent refs.
   - Managed checklists should include current open items and the latest completed outcomes/checklist items as checked entries with completion date/source.
   - Never delete completed items from the current managed view merely because they are done; preserve enough completed history for the user to see what changed and when.
   - It preserves human-written Trello notes above the managed block.
   - It posts automated comments only for meaningful changes to open items, urgency, next action, lane/status, or important links.

4. **Outputs**
   - Per-card markdown is stored under `5. Trackers/workstreams/`, `5. Trackers/tasks/`, `5. Trackers/trello/important-links/`, `3. Meetings/notes/`, or `4. People/`.
   - Trello cards keep one latest managed `.md` attachment as an archival snapshot, but daily reading should happen in the card description.
   - Run reports are written under `5. Trackers/trello/sync-runs/`.
   - Conflicts are written under `5. Trackers/trello/conflicts/`.
   - `TASK_MASTER.md` receives a managed Trello hotlist block.

5. **Automation**
   - `install-agent` creates a local macOS LaunchAgent that runs `sync --apply --quiet` every 30 minutes and respects the configured workday window.
   - `uninstall-agent` unloads and removes that LaunchAgent.
   - If the LaunchAgent log shows `Operation not permitted` for the iCloud Drive workspace, grant Full Disk Access to `/bin/zsh` and the Python executable shown in the plist, or move the repo out of iCloud Drive before reloading the agent.

// turbo
```bash
python3 system/scripts/trello_bridge.py status
```
