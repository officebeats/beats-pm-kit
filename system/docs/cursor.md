# Using Beats PM Brain with Cursor

> Step-by-step guide for Cursor IDE users

---

## Quick Setup

### Step 1: Open Your PM Brain Folder

1. Open **Cursor**
2. Go to **File → Open Folder**
3. Select your `beats-pm-antigravity-brain` folder

### Step 2: Open the Chat Panel

Press `Cmd+L` (Mac) or `Ctrl+L` (Windows) to open Cursor's AI chat

### Step 3: Initialize the Brain

In the chat, type:

```
I'm using the Beats PM Antigravity Brain system.
Please read the _AGENTS folder to understand the available agents,
and read SETTINGS.md for my configuration. Help me get started.
```

### Step 4: Start Capturing

Now use the chat for PM work:

```
/boss CFO needs budget projections by Monday
/bug Login fails for SSO users
/morning
```

---

## Adding Files to Context

Use `@` to reference specific files in your prompts:

```
@.agent/skills/daily-synth/SKILL.md Generate my morning brief

@5. Trackers/critical/boss-requests.md What's overdue?

@5. Trackers/bugs/bugs-master.md Show me P0 bugs
```

---

## Using .cursorrules (Optional)

Create a `.cursorrules` file in your PM brain folder to auto-load context:

```
You are helping me manage my PM work using the Beats PM Antigravity Brain system.

Key files to be aware of:
- .agent/skills/ contains AI skill prompts for different PM functions
- SETTINGS.md contains my personal configuration
- 5. Trackers/critical/ contains boss requests and escalations
- 5. Trackers/bugs/ contains bug tracking
- 0. Incoming/ is where I drop raw items to be processed

When I use / commands, process them according to the skill definitions.
```

---

## Command Reference

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

## Composer Mode

For longer workflows, use Cursor's Composer (`Cmd+I` / `Ctrl+I`):

```
Read all the files in system/agents/ and then:
1. Process everything in system/inbox/
2. Generate my morning brief
3. List all items that need follow-up today
```

---

## Pro Tips

1. **Pin your SETTINGS.md** to always have your config visible
2. **Use Cursor's @ mentions** to reference specific folders or files
3. **Split view** - keep your briefs on one side, capture on the other
4. **Use keyboard shortcuts** - `Cmd+L` for quick chat access

---

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
