# Using Beats PM Brain with Notion

> Step-by-step guide for Notion users

---

## Two Ways to Use This

### Option A: Notion as Your Viewer (Recommended Hybrid)

Keep the markdown files as your source of truth, sync to Notion for pretty viewing

### Option B: Notion Native

Import the structure into Notion and adapt the workflow

---

## Option A: Hybrid Setup (Markdown + Notion Sync)

### Step 1: Set Up Your PM Brain Folder

Download this repository to a synced folder (Dropbox, iCloud, OneDrive, Google Drive)

### Step 2: Use Antigravity/Claude for AI Processing

The AI agents work best with direct file access. Use:

- Antigravity (recommended)
- Claude Code
- Cursor

### Step 3: Sync Key Files to Notion

Use a tool like **Notion Markdown Importer** or manually copy key outputs:

| What to Sync        | How Often       |
| ------------------- | --------------- |
| Morning/EOD Briefs  | Daily           |
| Weekly Summary      | Weekly          |
| Critical Items      | As needed       |
| Stakeholder Updates | Before meetings |

### Step 4: Create a Notion Dashboard

Build a dashboard in Notion that links to your synced content

---

## Option B: Notion Native Setup

### Step 1: Create the Folder Structure

Create these pages/databases in Notion:

```
🧠 PM Brain
├── ⚙️ Settings
├── 📥 Inbox (Database)
├── 🔥 Critical
│   ├── Boss Requests (Database)
│   └── Escalations (Database)
├── 🐛 Bugs (Database)
├── 💬 Feedback
│   └── Feature Requests (Database)
├── 👥 People
│   ├── Stakeholders (Database)
│   └── Team (Database)
├── 📊 Projects (Database)
├── 🎯 Strategy
│   ├── Opportunities (Database)
│   └── Decisions (Database)
├── 📅 Meetings
│   └── Briefs (Database)
└── 🤖 Agents (Page with agent prompts)
```

### Step 2: Copy Agent Prompts

Create a page called "Skills" and paste the contents of each file from `.agent/skills/`

### Step 3: Use with Notion AI

1. Open an agent prompt page
2. Select all the text
3. Use Notion AI: "Use this as instructions and..."
4. Give your command

---

## Database Templates

### Boss Requests Database

| Property | Type                                  |
| -------- | ------------------------------------- |
| Title    | Title                                 |
| Status   | Select (Open, In Progress, Done)      |
| Priority | Select (🔥 Critical, ⚡ Now, 📌 Next) |
| Due Date | Date                                  |
| Owner    | Person                                |
| Notes    | Text                                  |

### Bugs Database

| Property    | Type                                         |
| ----------- | -------------------------------------------- |
| Title       | Title                                        |
| Severity    | Select (P0, P1, P2, P3)                      |
| Status      | Select (New, Investigating, Fixed, Verified) |
| SLA Due     | Date                                         |
| Assigned To | Person                                       |
| Description | Text                                         |

---

## Using Notion AI with PM Brain

### Load an Agent

1. Copy contents of a skill file (e.g., `.agent/skills/daily-synth/SKILL.md`)
2. Create a new Notion page
3. Paste the agent prompt
4. Then ask Notion AI to follow those instructions

### Example Prompts

```
Following the daily-synth instructions above,
generate my morning brief based on this context:
[paste your current priorities]

Following the boss-tracker instructions above,
help me track this request:
/boss CEO wants competitive analysis by Friday
```

---

## Command Reference

When using with Notion AI, prefix with `/`:

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

## Pro Tips

1. **Use Notion's database views** - Calendar, Board, Timeline for different perspectives
2. **Create linked databases** - Same data, different views per page
3. **Use templates** - Create database templates for each item type
4. **Quick capture** - Use Notion web clipper or mobile app
5. **Sync with external tools** - Zapier/Make for automation

---

## Upgrading Your Experience

For the best AI experience with direct file access, consider using:

- **Antigravity** with markdown files (recommended)
- Sync the outputs to Notion for sharing/viewing

---

_Need help? Open an issue at [github.com/officebeats/beats-pm-kit](https://github.com/officebeats/beats-pm-kit)_
