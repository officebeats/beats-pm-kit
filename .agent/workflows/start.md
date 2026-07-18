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
4. Named read-only source windows for Outlook, Teams, and Slack.
5. Whether Granola and Quill evidence will come from local access, exports, or pasted transcripts.

Write profile answers to `SETTINGS.md` and local stakeholder/task files only. Keep all profile output in ignored workspace paths.

These five evidence sources are the default daily triangulation loop. Optional board tools are enabled later through `/pack` and never replace Markdown task notes.

---

## Step 4: Obsidian Suggestion

Run `python3 system/scripts/obsidian_bridge.py guide --json`, then tell the user Obsidian is optional and show the exact returned paths:

- `kit_folder` is the folder to choose in Obsidian's **Open folder as vault** picker.
- `task_folder` contains the local task system.
- `task_folder` is the canonical `5. Trackers/tasks/` note folder; `task_master` is its generated navigation view.
- `guide` is the setup and usage guide.

Offer `/obsidian setup` to configure the existing kit folder directly as the vault. Do not create a mirrored copy unless the user explicitly asks for external-vault sync. Use `/obsidian tasks` to open the task ledger after setup.

Use `python3 system/scripts/obsidian_mcp_health.py --pretty` only for optional read/search/open MCP. If MCP is unavailable, agents fall back to `rg` over the repo.

Obsidian MCP is read/search/open only in v1. Do not use write, delete, patch, or arbitrary command tools.

---

## Step 5: First Useful Commands

Show:

```text
Start here:

  /paste       Process messy PM input into routed tasks, questions, or docs
  /day         See current priorities and triage questions
  /track       Manage local task state
  /obsidian    Set up or open the optional visual task workspace
  /transcript  Prepare and validate meeting transcripts
  /create      Draft PRDs, specs, and one-pagers
  /plan        Build roadmaps, OKRs, and strategic plans
  /help        Full command reference
```

Route any remaining user input through `system/scripts/pm_decision_router.py` before creating active tasks.
