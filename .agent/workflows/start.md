---
description: First-time guided setup wizard. Run on first session or manually with /start.
---

> **Compatibility Directive**: Works across Antigravity, Gemini CLI, Claude Code, and KiloCode.

# /start — Welcome Wizard

**Trigger**: `/start` or auto-triggered on first session if `.initialized` marker is missing.

---

## Step 0: Detect Runtime

// turbo
```bash
python3 system/scripts/detect_runtime.py --human
```

Display the detected runtime and capabilities to the user.

---

## Step 1: Welcome Banner

Display this greeting:

```
🧠 Welcome to the Beats PM Kit!

The AI Operating System that thinks like a 10x Product Manager.
Let's get you set up in under 2 minutes.
```

---

## Step 2: Collect User Profile (Interactive — 3 Questions)

Ask these questions one at a time. Wait for each answer before proceeding.

### Q1: Your Name
> "What's your name? (This is used for task ownership and document headers)"

→ Store response in `SETTINGS.md` under `owner_name`.

### Q2: Your Manager
> "Who's your direct manager? (Name and title if you know it — this seeds the Boss Protocol)"

→ Create `4. People/{manager-name}.md` with:
  - Role: [title if provided, or "Direct Manager"]
  - Relationship: Direct Manager (Boss)
  - Source: /start wizard setup

→ Store manager name in `SETTINGS.md` under `boss_name`.

### Q3: Product Focus
> "What product or initiative are you focusing on? (e.g., 'Platform API', 'Mobile App v3', 'AI Search')"

→ Store in `SETTINGS.md` under `product_focus`.

---

## Step 3: Initialize Trackers

After collecting answers, seed the tracker files:

1. Update `5. Trackers/TASK_MASTER.md` — replace `[Your Name]` with the user's name.
2. Update `5. Trackers/critical/boss-requests.md` — add manager name as header context.
3. Create `.initialized` marker file in root (empty file, gitignored).

---

## Step 4: Show the Playbook

Display the Diamond 6 commands:

```
✅ You're all set! Here's your command playbook:

  /paste    — Copy anything → auto-extract tasks & bugs
  /day      — Daily dashboard with priorities & boss asks  
  /track    — Manage your task ledger
  /meet     — Synthesize meeting transcripts → action items
  /create   — Generate PRDs, specs, and one-pagers
  /plan     — Build roadmaps, OKRs, and strategy docs

  /help     — Full command reference
  /outlook  — Sync your inbox for context (macOS + Outlook)

💡 Tip: Start with /day to see your daily priorities, or /paste to capture something from your clipboard.
```

---

## Step 5: Confirm

Tell the user:
```
Your setup is saved. This wizard won't run again automatically.
To re-run it anytime: type /start

Happy shipping! 🚀
```
