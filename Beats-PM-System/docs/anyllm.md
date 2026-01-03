# Using Beats PM Brain with Any LLM

> Universal guide for ChatGPT, Claude.ai, Gemini, Copilot, or any AI assistant

---

## The Agents Are Portable Markdown

The magic of this system is that the agents in `system/agents/` are just markdown files with detailed prompts. You can copy-paste them into **any** LLM.

---

## Quick Setup (Any LLM)

### Step 1: Download the Brain

Download this repository to your computer

### Step 2: Open Your Favorite LLM

- ChatGPT (chat.openai.com)
- Claude (claude.ai)
- Gemini (gemini.google.com)
- Copilot
- Any other AI chat

### Step 3: Paste an Agent Prompt

1. Open the agent file you want to use from `system/agents/`
2. Copy the entire contents
3. Paste it into your LLM chat
4. Start interacting!

---

## Which Agent to Use?

| I want to...                    | Use this agent                |
| ------------------------------- | ----------------------------- |
| Organize my messy thoughts      | `requirements-translator.md`  |
| Get my morning/daily brief      | `daily-synthesizer.md`        |
| Get my weekly summary           | `weekly-synthesizer.md`       |
| Track boss requests             | `boss-tracker.md`             |
| Track and chase bugs            | `bug-chaser.md`               |
| Manage stakeholder updates      | `stakeholder-manager.md`      |
| Work with engineering           | `engineering-collaborator.md` |
| Work with UX/design             | `ux-collaborator.md`          |
| Find patterns and opportunities | `strategy-synthesizer.md`     |

---

## Example: Using Daily Synthesizer

1. Open `system/agents/daily-synthesizer.md`
2. Copy entire contents
3. Paste into ChatGPT/Claude/etc
4. Then say: "Generate my morning brief"
5. Provide any context it asks for

---

## Command Reference

When talking to the LLM with an agent loaded, use these commands:

| Command       | Action                   |
| ------------- | ------------------------ |
| `#boss`       | Boss request (Critical)  |
| `#bug`        | Bug entry                |
| `#task`       | Task                     |
| `#feature`    | Feature request          |
| `#ux`         | UX task                  |
| `#eng`        | Engineering item         |
| `#note`       | Quick note               |
| `#transcript` | Paste meeting transcript |
| `#morning`    | Morning brief            |
| `#lunch`      | Midday brief             |
| `#eod`        | End of day brief         |
| `#weekly`     | Weekly summary           |
| `#monthly`    | Monthly summary          |

---

## Managing Your Files

Since web-based LLMs can't access your local files directly:

1. **Copy-paste content** from your markdown files when needed
2. **Copy the AI's output** back to your local files
3. **Use file sync** (Dropbox, iCloud, OneDrive) to access from anywhere

---

## Pro Tips

1. **Save agent prompts as favorites** in your LLM for quick access
2. **Use Custom GPTs** (ChatGPT Plus) to create a dedicated PM assistant
3. **Use Claude Projects** to save agents as project knowledge
4. **Chain agents** - use output from one as input to another

---

## Upgrading Your Experience

For a more seamless experience where the AI can directly read/write your files, consider:

- **[Antigravity](https://antigravity.google/)** - Recommended, full folder access
- **Claude Code** - Terminal-based, full file access
- **Cursor** - IDE-based, great for file management
- **Gemini CLI** - Terminal-based, file access

---

_Need help? Open an issue at [github.com/officebeats/beats-pm-antigravity-brain](https://github.com/officebeats/beats-pm-antigravity-brain)_
