# Using Beats PM Kit with Obsidian

Obsidian works well with this kit because the kit is already a local Markdown system. The integration is intentionally local-first: filesystem sync and Obsidian URI/CLI support are the default path, while MCP is an optional advanced layer.

## Quick Start

Run:

```bash
python3 system/scripts/obsidian_bridge.py status
python3 system/scripts/obsidian_bridge.py configure
python3 system/scripts/obsidian_bridge.py open dashboard
```

The bridge detects Obsidian, validates saved vault paths, writes local machine configuration to `system/config/obsidian.local.json`, and creates or updates the safe dashboard note `OBSIDIAN.md`.

## Modes

| Mode | Use When | Behavior |
| --- | --- | --- |
| `kit-vault` | You want this repo opened directly in Obsidian | Obsidian reads the kit folders in place. No duplicate copy is needed. |
| `sync` | You already have a separate Obsidian vault | The bridge copies managed kit content into a target folder inside that vault. |

If no valid saved vault exists, the bridge defaults to `kit-vault` mode and treats the kit root as the vault.

## Commands

```bash
python3 system/scripts/obsidian_bridge.py status
python3 system/scripts/obsidian_bridge.py configure --vault "/path/to/vault"
python3 system/scripts/obsidian_bridge.py open dashboard
python3 system/scripts/obsidian_bridge.py open daily
python3 system/scripts/obsidian_bridge.py open tracker
python3 system/scripts/obsidian_bridge.py open search --query "priority: now"
python3 system/scripts/obsidian_bridge.py sync --dry-run
python3 system/scripts/obsidian_bridge.py sync --apply
python3 system/scripts/obsidian_bridge.py sync --apply --clean
python3 system/scripts/obsidian_bridge.py mcp-template
```

The older command still works:

```bash
python3 system/scripts/obsidian_sync.py --dry-run
```

## Sync Safety

The sync path adds Beats-managed frontmatter only to Markdown files without user-authored frontmatter. Files with non-kit frontmatter are preserved. Re-running sync is idempotent: unchanged files are skipped instead of being rewritten with a new timestamp.

`--clean` only removes stale files that contain Beats PM Kit managed frontmatter. Human-created Obsidian notes are left alone.

## Optional MCP

MCP is optional. Use it only if you have Obsidian running with the Local REST API community plugin enabled.

1. In Obsidian, install and enable the Local REST API plugin.
2. Run:

   ```bash
   python3 system/scripts/obsidian_bridge.py mcp-template
   ```

3. Put the local REST API key into the ignored `system/config/mcp.obsidian.local.json` file or an environment variable.

Never commit `OBSIDIAN_API_KEY`, private vault paths, plugin tokens, or local MCP runtime state.

## Recommended Plugins

These are optional, not required:

| Plugin | Why |
| --- | --- |
| Dataview | Query notes and trackers across the vault |
| Tasks | Better task rollups from Markdown checkboxes |
| Calendar | Daily and weekly note navigation |
| Templater | Reusable capture and meeting templates |

## Troubleshooting

- If `status` shows stale vaults, Obsidian's global metadata points at folders that no longer exist. Run `configure` to choose the best current mode.
- If `open dashboard` does not open the kit as a vault, open the kit folder once through Obsidian's vault picker, then rerun the command.
- If REST API health is `not reachable`, Obsidian is either closed or the Local REST API plugin is not enabled.
