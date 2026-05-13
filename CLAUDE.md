# CLAUDE.md - Beats PM Kit Claude Adapter

This file is a thin compatibility entrypoint for Claude Code.

The canonical agent contract, workflows, skills, and rules live in `.agent/`.
Run `python system/scripts/sync_cli_adapters.py` to regenerate local Claude command adapters under `.claude/`.
Generated local adapter directories are intentionally ignored by Git.
