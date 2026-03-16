# Using Beats PM Brain with Obsidian

> Step-by-step guide for Obsidian users

---

## Why Obsidian + PM Brain?

Obsidian is perfect for this system because:

- ✅ It's built for markdown files (which is what this brain uses)
- ✅ You get beautiful rendering of your notes
- ✅ Graph view shows connections between items
- ✅ Plugins extend functionality
- ✅ Everything stays local on your machine

---

## Quick Setup

### Step 1: Download the PM Brain

Download this repository to your computer

### Step 2: Open as Obsidian Vault

1. Open **Obsidian**
2. Click **"Open folder as vault"**
3. Select your `beats-pm-antigravity-brain` folder
4. Trust the folder when prompted

### Step 3: Configure Your Settings

Open `SETTINGS.md` and edit it directly in Obsidian with your personal details

---

## Recommended Plugins

Install these community plugins for the best experience:

| Plugin        | Why                                  |
| ------------- | ------------------------------------ |
| **Dataview**  | Query tasks and items across files   |
| **Templater** | Use the TEMPLATES folder effectively |
| **Calendar**  | See briefs and meetings by date      |
| **Tasks**     | Better task management               |
| **Copilot**   | AI assistant inside Obsidian         |

---

## Using with AI (Obsidian Copilot)

If you install the **Obsidian Copilot** plugin:

1. Configure it with your API key (OpenAI, Anthropic, etc.)
2. Open any skill file from `.agent/skills/`
3. Use the AI chat to interact with your PM brain

Example prompts:

```
Based on the daily-synth skill, generate my morning brief

Look at 5. Trackers/critical/boss-requests.md and tell me what's overdue

Process this transcript and extract action items:
[paste transcript]
```

---

## Folder Structure in Obsidian

Your vault will look like this:

```
📁 beats-pm-antigravity-brain (vault)
├── 📁 _AGENTS          ← AI prompts (read these to understand the system)
├── 📁 _INBOX           ← Quick capture zone
├── 📁 _QUEUE           ← Needs your input
├── 📁 CRITICAL         ← Boss requests, escalations
├── 📁 BUGS             ← Bug tracking
├── 📁 FEEDBACK         ← Feature requests
├── 📁 PEOPLE           ← Stakeholders & team
├── 📁 PROJECTS         ← Active projects
├── 📁 STRATEGY         ← Opportunities & decisions
├── 📁 MEETINGS         ← Briefs & notes
└── 📁 TEMPLATES        ← Reusable templates
```

---

## Command Reference

When using with an AI plugin, use these `/` commands:

| Command       | Action                   |
| ------------- | ------------------------ |
| `/boss`       | Boss request (Critical)  |
| `/bug`        | Bug entry                |
| `/task`       | Task                     |
| `/feature`    | Feature request          |
| `/ux`         | UX task                  |
| `/eng`        | Engineering item         |
| `/note`       | Quick note               |
| `/transcript` | Paste meeting transcript |
| `/morning`    | Morning brief            |
| `/lunch`      | Midday brief             |
| `/eod`        | End of day brief         |
| `/weekly`     | Weekly summary           |
| `/monthly`    | Monthly summary          |

---

## Daily Workflow in Obsidian

### Morning

1. Open Obsidian
2. Ask AI: `/morning` (or manually review CRITICAL folder)
3. Check `_QUEUE` for items needing your input

### Throughout the Day

1. Quick capture to `_INBOX` with Daily Note
2. Use templates for structured entries
3. Tag items with priorities: `🔥` `⚡` `📌` `📋` `💭`

### End of Day

1. Ask AI: `/eod`
2. Review what was accomplished
3. Prep tomorrow's priorities

---

## Pro Tips

1. **Use Daily Notes** for quick capture, then process to proper folders
2. **Create hotkeys** for quick navigation to CRITICAL and \_INBOX
3. **Use Graph View** to see connections between stakeholders, projects, and bugs
4. **Star your SETTINGS.md** for quick access
5. **Template your briefs** for consistent formatting

---

## Syncing with Antigravity/Claude

You can use Obsidian for viewing/editing AND Antigravity/Claude for AI processing:

1. Keep Obsidian open for beautiful markdown editing
2. Open the same folder in Antigravity for AI commands
3. Changes sync instantly (same folder)

---

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
