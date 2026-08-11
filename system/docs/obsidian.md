# Using Beats PM Kit With Obsidian

Obsidian is an optional visual layer over the same local Markdown files used by Antigravity, Codex, Claude Code, Gemini CLI, and KiloCode. It is not a second task database.

## Start With `/obsidian`

Run this in a supported agent:

```text
/obsidian
```

The workflow runs the local guide and reports exact machine-specific paths:

- `kit_folder` - choose this in Obsidian's **Open folder as vault** picker.
- `task_folder` - the canonical `5. Trackers/` task workspace.
- `task_folder` - the canonical `5. Trackers/tasks/` note folder.
- `task_master` - the generated `5. Trackers/TASK_MASTER.md` navigation view.
- `obsidian_task_folder` - the task folder displayed by the active Obsidian mode.
- `obsidian_task_master` - the Task Master path opened by `/obsidian tasks`.
- `guide` - this file.

Useful actions:

```text
/obsidian setup
/obsidian tasks
/obsidian status
```

## Direct Vault Setup

1. Run `/obsidian setup`. This configures the existing repo as a direct vault and creates local graph settings.
2. Open Obsidian.
3. Choose **Open folder as vault** and select the exact `kit_folder` reported by `/obsidian`:

```text
<path-to-your-beats-pm-kit-folder>
```

4. Run `/obsidian tasks` to open the generated Task Master and follow links into canonical task notes.

Terminal equivalent:

```bash
python3 system/scripts/obsidian_bridge.py configure --mode kit-vault
python3 system/scripts/obsidian_bridge.py open tracker
```

The bridge uses the existing `obsidian_vault_setup.py` implementation to create local `.obsidian/` settings and `6. Resources/obsidian/Obsidian Graph Index.md`.

## How Tasks Work

- `5. Trackers/WORKSTREAMS.md` is the human-facing workstream rollup.
- `5. Trackers/tasks/` contains the canonical individual task notes.
- `5. Trackers/TASK_MASTER.md` is generated linked navigation over those notes.
- `5. Trackers/tasks/` contains task detail, evidence, subtasks, and progress.
- `/track` updates the Markdown source of truth.
- `/obsidian tasks` opens that same Task Master in Obsidian.

After a full `/track` run, the agent may offer this Obsidian view when it is not configured. The prompt is optional and never blocks task capture or triage.

## What This Does

- Enables Obsidian core plugins for graph view, backlinks, outgoing links, tags, canvas, properties, bases, templates, and daily notes.
- Adds graph color groups for Trackers, Meetings, People, Products, Partners, Clients, SOPs, and Resources.
- Excludes noisy implementation/runtime folders and the generated `MARKDOWN_LABELS.md` reference catalog from Obsidian search and graph.
- Creates a graph index note that links to generated human-readable workstream, task, meeting, and operating-area hubs.

## What This Does Not Do

- It does not duplicate files into a separate mirror vault.
- It does not mutate Slack, Teams, Outlook, Jira, Confluence, Trello, or any external source system.
- It does not commit local Obsidian workspace state or plugin state.
- It does not make Obsidian a writable task ledger for agents; the kit files remain canonical.

## Optional MCP Read/Search

For Codex, Antigravity, or other MCP-capable runtimes, Obsidian can expose the direct vault as a read/search/open-file context surface. Follow [Obsidian MCP Profile For Beats PM Kit](obsidian-mcp.md).

Health check:

```bash
python3 system/scripts/obsidian_mcp_health.py --pretty
```

If the MCP endpoint or API key is unavailable, agents must fall back to repo-local `rg` searches.

## Terminal Commands

Show exact task and setup paths without writing:

```bash
python3 system/scripts/obsidian_bridge.py guide
python3 system/scripts/obsidian_bridge.py guide --json
```

Preview changes:

```bash
python3 system/scripts/obsidian_vault_setup.py --dry-run
```

Apply local vault settings:

```bash
python3 system/scripts/obsidian_bridge.py configure --mode kit-vault
```

Apply settings and open the graph index in Obsidian:

```bash
python3 system/scripts/obsidian_bridge.py open tracker
```

## Graph Tips

- Start at `5. Trackers/graph-hubs/Human-readable Hubs.md` or `6. Resources/obsidian/Obsidian Graph Index.md`.
- `5. Trackers/MARKDOWN_LABELS.md` remains a complete reference catalog, but is intentionally not the graph center.
- Use graph search `path:"5. Trackers"` for active task state.
- Use graph search `path:"4. People"` for stakeholder context.
- Use graph search `path:"3. Meetings"` for meeting notes, transcripts, and evidence.
- Use graph search `path:"7. Partners" OR path:"8. Clients"` for external relationship context.

## External-Vault Sync

Direct-vault mode is the default even when Obsidian already knows about other vaults. Use `sync` mode only when you explicitly want a managed copy inside an existing external vault. Preview with `obsidian_bridge.py sync --dry-run` before applying. Managed cleanup never removes human-created notes.

In external sync mode, `guide --json` keeps prompting until the synced Task Master exists. `/obsidian tasks` opens the synced `Trackers/TASK_MASTER.md`; the local notes under `5. Trackers/tasks/` remain canonical.
