# Agent Memory Integration

The kit's durable memory is the local Markdown repo. External memory systems are retrieval accelerators, not a second source of truth.

## Retrieval Order

1. Canonical repo files and manifests:
   - `5. Trackers/TASK_MASTER.md`
   - `5. Trackers/tasks/`
   - `3. Meetings/chat-transcripts/_manifest.json`
   - `3. Meetings/reports/`
   - `4. People/`
   - `1. Company/`, `2. Products/`, `6. Resources/`, `6. SOPs/`, `7. Partners/`, `8. Clients/`
2. Obsidian direct vault / MCP, read/search/open only, when configured.
3. Agent memory backend, preferably `tenscentdb` / `tencentdb`, when configured.
4. Repo-local `rg` fallback when optional integrations are unavailable.

## TenscentDB / TencentDB Profile

Use a TenscentDB/TencentDB-style backend only as an optional memory retrieval and embedding index.

- Health check: `python3 system/scripts/agent_memory_health.py --pretty`
- CLI gateway: `python3 system/scripts/beats.py agent-memory -- --pretty`
- Provider env: `AGENT_MEMORY_PROVIDER=tenscentdb` or `AGENT_MEMORY_PROVIDER=tencentdb`
- Endpoint env: `AGENT_MEMORY_URL` or `TENCENTDB_URL`
- Secret env: `AGENT_MEMORY_API_KEY` or `TENCENTDB_API_KEY`
- Namespace env: `AGENT_MEMORY_NAMESPACE` or `TENCENTDB_NAMESPACE`

## Allowed Operations

- Check configuration health.
- Retrieve semantically relevant memory snippets.
- Return source pointers back to canonical repo files.
- Use memory hits to choose which repo files to read next.

## Disallowed Operations

- Do not write, overwrite, delete, or mutate external memory without an explicit workflow that says so.
- Do not treat external memory as fresher than repo files or source manifests.
- Do not store secrets, raw transcripts, private chats, emails, or unmanaged attachments in external memory.
- Do not create tasks, decisions, or status changes from external memory alone; route through the selected kit workflow.

## Runtime Contract

- Antigravity, Codex, Gemini CLI, Claude Code, and KiloCode should all follow this same retrieval order.
- If the memory backend is missing, expired, blocked, or unconfigured, record the gap and continue with Obsidian or repo-local search.
- Any synthesis that used external memory must cite the local repo artifact that confirms the memory, or explicitly label the memory hit as unverified.
