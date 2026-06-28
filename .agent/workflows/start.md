---
description: First-time guided setup and agent-native bootstrap. Run on first session or manually with /start.
---

> **Compatibility Directive**: Works across Antigravity, Codex, Gemini CLI, Claude Code, and KiloCode.

# /start — Bootstrap And Welcome

**Trigger**: `/start`, first session setup, or a user providing only the Beats PM Kit GitHub URL.

---

## Step 0: Agent-Native Bootstrap

If the user provides only the GitHub repo URL, clone/open the repo first, then run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

If the repo is already open, run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive
```

Bootstrap verifies the repo, creates ignored local workspace folders, writes `.beats/initialized`, seeds local templates, syncs runtime adapters, installs git hooks when possible, runs privacy/adapter health checks, previews root cleanup, and suggests direct-vault Obsidian setup.

Do not write to Slack, Teams, Outlook, Jira, Confluence, Trello, or Obsidian during bootstrap.

---

## Step 1: Runtime Check

Run:

```bash
python3 system/scripts/detect_runtime.py --human
```

Display the detected runtime and any missing optional capabilities.

---

## Step 2: Welcome

Display:

```text
Welcome to Beats PM Kit.

The kit is ready to process PM work from local Markdown, transcripts, screenshots, task ledgers, and named read-only communication source windows.
```

---

## Step 3: Optional Profile Setup

Ask for only the profile fields needed for useful local artifacts:

1. Name for local task ownership.
2. Direct manager for boss-request routing.
3. Product or initiative focus.
4. Whether Trello should remain disabled, connect to an existing board, or provision a new board.

Write profile answers to `SETTINGS.md` and local stakeholder/task files only. Keep all profile output in ignored workspace paths.

If Trello is enabled, use `system/scripts/trello_bridge.py` and keep Trello downstream from accepted local task state.

---

## Step 4: Obsidian Suggestion

Tell the user Obsidian is optional:

- Open the existing kit folder directly as the vault.
- Do not create a mirrored copy.
- Use `python3 system/scripts/obsidian_vault_setup.py --apply` for local graph settings.
- Use `python3 system/scripts/obsidian_mcp_health.py --pretty` to check optional read/search/open MCP.
- If MCP is unavailable, agents fall back to `rg` over the repo.

Obsidian MCP is read/search/open only in v1. Do not use write, delete, patch, or arbitrary command tools.

---

## Step 5: First Useful Commands

Show:

```text
Start here:

  /paste       Process messy PM input into routed tasks, questions, or docs
  /day         See current priorities and triage questions
  /track       Manage local task state
  /transcript  Prepare and validate meeting transcripts
  /create      Draft PRDs, specs, and one-pagers
  /plan        Build roadmaps, OKRs, and strategic plans
  /help        Full command reference
```

Route any remaining user input through `system/scripts/pm_decision_router.py` before creating active tasks.
