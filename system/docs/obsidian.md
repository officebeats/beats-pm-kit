# Using Beats PM Kit Directly With Obsidian

This setup uses the existing `beats-pm-kit` folder as the Obsidian vault. It does not copy or mirror working files into a separate vault.

## Direct Vault Setup

1. Open Obsidian.
2. Choose **Open folder as vault**.
3. Select:

```text
<path-to-your-beats-pm-kit-folder>
```

4. Run the local setup helper from the kit root:

```bash
python3 system/scripts/obsidian_vault_setup.py --apply
```

The helper creates local `.obsidian/` settings and `6. Resources/obsidian/Obsidian Graph Index.md`. These files are for local navigation and graphing over the raw kit files.

## What This Does

- Enables Obsidian core plugins for graph view, backlinks, outgoing links, tags, canvas, properties, bases, templates, and daily notes.
- Adds graph color groups for Trackers, Meetings, People, Products, Partners, Clients, SOPs, and Resources.
- Excludes noisy implementation/runtime folders from Obsidian search and graph, including `.git`, generated runtime adapters, caches, tests, scratch files, and outputs.
- Creates a graph index note that links to Task Master, weekly planning, decision logs, people, meetings, clients, partners, SOPs, and evidence lanes.

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

## Useful Commands

Preview changes:

```bash
python3 system/scripts/obsidian_vault_setup.py --dry-run
```

Apply local vault settings:

```bash
python3 system/scripts/obsidian_vault_setup.py --apply
```

Apply settings and open the graph index in Obsidian:

```bash
python3 system/scripts/obsidian_vault_setup.py --apply --open
```

## Graph Tips

- Start at `6. Resources/obsidian/Obsidian Graph Index.md`.
- Use graph search `path:"5. Trackers"` for active task state.
- Use graph search `path:"4. People"` for stakeholder context.
- Use graph search `path:"3. Meetings"` for meeting notes, transcripts, and evidence.
- Use graph search `path:"7. Partners" OR path:"8. Clients"` for external relationship context.

## Mirror Mode

`system/scripts/obsidian_sync.py` still exists for a separate mirrored-vault workflow. Do not use it when the goal is to graph the raw kit folder in place.
