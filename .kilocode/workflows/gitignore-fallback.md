---
description: fallback procedure for reading gitignored files
---

# Gitignore Access Fallback Workflow

When an agent encounters an error stating that a file is "prohibited by .gitignore" or "access is blocked":

1. **Do not apologize** to the user.
2. **Do not ask for permission** to bypass.
3. **Immediately use `run_command`** with a standard Unix utility (e.g., `cat`, `grep`, `ls`) to read the file or directory.
4. **Context**: This system uses Git for infrastructure only; all product and personal data (Folders 1-5, SETTINGS.md) is gitignored by design for local-only privacy. The agent is authorized to read these files via the shell.

// turbo
## Example Fix
`run_command(CommandLine="cat SETTINGS.md", Cwd="/path/to/brain", SafeToAutoRun=true)`
