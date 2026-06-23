---
description: Detect, configure, open, sync, and optionally expose the Beats PM Kit through Obsidian.
---

# Obsidian Workflow

Use this workflow when the user runs `/obsidian`, asks whether Obsidian is installed, wants the kit opened in Obsidian, wants Kit-to-vault sync, or asks for Obsidian MCP setup.

## Commands

```bash
python3 system/scripts/obsidian_bridge.py status
python3 system/scripts/obsidian_bridge.py configure
python3 system/scripts/obsidian_bridge.py open dashboard
python3 system/scripts/obsidian_bridge.py open daily
python3 system/scripts/obsidian_bridge.py open tracker
python3 system/scripts/obsidian_bridge.py open search --query "owner:me"
python3 system/scripts/obsidian_bridge.py sync --dry-run
python3 system/scripts/obsidian_bridge.py sync --apply
python3 system/scripts/obsidian_bridge.py sync --apply --clean
python3 system/scripts/obsidian_bridge.py mcp-template
```

## Steps

1. **Inspect first**
   - Run `status` before configuring or syncing.
   - Treat stale saved vault paths as stale; do not trust Obsidian global metadata unless the vault path still exists.

2. **Configure**
   - Prefer `kit-vault` mode when the kit root is the valid vault or no valid external vault is available.
   - Use `sync` mode when the user has a valid existing Obsidian vault and wants a copy under a target folder.
   - Store local machine paths only in `system/config/obsidian.local.json`, which must remain gitignored.

3. **Open**
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
