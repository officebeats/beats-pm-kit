---
description: First-time guided setup and agent-native bootstrap. Run on first session or manually with /start.
---

> **Compatibility Directive**: Works across Antigravity, Codex, Gemini CLI, Claude Code, and KiloCode.

# /start — Bootstrap And Welcome

**Trigger**: `/start`, first session setup, or a user providing only the Beats PM Kit GitHub URL.

---

## Step 0: Agent-Native Bootstrap (Super-Fast)

If the user provides only the GitHub repo URL, clone/open the repo first, then run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --fast --repo-url <url>
```

If the repo is already open, run:

```bash
python3 system/scripts/bootstrap.py --agent --non-interactive --fast
```

Bootstrap verifies the repo, runs upgrade-compatibility, creates ignored local workspace folders, writes `.beats/initialized`, seeds local templates, syncs runtime adapters, installs git hooks when possible, and suggests direct-vault Obsidian setup.

Do not write to Slack, Teams, Outlook, Jira, Confluence, Trello, or Obsidian during bootstrap.

---

## Step 1: Runtime & Profile Check

Run:

```bash
python3 system/scripts/detect_runtime.py --human
python3 system/scripts/ftue.py status --json
```

---

## Step 2: Terminal Matrix Banner & Welcome

Display the glyph matrix terminal banner:

```text
 ▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
▌   ██████╗ ███████╗ █████╗ ████████╗███████╗   ██████╗ ███╗   ███╗  ▐
▌   ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝   ██╔══██╗████╗ ████║  ▐
▌   ██████╔╝█████╗  ███████║   ██║   ███████╗   ██████╔╝██╔████╔██║  ▐
▌   ██╔══██╗██╔══╝  ██╔══██║   ██║   ╚════██║   ██╔═══╝ ██║╚██╔╝██║  ▐
▌   ██████╔╝███████╗██║  ██║   ██║   ███████║██╗██║     ██║ ╚═╝ ██║  ▐
▌   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝╚═╝     ╚═╝     ╚═╝  ▐
▌       [ ◈ B E A T S   P M   K I T  ::  F T U E   O N L I N E ◈ ]   ▐
 ▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞
```

Display the welcome message:

```text
Welcome to Beats PM Kit — the agentic, local-first PM operating system.
Environment verified. Runtime active.
```

---

## Step 3: Adaptive Conversational FTUE Setup (One Question at a Time)

If the profile is already configured (`is_configured: true`), show the current settings and ask if the user would like to update anything or jump straight into `/paste` or `/day`.

If the profile is pending setup (`is_configured: false`), conduct a streamlined, conversational FTUE asking **exactly one question at a time**, adapting each follow-up question based on the user's prior response.

---

### Question 1: Operational Model (The Fork)

Present the initial glyph card and ask:

```text
┌──[ INITIAL SETUP :: OPERATIONAL MODEL ]───────────────────────────┐
│ 1. In-House PM : Working at a single organization managing one or │
│                  multiple products / feature areas.               │
│ 2. Consulting  : Working for a consulting firm / agency assisting │
│                  multiple client companies on product projects.   │
└───────────────────────────────────────────────────────────────────┘
```

> "Do you work in-house at a **single organization** (managing one or more products), or at a **consulting firm** (defining and managing product projects across various client companies)?"

---

### Adaptive Follow-Up Sequence

#### Branch A: In-House Setup
1. **Turn 2 (Identity & Team)**: Ask for the user's **Name & PM Role** (and company/team name).
2. **Turn 3 (Product Scope)**: Ask whether they manage a **single primary product** or a **portfolio of products**, and what those product names/keywords are.
3. **Turn 4 (Leadership)**: Ask for their **Direct Manager's name** (for automatic `#boss` priority routing).
4. **Turn 5 (Telemetry, Optional)**: Ask if daily evidence will come from specific Slack/Teams/Outlook windows or pasted notes.

Apply responses:
```bash
python3 system/scripts/ftue.py configure \
  --owner "<name>" \
  --role "<role>" \
  --org-type in-house \
  --manager "<manager>" \
  --products "<products>"
```

#### Branch B: Consulting Setup (Multi-Client & Multi-Project)
1. **Turn 2 (Identity & Firm)**: Ask for their **Name, Role, and Consulting Firm / Agency name** (e.g. `Alex Rivera, Principal Consultant at Slalom`).
2. **Turn 3 (Clients & Projects)**: Ask which **client companies** they are serving and the **product projects/engagements** under each client (e.g. `FinCorp: Mobile Banking, Cloud Migration; HealthNet: Provider Portal`).
3. **Turn 4 (Leadership Alignment)**: Ask for their **Internal Consulting Partner / Practice Lead** and any **Key Client Executive Sponsors** (both route to `#boss` priority).
4. **Turn 5 (Telemetry, Optional)**: Ask how evidence is captured per client (client-specific channels vs pasted transcripts).

Apply responses:
```bash
python3 system/scripts/ftue.py configure \
  --owner "<name>" \
  --role "<role>" \
  --org-type consulting \
  --firm "<firm>" \
  --manager "<internal_partner>" \
  --clients "<client_projects_mapping>" \
  --client-sponsors "<sponsors_mapping>"
```

This automatically provisions:
- `8. Clients/<Client_Name>/CLIENT_OVERVIEW.md` dossiers.
- `5. Trackers/workstreams/<client>-<project>.md` for cross-client task routing.
- Unified cross-client portfolio in `SETTINGS.md`.
- Client sponsors in `4. People/PEOPLE.md`.

All profile details remain strictly local in gitignored files (`SETTINGS.md`, `4. People/`, `8. Clients/`).

## Step 4: Obsidian Vault Integration (Optional)

Run:

```bash
python3 system/scripts/obsidian_bridge.py guide --json
```

Inform the user that Obsidian is optional:
- `kit_folder` is the folder to choose in Obsidian's **Open folder as vault** picker.
- `task_folder` is the canonical `5. Trackers/tasks/` note folder.
- `task_master` is its generated navigation view.

Offer `/obsidian setup` to configure the existing kit folder directly as the vault.

---

## Step 5: System Ready & First Commands

Display the completion banner:

```text
 ▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
▌   ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗   ██████╗  ▐
▌   ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║  ██╔═══██╗ ▐
▌   ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║  ██║   ██║ ▐
▌   ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║  ██║   ██║ ▐
▌   ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║  ╚██████╔╝ ▐
▌   ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝   ╚═════╝  ▐
▌      [ ◈ S Y S T E M   L O A D E D   ::   R E A D Y  ◈ ]           ▐
 ▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞
```

Show first useful commands:

```text
Ready to roll. Start here:

  /paste       Process messy PM input into routed tasks, questions, or docs
  /day         See current priorities and triage questions
  /track       Manage local task state
  /obsidian    Set up or open the optional visual task workspace
  /transcript  Prepare and validate meeting transcripts
  /create      Draft PRDs, specs, and one-pagers
  /plan        Build roadmaps, OKRs, and strategic plans
  /help        Full command reference
```

Route any remaining user input through `system/scripts/pm_decision_router.py`.
