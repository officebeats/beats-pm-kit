# AGENTS.md - Beats PM Kit Codex Adapter

> Thin runtime adapter. Source of truth: `.agent/`.

## Runtime Priority

1. **Antigravity first** - canonical command behavior and orchestration semantics live in `.agent/`.
2. **Codex second** - use native-feeling adapters for the most-used commands: `/boss`, `/create`, `/day`, `/meet`, `/paste`, `/plan`, `/track`, `/transcript`, `/update`, `/vacuum`, `/week`.
3. **Compatibility CLIs next** - Gemini CLI, Claude Code, and KiloCode generate local adapters from `.agent/` without redefining workflow logic.

## Startup

On a new Codex session:

1. If the user provides only the GitHub repo URL, clone/open the repo and run `python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>` from the repo root.
2. Read `SETTINGS.md` and `STATUS.md` first when they are relevant to the task.
3. Treat `.agent/` as the source of truth.
4. When the user invokes `/command`, resolve it through `CODEX_COMMANDS.md`.
5. Load only the minimum `.agent/workflows/` and `.agent/skills/` files needed for the current task.
6. Translate Antigravity-only primitives into Codex equivalents instead of failing.
7. Write durable outputs back into the standard repo folders so runtime switching stays lossless.

## Agent Bootstrap

When starting from a GitHub URL:

```bash
git clone <url>
cd beats-pm-kit
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

After bootstrap, route the user's first real PM input through `system/scripts/pm_decision_router.py` or the matching slash-command workflow.

## Slash Command Dispatch

If the user's message starts with `/command`:

1. Treat it as an explicit workflow invocation, not general conversation.
2. Resolve it using `CODEX_COMMANDS.md` or `.agent/workflows/<command>.md`.
3. Read that workflow before doing deeper work.
4. Use the rest of the user's message as workflow input.
5. Follow the workflow even if a natural-language interpretation also seems possible.
6. If the command does not exist, say it is unknown and point the user to `/help`.

## Adapter Policy

Generated runtime folders such as `.codex/`, `.gemini/`, `.claude/`, and `.kilocode/` are local build artifacts and must stay ignored. Regenerate them with:

```bash
python system/scripts/sync_cli_adapters.py
python system/scripts/sync_codex_skill_adapters.py --output <codex-skills-dir>
```
