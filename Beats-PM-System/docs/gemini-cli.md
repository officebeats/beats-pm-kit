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

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
