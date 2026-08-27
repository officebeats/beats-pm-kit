# CLAUDE.md - Beats Agentic PM Harness Claude Adapter

The canonical agent contract, workflows, skills, and rules live in `.agent/`.
Load `.agent/rules/TOKEN_EFFICIENCY.md` and `.agent/rules/ACTION_FIRST_OUTPUT.md` for every user-facing response.
For file-to-Markdown conversion, load `.agent/skills/markitdown/SKILL.md`.
Run `python system/scripts/sync_cli_adapters.py` to regenerate local Claude command adapters under `.claude/`.
Generated local adapter directories are intentionally ignored by Git.

If the user provides only the GitHub repo URL, clone/open the repo and run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

Then resolve the first real PM input with `system/scripts/harness_registry.py` and load only the selected bounded workflow context.
