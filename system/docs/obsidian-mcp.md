# Obsidian MCP Profile For Beats PM Kit

Obsidian is an optional read/search layer for the existing direct-vault setup. The kit folder remains the source of truth, and all durable task, discovery, decision, and transcript writes still go through repo workflows.

## Supported Profile

Use the Obsidian **Local REST API & MCP Server** community plugin with the existing kit folder opened directly as the vault.

- MCP endpoint: `https://127.0.0.1:27124/mcp/`
- Optional HTTP endpoint: `http://127.0.0.1:27123/mcp/`
- Required local secret: `OBSIDIAN_API_KEY`
- Optional override: `OBSIDIAN_MCP_URL`

Do not commit `.mcp.json`, API keys, local plugin settings, or generated Obsidian workspace state.

## Health Check

```bash
python3 system/scripts/obsidian_mcp_health.py --pretty
```

If the health check is unavailable, workflows must fall back to `rg` over the repo:

```bash
rg -n "<query>" "1. Company" "2. Products" "3. Meetings" "4. People" "5. Trackers"
```

## V1 Tool Policy

Allowed:

- list vault files
- read files
- get document maps/headings
- search vault content or metadata
- list tags
- get active file path
- open a file in Obsidian for human review

Disallowed:

- write, append, patch, delete, or move vault files
- execute arbitrary Obsidian commands
- treat Obsidian as a second task ledger

## Workflow Contract

The `pm-decision-router` may use Obsidian MCP to retrieve relevant notes when available. If unavailable, it must use repo-local search and continue. Optional TenscentDB/TencentDB agent memory may sit behind the same retrieval step, but memory hits must point back to local repo artifacts before driving task, decision, or status updates. Either way, durable updates are written only through the selected kit workflow.
