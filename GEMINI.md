# GEMINI.md - Beats Agentic PM Harness Adapter

This file is a thin compatibility entrypoint for Gemini CLI and Antigravity.

The canonical agent contract, workflows, skills, and rules live in `.agent/`.
Load `.agent/rules/GEMINI.md` and `.agent/rules/ACTION_FIRST_OUTPUT.md` first,
then resolve workflows from `.agent/workflows/`.
For file-to-Markdown conversion, load `.agent/skills/markitdown/SKILL.md`.
Generated local adapter directories are intentionally ignored by Git.

If the user provides only the GitHub repo URL, clone/open the repo and run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

Then route the first real PM input through the PM decision router or the matching workflow.
