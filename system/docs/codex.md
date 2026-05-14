# Using Beats PM Kit with Codex

> Codex-first setup and operating guide

---

## Quick Setup

### Step 1: Open the PM brain in Codex

```bash
cd /path/to/your/beats-pm-kit
codex
```

Codex is the optimized default runtime for this kit. Antigravity, Gemini CLI, Claude Code, and KiloCode remain compatibility runtimes that share the same repo state.

### Step 2: Run the Codex setup command

```bash
python system/scripts/beats.py codex-setup
```

This regenerates the runtime adapters, syncs promoted Codex skills into the project and user Codex skill directories, and installs the repo hooks that keep generated adapters synchronized.

For read-only verification:

```bash
python system/scripts/beats.py codex-doctor
python system/scripts/adapter_guard.py --mode check
python system/scripts/context_health.py --check
```

### Step 3: Bootstrap a session

Use this once at the start of a session if Codex needs manual re-anchoring:

```text
I'm using the Beats PM Kit in this repo.
Read AGENTS.md first.
Read SETTINGS.md and STATUS.md when they exist.
Treat .agent/ as the source of truth.
If my message starts with /command, treat it as an explicit workflow invocation.
Resolve it using CODEX_COMMANDS.md, then load the mapped .agent/workflows/<command>.md.
Only load the minimum required SKILL.md files.
Write durable output back into the repo.
```

The reusable copy is [CODEX_PROMPT.md](../../CODEX_PROMPT.md). Slash-command routing is generated in [CODEX_COMMANDS.md](../../CODEX_COMMANDS.md).

---

## Codex-Native Surfaces

- `AGENTS.md`: generated Codex adapter and project inventory.
- `CODEX_COMMANDS.md`: generated slash-command routing table for 40 workflows.
- `.codex/agents/*.toml`: project-scoped custom agents for exploration, writing, verification, docs research, and communication intake review.
- `.codex/skills/`: project-local promoted Beats skill adapters, refreshed by `codex-setup`.
- `system/scripts/feature_inventory.py --json`: authoritative inventory for counts, runtimes, workflows, and promoted Codex commands.

Promoted Codex commands are intentionally high-signal: `/beats-comms`, `/beats-slack`, `/beats-teams`, `/boss`, `/create`, `/day`, `/deck`, `/discover`, `/meet`, `/obsidian`, `/office-cli`, `/paste`, `/plan`, `/prioritize`, `/review`, `/sop`, `/track`, `/transcript`, `/update`, `/vacuum`, `/vibe`, and `/week`.

---

## Codex Cloud and CI

The deterministic Python checks remain the required gate. Codex Action support is optional and manual:

- Prompt files live under `.github/codex/prompts/`.
- The optional workflow uses `workflow_dispatch` only.
- It runs only when `OPENAI_API_KEY` is available as a GitHub secret.
- Keep Codex cloud prompts privacy-safe: no local tracker data, no secrets, no OAuth tokens, no private transcript content.
- Prefer restricted internet access and trusted domains only when configuring Codex cloud environments.

Useful references:

- [AGENTS.md custom instructions](https://developers.openai.com/codex/guides/agents-md)
- [Agent Skills](https://developers.openai.com/codex/skills)
- [Subagents and custom agents](https://developers.openai.com/codex/subagents)
- [Docs MCP](https://developers.openai.com/learn/docs-mcp)
- [Codex cloud](https://developers.openai.com/codex/cloud)
- [Codex GitHub Action](https://developers.openai.com/codex/github-action)

---

## Best Practices

1. Use Codex for repo edits, verification, generated artifacts, and local synthesis.
2. Let `.agent/workflows/*.md` decide the sequence for each playbook.
3. Load `SKILL.md` files only on demand to keep context tight.
4. Use subagents only when the task is explicitly parallel and bounded.
5. Keep all durable output in standard ignored repo folders so compatibility runtimes see the same state.

---

## Useful Local Commands

```bash
python system/scripts/beats.py codex-doctor
python system/scripts/beats.py codex-setup
python system/scripts/beats.py inventory -- --json
python system/scripts/detect_runtime.py --human
python system/scripts/context_health.py --check
python system/scripts/context_health.py --repair
python system/scripts/adapter_guard.py --mode check
python system/scripts/adapter_guard.py --mode fix
python system/scripts/beats.py resolve --args /day
```
