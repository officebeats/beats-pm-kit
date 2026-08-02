# Beats Agentic PM Harness — Antigravity Adapter

`.agent/` is canonical. Antigravity, Codex, and Claude are equal primary runtimes; inherit the active runtime's model and use only positively detected capabilities.

## Startup and routing

- For a repo URL only, clone/open it and run `python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>`.
- Run health/setup only when initialization is missing or the selected workflow needs it.
- Resolve a command or skill with `python3 system/scripts/harness_registry.py resolve <target>`.
- Read the selected workflow or skill directly. Load no more than five relevant sources and follow at most one raw-evidence hop; never invoke another routing hierarchy.
- Use `compact_operator` narration while acting, then the resolved `artifact` or `verbatim` final profile.

## Non-negotiable boundaries

- Keep private evidence and runtime state local. Do not expose PII, credentials, tokens, tenant IDs, transcripts, or private paths in tracked/system artifacts.
- Never send, forward, or reply to email unless the user explicitly asks for that specific message in the current turn.
- External mutation and destructive actions require the selected workflow's approval gate and explicit current-turn authority.
- `/beats-comms` uses named, read-only Slack, Teams, Outlook, and Calendar windows under `MCP_COMMUNICATION_INTAKE.md`.
- Screenshots and transcripts default to task/workstream evidence unless the user states another intent. Route ambiguous durable work through `pm-decision-router`.
- Obsidian and TWG are optional read-only accelerators. Exact sources and accepted local state remain authoritative.

## Execution

`route → bounded context → tools → checkpoint → verify → persist artifact and trace → hand off`

Archive oversized payloads with `context_store.py`. Compact only at completed discovery, planning, creation, or verification boundaries when context is at least 65% or the next phase will not fit. Retrieve raw evidence before quotations, customer commitments, legal language, security findings, or final citations.
