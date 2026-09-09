---
title: 'Beats PM Kit — First Time User Experience (FTUE)'
---

# ◈ BEATS PM KIT :: FIRST TIME SETUP GUIDE ◈

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

Welcome to **Beats PM Kit** — the agentic, local-first PM operating system.

---

## ⚡ Super-Fast Quickstart

### Option A: Guided via AI Agent (Recommended)

Open this folder in your AI harness (**Codex**, **Antigravity**, **Claude Code**, or **Gemini CLI**) and type:

```text
/start
```

The agent will automatically bootstrap your workspace and guide you through 3 simple setup questions:
1. **Identity Matrix**: Your name, role, and manager (for boss-request routing).
2. **Product Grid**: Your core products or focus initiatives.
3. **Evidence Streams**: Where your daily input comes from (Slack, Teams, Outlook, Granola, Quill, or pasted text).

### Option B: Terminal Command Line (Instant)

#### In-House Product Setup:

```bash
python3 system/scripts/ftue.py configure \
  --owner "Alex Rivera" \
  --role "Senior Product Manager" \
  --manager "Sarah Chen" \
  --products "Mobile App, Web Dashboard, Core API"
```

#### Consulting & Agency Setup (Multi-Client & Multi-Project):

If you work for a consulting firm or advisory practice managing multiple clients and projects:

```bash
python3 system/scripts/ftue.py configure \
  --owner "Alex Rivera" \
  --role "Principal Consultant" \
  --org-type consulting \
  --firm "Apex Strategy Partners" \
  --manager "Sarah Jenkins" \
  --clients "FinCorp: Mobile Banking, Cloud Migration; HealthNet: Provider Portal" \
  --client-sponsors "FinCorp: VP Jane Doe; HealthNet: CTO Mark Davis"
```

This automatically:
1. Maps your consulting firm and internal partner.
2. Creates dedicated client dossiers under `8. Clients/<Client_Name>/CLIENT_OVERVIEW.md`.
3. Seeds workstream notes under `5. Trackers/workstreams/` for each client project.
4. Sets up cross-client task routing and boss-priority triggers for both internal leadership and client sponsors.

Check your configuration status anytime:

```bash
python3 system/scripts/ftue.py status
```

---

## ◈ 3-Step Setup Matrix

### Step 1: Identity Matrix
- **Owner**: Sets local task ownership so assigned tasks route to your personal queue.
- **Role**: Context for PRDs, executive memos, and strategy docs.
- **Manager**: Identifies leadership requests for automatic priority bumping (`#boss`).

### Step 2: Portfolio Matrix (In-House or Consulting)
- **In-House**: Define your core products (e.g. Mobile App, Web Portal).
- **Consulting**: Define your client companies and the one-to-many projects/engagements under each client (e.g. `ClientA: Project 1, Project 2`). Beats PM Kit isolates client context in `8. Clients/` while giving you a unified cross-client task ledger.
### Step 3: Evidence Telemetry
Beats PM Kit triangulates truth across your daily tools:
- **Chat**: Read-only source windows for Slack / Teams.
- **Email & Calendar**: Outlook / Google Calendar windows.
- **Transcripts**: Granola / Quill meeting recordings or pasted text.

---

## 🚀 First Useful Commands

Once configured, jump straight into real PM work:

| Command | Action |
| :--- | :--- |
| `/paste` | Paste raw email threads, chat transcripts, or messy notes to extract routed tasks |
| `/day` | View today's priorities, overdue items, and triage questions |
| `/track` | Manage the local task ledger (`5. Trackers/tasks/`) |
| `/obsidian` | Open the optional direct-vault Obsidian visual workspace |
| `/transcript` | Process and validate call recordings and meeting notes |
| `/create` | Draft PRDs, user stories, and specs |
| `/plan` | Generate roadmaps, OKRs, and executive memos |
| `/help` | Complete catalog of available PM skills and commands |

---

## 🔒 Privacy Guarantee

All personal settings, stakeholder names, and task files stay strictly local in gitignored files (`SETTINGS.md`, `4. People/`, `5. Trackers/`). Nothing is committed to public source control.
