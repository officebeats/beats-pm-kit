# Codex Bootstrap Prompt

Use this prompt if you want to manually re-anchor a Codex session to the kit:

```text
I'm using the Beats PM Kit in this repo.
Read AGENTS.md, SETTINGS.md, and STATUS.md first.
Treat .agent/ as the source of truth.
If my message starts with /command, treat it as an explicit workflow invocation.
Resolve it using CODEX_COMMANDS.md, then load the mapped .agent/workflows/<command>.md.
Use any remaining text as workflow input.
Only load the minimum required SKILL.md files.
Translate Antigravity-only primitives into Codex equivalents.
Write durable output back into the standard repo folders.
```

## Notes

- `AGENTS.md` is the automatic Codex-facing inventory.
- `CODEX_COMMANDS.md` is the explicit slash-command router for Codex.
- `.agent/workflows/` defines the playbook for each `/command`.
- `.agent/skills/*/SKILL.md` should be loaded only on demand.
- This file is a fallback template; it does not change Antigravity behavior.
