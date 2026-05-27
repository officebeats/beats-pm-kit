# GEMINI.md - Beats PM Kit Runtime Adapter

This file is a thin compatibility entrypoint for Gemini CLI and Antigravity.

The canonical agent contract, workflows, skills, and rules live in `.agent/`.
Load `.agent/rules/GEMINI.md` first, then resolve workflows from `.agent/workflows/`.
Generated local adapter directories are intentionally ignored by Git.

If the user provides only the GitHub repo URL, clone/open the repo and run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

Then route the first real PM input through the PM decision router or the matching workflow.
