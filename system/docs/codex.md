# Using Beats PM Kit with Codex

> Step-by-step guide for Codex users

---

## Quick Setup

### Step 1: Open the PM Brain in Codex

```bash
cd /path/to/your/beats-pm-kit
codex
```

### Step 2: Bootstrap Codex with the Repo Context

Use this once at the start of a session:

```text
I'm using the Beats PM Kit in this repo.
Read AGENTS.md, SETTINGS.md, and STATUS.md first.
Treat .agent/ as the source of truth.
If my message starts with /command, treat it as an explicit workflow invocation.
Resolve it using CODEX_COMMANDS.md, then load the mapped .agent/workflows/<command>.md.
Use any remaining text as workflow input.
Only load the minimum required SKILL.md files.
Write durable output back into the repo.
```

If you want a reusable copy-paste version in the repo root, use [CODEX_PROMPT.md](../../CODEX_PROMPT.md).

Codex slash-command routing is documented explicitly in [CODEX_COMMANDS.md](../../CODEX_COMMANDS.md).

### Step 3: Work in Repo-Native Mode

Codex works best when you are explicit about the playbook:

```text
Run `/day` by reading `.agent/workflows/day.md`.
```

```text
Run `/meet` on `3. Meetings/transcripts/<file>.md` and route action items into the trackers.
```

```text
Run `/create` for a PRD on <topic>. Mine `1. Company/` and relevant `2. Products/` docs first.
```

---

## Best Practices for Codex

1. Use `AGENTS.md` as the inventory, not as the full instructions.
2. Let `.agent/workflows/*.md` decide the sequence for each playbook.
3. Load `SKILL.md` files only on demand to keep context tight.
4. Keep all outputs in the standard repo folders so Antigravity sees the same state later.
5. Use Codex for deterministic editing, tracker maintenance, PRDs, and local synthesis.

---

## Best Split Between Antigravity and Codex

| Runtime | Best At |
| :--- | :--- |
| **Antigravity** | Parallel fan-out, browser/MCP-heavy work, rapid intake, multimodal exploration |
| **Codex** | Precise file edits, workflow execution over local markdown, repo refactors, reliable artifact generation |

### Recommended Rhythm

1. Use **Antigravity** for broad exploration, research, and high-parallel intake.
2. Use **Codex** for turning that context into durable repo updates.
3. Keep trackers, summaries, specs, and strategy docs in the repo so switching runtimes is lossless.

---

## Useful Local Commands

```bash
python3 system/scripts/detect_runtime.py --human
python3 system/scripts/sync_cli_adapters.py
python3 system/scripts/beats.py help
python3 system/scripts/beats.py day
python3 system/scripts/beats.py resolve --args /day
```

`beats.py` runs script-backed utilities directly and gives workflow hints for model-driven commands such as `day`, `track`, `meet`, `create`, and `plan`.
