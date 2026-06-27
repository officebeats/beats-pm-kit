# Agent Memory Retrieval

Beats PM Kit can use an optional agent-memory backend for semantic retrieval, but the local Markdown repo remains the source of truth.

## Source Of Truth

Use this order in Codex, Antigravity, Gemini CLI, Claude Code, and KiloCode:

1. Read canonical repo files and manifests.
2. Use Obsidian MCP as an optional direct-vault read/search/open layer.
3. Use TenscentDB/TencentDB-style agent memory as an optional semantic retrieval layer.
4. Fall back to repo-local `rg` when optional integrations are unavailable.

Agent memory should help decide which local files to inspect. It must not create tasks, update status, or write decisions without confirming against the repo.

## Configure

```bash
export AGENT_MEMORY_PROVIDER=tenscentdb
export AGENT_MEMORY_URL=<memory-endpoint>
export AGENT_MEMORY_API_KEY=<local-secret>
export AGENT_MEMORY_NAMESPACE=beats-pm-kit
```

The health check also accepts TencentDB-style aliases:

```bash
export AGENT_MEMORY_PROVIDER=tencentdb
export TENCENTDB_URL=<memory-endpoint>
export TENCENTDB_API_KEY=<local-secret>
export TENCENTDB_NAMESPACE=beats-pm-kit
```

Do not commit API keys, endpoint secrets, local MCP config, or generated memory cache files.

## Health Check

```bash
python3 system/scripts/agent_memory_health.py --pretty
python3 system/scripts/beats.py agent-memory -- --pretty
```

If the health check is unavailable or unconfigured, continue with Obsidian MCP or repo-local `rg`.

## Policy

Allowed:

- configuration health checks
- semantic retrieval
- source pointer lookup
- read-only retrieval cache use

Disallowed:

- external memory writes unless a workflow explicitly allows them
- raw transcript or private chat storage in external memory
- secret storage
- treating memory as a task ledger
- treating memory hits as confirmed-current without local evidence
