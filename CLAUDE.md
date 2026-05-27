# CLAUDE.md - Beats PM Kit Claude Adapter

This file is a thin compatibility entrypoint for Claude Code.

The canonical agent contract, workflows, skills, and rules live in `.agent/`.
Run `python system/scripts/sync_cli_adapters.py` to regenerate local Claude command adapters under `.claude/`.
Generated local adapter directories are intentionally ignored by Git.

If the user provides only the GitHub repo URL, clone/open the repo and run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

Then route the first real PM input through the PM decision router or the matching workflow.
