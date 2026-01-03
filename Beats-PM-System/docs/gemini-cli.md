# Using Beats PM Brain with Gemini CLI

> Step-by-step guide for Gemini CLI users

---

## Quick Setup

### Step 1: Navigate to Your PM Brain

```bash
cd /path/to/your/beats-pm-antigravity-brain
```

### Step 2: Start Gemini CLI

```bash
gemini
```

### Step 3: Initialize the Brain

Tell Gemini about your PM system:

```
I'm using the Beats PM Antigravity Brain system in this folder.
Please read the _AGENTS folder to understand the available agents,
and read SETTINGS.md for my personal configuration.
```

### Step 4: Start Working

Now use natural language or # commands:

```
#boss CEO wants a product demo next Tuesday
#bug Users can't reset their passwords
#morning
```

---

## Using Agents as System Prompts

You can use individual agent files as system prompts for focused sessions:

```bash
# For a daily brief session
gemini --system-instruction "system/agents/daily-synthesizer.md"

# For bug triage
gemini --system-instruction "system/agents/bug-chaser.md"

# For stakeholder management
gemini --system-instruction "system/agents/stakeholder-manager.md"
```

---

## Command Reference

| Command       | Action                                  |
| ------------- | --------------------------------------- |
| `#boss`       | Boss request (Critical)                 |
| `#bug`        | Bug entry                               |
| `#task`       | Task                                    |
| `#feature`    | Feature request                         |
| `#ux`         | UX task                                 |
| `#eng`        | Engineering item                        |
| `#note`       | Quick note                              |
| `#transcript` | Paste meeting transcript for processing |
| `#morning`    | Morning brief                           |
| `#lunch`      | Midday brief                            |
| `#eod`        | End of day brief                        |
| `#weekly`     | Weekly summary                          |
| `#monthly`    | Monthly summary                         |

---

## Workflow Examples

### Morning Routine

```
#morning
```

### Capture from a Meeting

```
#transcript
[paste your meeting transcript here]
```

### Track a Boss Request

```
#boss VP of Sales needs competitive analysis by end of week
```

### End of Day Wrap

```
#eod
```

---

## Pro Tips

1. **Create an alias** for quick access:

   ```bash
   alias pm='cd ~/beats-pm-antigravity-brain && gemini'
   ```

2. **Combine with file operations** - Gemini CLI can read/write your markdown files directly

3. **Use @ mentions** to reference specific files:
   ```
   @5. Trackers/critical/boss-requests.md show me open items
   ```

---

## 🎼 Using Gemini CLI Conductor

The PM Brain is pre-configured for **Conductor**, Google's context-driven development extension.

### Context Files (Already Set Up)

| File | Purpose |
| :--- | :--- |
| `.gemini/context.md` | System architecture, folder structure, agents |
| `.gemini/style-guide.md` | Markdown conventions |
| `.gemini/workflow-preferences.md` | Behavior settings |
| `.gemini/templates/` | Feature and bug-fix spec templates |

### Conductor Commands

| Command | Action |
| :--- | :--- |
| `/conductor:setup` | Already done via `.gemini/context.md` |
| `/conductor:newTrack` | Create a new spec for a feature or bug fix |
| `/conductor:implement` | Execute the plan |

### Benefits

- **Persistent Memory**: Context survives across sessions.
- **Reduced Hallucinations**: AI understands your folder structure and conventions.
- **Consistent Style**: Follows your tracker formats and Markdown patterns.

---

## 📂 Session Memory (Per-Session Persistence)

Use the `--context-file` flag for persistent session state that survives terminal restarts:

```bash
gemini --context-file .gemini/session-memory.md
```

This creates a dedicated read/write memory for the session. The agent can persist notes, focus areas, and quick references across restarts.

---

## 🗄️ Archive Rotation

Old daily briefs are auto-archived to `3. Meetings/archive/` to prevent context bloat. The archive folder is excluded from initial AI indexing but can be accessed on demand.

**Manual archive command:**
```bash
mv "3. Meetings/daily-briefs/2025-*" "3. Meetings/archive/"
```

---

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
