# Using Beats PM Brain with Claude Code

> Step-by-step guide for Claude Code users

---

## Quick Setup

### Step 1: Open Your PM Brain Folder

```bash
cd /path/to/your/beats-pm-antigravity-brain
claude
```

### Step 2: Load the Agents

When Claude Code starts, tell it about your PM brain:

```
I'm using the Beats PM Antigravity Brain system.
Please read the _AGENTS folder to understand the available agents,
and read SETTINGS.md for my configuration.
```

### Step 3: Start Capturing

Now you can use natural language or `/` commands:

```
/boss Sarah needs the Q1 metrics by Friday
/bug The checkout page is broken on mobile Safari
/transcript [paste your meeting notes]
Give me my morning brief
```

---

## How to Use Each Agent

| Agent File                    | What It Does                   | Example Command              |
| ----------------------------- | ------------------------------ | ---------------------------- |
| `requirements-translator.md`  | Organizes chaos into structure | _"Sort through my inbox"_    |
| `daily-synth.md`              | Generates daily briefs         | `/morning`, `/lunch`, `/eod` |
| `weekly-synth.md`             | Weekly summaries               | `/weekly`                    |
| `boss-tracker.md`             | Tracks boss requests           | `/boss [request]`            |
| `bug-chaser.md`               | Bug SLA tracking               | `/bug [description]`         |
| `stakeholder-mgr.md`          | Stakeholder updates            | _"Draft update for [name]"_  |
| `engineering-collab.md`       | Engineering work               | `/eng [item]`                |
| `ux-collaborator.md`          | UX tasks                       | `/ux [task]`                 |
| `strategy-synth.md`           | Pattern recognition            | `/strategy`                  |

---

## Loading Agents as Context

For best results, you can explicitly load agents:

```
Please read .agent/skills/daily-synth/SKILL.md and generate my morning brief
```

Or load multiple:

```
Read .agent/skills/boss-tracker/SKILL.md and .agent/skills/bug-chaser/SKILL.md,
then show me all critical items I need to follow up on today
```

---

## Pro Tips

1. **Keep Claude Code open** in your PM brain folder for quick capture
2. **Use `/add` command** to add specific files to context when needed
3. **Paste transcripts** directly - Claude will extract action items
4. **Ask for briefs** at natural break points in your day

---

## Quick Reference

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

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
