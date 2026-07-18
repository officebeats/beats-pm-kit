---
description: Detect, configure, open, sync, and optionally expose the Beats PM Kit through Obsidian.
---

# Obsidian Workflow

Use this workflow when the user runs `/obsidian`, wants a visual task view, asks whether Obsidian is installed, wants the kit opened in Obsidian, explicitly wants external-vault sync, or asks for Obsidian MCP setup.

The existing Beats PM Kit folder is the default vault. Individual notes under `5. Trackers/tasks/` remain the task source of truth; `TASK_MASTER.md` is generated navigation.

## Commands

```bash
python3 system/scripts/obsidian_bridge.py guide
python3 system/scripts/obsidian_bridge.py guide --json
python3 system/scripts/obsidian_bridge.py status
python3 system/scripts/obsidian_bridge.py configure --mode kit-vault
python3 system/scripts/obsidian_bridge.py open dashboard
python3 system/scripts/obsidian_bridge.py open tracker
python3 system/scripts/obsidian_bridge.py open daily
python3 system/scripts/obsidian_bridge.py open search --query "owner:me"
python3 system/scripts/obsidian_bridge.py sync --dry-run
python3 system/scripts/obsidian_bridge.py sync --apply
python3 system/scripts/obsidian_bridge.py sync --apply --clean
python3 system/scripts/obsidian_bridge.py mcp-template
```

## Steps

1. **Guide first**
   - With no extra user input, run `guide` so the response includes the exact kit folder, canonical task-note folder, generated Task Master, and guide paths.
   - Run `status` before configuring or syncing.
   - Treat stale saved vault paths as stale; do not trust Obsidian global metadata unless the vault path still exists.

2. **Configure**
   - `/obsidian setup` means `configure --mode kit-vault`; it configures the existing kit folder and its local graph settings in one path.
   - Prefer `kit-vault` mode even when other saved vaults exist.
   - Use `sync` mode only when the user explicitly asks for a copy inside an existing external vault.
   - Store local machine paths only in `system/config/obsidian.local.json`, which must remain gitignored.

3. **Open**
   - `/obsidian tasks` means `open tracker`: direct mode opens the generated `5. Trackers/TASK_MASTER.md` navigation view; external sync mode opens its synced `Trackers/TASK_MASTER.md` view.
   - Use Obsidian URI/CLI behavior for vault, dashboard, daily note, tracker, search, and file opening.
   - If a folder has never been opened as an Obsidian vault, tell the user to open the folder once through Obsidian's vault picker if the URI cannot resolve it.

4. **Sync**
   - Run `sync --dry-run` before risky changes.
   - Use `sync --apply` for normal operation.
   - `--clean` removes only managed files with Beats PM Kit frontmatter; it must not delete human-created Obsidian notes.

5. **MCP**
   - MCP is optional and should use the Obsidian Local REST API plugin.
   - Generate only placeholder config with `mcp-template`.
   - Never place `OBSIDIAN_API_KEY` or private vault paths in tracked files.

## Task Manager Handoff

`/track` may call `guide --json` after local task work completes. If `should_prompt` is true, show the exact returned paths and offer `/obsidian setup`. The prompt is optional and must never block Markdown task management.
