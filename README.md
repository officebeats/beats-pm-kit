<div align="center">

# 🧠 Beats PM Antigravity Brain

### The Professional Second Brain for Product Managers

**Stop drowning in chaos. Capture everything. Let AI organize the rest.**

[![Made for Antigravity](https://img.shields.io/badge/Made%20for-Antigravity-blueviolet?style=for-the-badge&logo=google)](https://antigravity.google/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/officebeats/beats-pm-antigravity-brain?style=for-the-badge&logo=github)](https://github.com/officebeats/beats-pm-antigravity-brain)
[![GitHub Issues](https://img.shields.io/github/issues/officebeats/beats-pm-antigravity-brain?style=for-the-badge&logo=github)](https://github.com/officebeats/beats-pm-antigravity-brain/issues)

</div>

---

## ✨ Overview

As a Product Manager, you're constantly bombarded with information: Slack messages, meeting transcripts, screenshots of bugs, and "quick asks" from your boss.

The **Antigravity Brain** is a local-first system designed to catch all that noise and turn it into professional artifacts (Product Specs, Bug Trackers, and Daily Briefs) automatically.

**No more manual entry. No more lost notes.**

---

## 🚀 Quick Start (60 Seconds)

### 📖 Step 1: Get the App

Download **[Google Antigravity](https://antigravity.google/)** (it's free).

### 📥 Step 2: Load the Brain

Download this project as a ZIP file and drag the extracted folder directly into the **Antigravity** app.

> **Advanced:** Or clone directly into your workspace:
>
> ```bash
> git clone https://github.com/officebeats/beats-pm-antigravity-brain.git
> ```

### 🎯 Step 3: Run the Wizard

Once the folder is open in Antigravity, just type or copy this into the chat:

```text
#start
```

**Antigravity will handle the rest**, automatically setting up your team profile and securing your privacy permissions.

---

---

## ⚡ Gemini-Native Architecture (v3.0.0 - Skills Protocol)

This edition is re-engineered as a **Skills-First Orchestration** system. It leverages the latest **Gemini CLI Agent Skills** protocol for maximum efficiency, modularity, and speed.

- **Dynamic Skill Activation**: Expertise is lazy-loaded on-demand. The system identifies which "Agent Skill" to activate based on your command, saving massive amounts of context tokens.
- **Parallel Fan-Out**: Expert agents execute non-dependent tasks simultaneously using the `waitForPreviousTools: false` protocol.
- **Conductor-First Protocol**: All artifacts (PRDs, Bugs, Strategy Memos) are generated via hierarchical `.gemini/templates/` managed by the Gemini CLI Conductor.
- **Access Override Fallback**: High-performance local file access protocol ensures gitignored files are always readable by the AI agents.

---

## 🤖 Meet Your AI Team

You aren't just talking to one AI. You have a mesh of specialized "experts" working for you in the background. Each agent has a specific role and expertise.

### 📋 Core Agents

|         Agent          | Role                         | What It Does                                                                                                   |
| :--------------------: | :--------------------------- | :------------------------------------------------------------------------------------------------------------- |
|    **Boss Tracker**    | 🔥 Critical Priority Monitor | Never lets a boss request slip. All boss asks are Critical by default. Monitors deadlines and sends alerts.    |
|     **Bug Chaser**     | 🐛 Quality Control           | Follows up on bugs by SLA. Automatically triages issues into "Red", "Yellow", and "Green" priority levels.     |
|  **Visual Processor**  | 👁️ The Eyes                  | Reads screenshots of Slack, Figma, or your App to understand context and route to the right agent.             |
| **Daily Synthesizer**  | 📅 Personal Assistant        | Prepares your `#morning`, `#lunch`, and `#eod` briefs so you always know what's next.                          |
| **Weekly Synthesizer** | 📊 Rollup Specialist         | Generates weekly and monthly summaries with accomplishments, metrics, and strategy pulse.                      |
|    **Task Manager**    | 🧩 The Glue                  | Prevents things from slipping through cracks. Owns task lifecycle, brain dump triage, and clarification flows. |

### 📝 Documentation Agents

|            Agent            | Role                        | What It Does                                                                                               |
| :-------------------------: | :-------------------------- | :--------------------------------------------------------------------------------------------------------- |
|       **PRD Author**        | 📄 High-Fidelity Documenter | Translates strategy into technical blueprints. Creates "Dual-Audience" PRDs for executives and engineers.  |
| **Requirements Translator** | 🔄 Primary Router           | Transforms chaotic input into structured, routed artifacts. Zero friction capture.                         |
|   **Meeting Synthesizer**   | 🗣️ Meeting Orchestrator     | Parses conversations, detects Product Context, and transforms raw meeting input into structured artifacts. |

### 👥 Collaboration Agents

|            Agent             | Role                     | What It Does                                                                                 |
| :--------------------------: | :----------------------- | :------------------------------------------------------------------------------------------- |
| **Engineering Collaborator** | 🔧 PM-Eng Bridge         | Tracks spikes, questions, estimates, and architecture decisions. Bridges PM and engineering. |
|     **UX Collaborator**      | 🎨 PM-UX Bridge          | Tracks design tasks, surfaces needs from strategy, and bridges PM and UX teams.              |
|   **Stakeholder Manager**    | 📢 Communication Expert  | Proactive stakeholder communication. Updates before they ask.                                |
|    **Delegation Manager**    | ✅ Accountability Expert | Tracks tasks assigned to others. Ensures no task handed off falls through cracks.            |

### 🧠 Strategy Agents

|          Agent           | Role                  | What It Does                                                                       |
| :----------------------: | :-------------------- | :--------------------------------------------------------------------------------- |
| **Strategy Synthesizer** | 💡 Insights Generator | Transforms operational data into strategic insights. Surfaces patterns and trends. |

---

## 🎮 Complete Command Reference

The Brain uses **Zero-Friction Routing**. You don't need to know which agent is which; just use the hashtags. The system's **Universal Orchestration Protocol** will automatically identify the intent and trigger the correct expert agent.

### 📅 Daily Briefing Commands

|  Command   | Focus                | What It Does                                                                                      |
| :--------: | :------------------- | :------------------------------------------------------------------------------------------------ |
|   `#day`   | **The Master Brief** | Context-aware summary (Morning/Lunch/EOD) of what matters most right now. Adapts to current time. |
| `#morning` | Morning Routine      | Your start-of-day punch list including Critical Boss requests and Calendar.                       |
|  `#lunch`  | Mid-day Pivot        | A quick pulse check on what's left for the afternoon.                                             |
|   `#eod`   | Wrap Up              | "End of Day" summary and a preview of tomorrow's priorities.                                      |
| `#status`  | Status Check         | Alias for `#day` - shows current status.                                                          |
| `#latest`  | Latest Updates       | Alias for `#day` - shows latest information.                                                      |
|  `#info`   | Information          | Alias for `#day` - shows current information.                                                     |

### 📥 Capture & Import Commands

|    Command    | Focus              | What It Does                                                                          |
| :-----------: | :----------------- | :------------------------------------------------------------------------------------ |
|   `#paste`    | **Magic Import**   | Pulls whatever is on your Clipboard (Files, Images, or Text) into the system.         |
| `#clipboard`  | Clipboard Import   | Alias for `#paste`.                                                                   |
| `#screenshot` | Screenshot Capture | Captures clipboard image to staging area.                                             |
|  `#process`   | Logic Commit       | Tells agents to analyze, move, and organize everything currently in your "Drop Zone". |

### 📄 Documentation Commands

|       Command       | Focus           | What It Does                                                                |
| :-----------------: | :-------------- | :-------------------------------------------------------------------------- |
|  `#prd [subject]`   | Document Author | Translates strategy into a high-fidelity PRD (Executive Logic + Eng Specs). |
|  `#feature [text]`  | Strategic Asks  | Documents a new feature request or strategic improvement with Source Truth. |
| `#braindump [text]` | Random Thoughts | Parks unstructured thoughts in `BRAIN_DUMP.md` for later triage.            |

### 🗣️ Meeting Commands

|        Command        | Focus              | What It Does                                                                 |
| :-------------------: | :----------------- | :--------------------------------------------------------------------------- |
| `#transcript [paste]` | Call Audio/Text    | Extracts action items, decisions, and roadmap concepts from raw transcripts. |
|  `#meeting [paste]`   | Hand-written Notes | Converts raw notes into structured artifacts with owners and deadlines.      |
|   `#call [subject]`   | Sync Capture       | Quick capture protocol for phone calls or unscheduled sync messages.         |
|   `#1on1 [person]`    | People Sync        | Templated sync for performance tracking and feedback loops.                  |
|      `#standup`       | Team Pulse         | Optimized capture for daily engineering or pod standups.                     |
|   `#notes [paste]`    | Raw Notes          | Raw notes dump for processing.                                               |

### 🧠 Strategy Commands

|          Command          | Focus           | What It Does                                                                         |
| :-----------------------: | :-------------- | :----------------------------------------------------------------------------------- |
|        `#strategy`        | Insights        | Generates a high-fidelity brief using current "signals" from bugs and user feedback. |
|     `#strategy pulse`     | Pattern Check   | Weekly check for recurring themes across all project and bug trackers.               |
| `#strategy theme [name]`  | Theme Deep Dive | Deep dive into a specific strategic theme.                                           |
| `#strategy opportunities` | Opportunities   | Lists opportunity cards from strategy analysis.                                      |

### 🎨 Design Commands

|     Command     | Focus          | What It Does                                                         |
| :-------------: | :------------- | :------------------------------------------------------------------- |
|  `#ux [text]`   | Design Tasks   | Routes UI/UX experiments, mockups, or design debt to the UX tracker. |
| `#ux discovery` | Discovery Task | Creates a UX discovery task.                                         |
| `#ux wireframe` | Wireframe Task | Creates a wireframe task.                                            |
|  `#ux mockup`   | Mockup Task    | Creates a mockup task.                                               |
| `#ux prototype` | Prototype Task | Creates a prototype task.                                            |
|  `#ux [name]`   | Assigned Task  | Creates a UX task assigned to a specific person.                     |

### 🔧 Engineering Commands

|     Command     | Focus              | What It Does                                                                           |
| :-------------: | :----------------- | :------------------------------------------------------------------------------------- |
|  `#eng [text]`  | Tech Tasks         | Routes architecture questions, tech debt, or dev-ops items to the Engineering tracker. |
|  `#eng spike`   | Technical Spike    | Creates a dedicated investigation task.                                                |
| `#eng question` | Quick Question     | Creates a quick question task.                                                         |
| `#eng discuss`  | Discussion Needed  | Creates a task requiring a meeting.                                                    |
| `#eng estimate` | Estimation Request | Creates an effort estimation request.                                                  |
|  `#eng [name]`  | Assigned Task      | Creates an engineering task assigned to a specific person.                             |
| `#eng standup`  | Standup Agenda     | Creates a standup agenda item.                                                         |

### 📋 Task Management Commands

|    Command     | Focus          | What It Does                                                 |
| :------------: | :------------- | :----------------------------------------------------------- |
| `#task [text]` | General Action | Captures a general task or action item for project tracking. |
|    `#tasks`    | Show Tasks     | Shows current `ACTION_PLAN.md` with status.                  |
|   `#clarify`   | Process Queue  | Processes clarification queue, asks user for input.          |
|   `#triage`    | Run Triage     | Runs full brain dump triage.                                 |
|    `#plan`     | Rebuild Plan   | Rebuilds `ACTION_PLAN.md` from all sources.                  |

### 🛠️ System Commands

|      Command       | Focus           | What It Does                                                                  |
| :----------------: | :-------------- | :---------------------------------------------------------------------------- |
|     `#update`      | Logic Sync      | Fetches latest brain mesh and runs `core_setup.py` to ensure platform parity. |
|      `#help`       | User Guide      | Displays the full Command Menu and provides an onboarding assist.             |
|      `#vibe`       | Diagnostics     | Runs system health diagnostics.                                               |
| `/conductor:[cmd]` | Direct Template | Direct access to Gemini CLI Conductor templates.                              |

### 📊 Reporting Commands

|  Command   | Focus          | What It Does                                  |
| :--------: | :------------- | :-------------------------------------------- |
| `#weekly`  | Weekly Summary | Generates weekly summary (Friday).            |
| `#monthly` | Monthly Rollup | Generates monthly rollup (last day of month). |

---

## 💡 Best Practices

### 🌅 Daily Workflow

1.  **Start Your Day**: Type `#morning` to get your daily brief with critical boss requests and calendar items.
2.  **Capture Everything**: Use `#paste` to quickly import screenshots, files, or text from your clipboard.
3.  **Process Regularly**: Run `#process` at least once a day to organize items in your Drop Zone.
4.  **End Your Day**: Type `#eod` to wrap up and preview tomorrow's priorities.

### 📸 Information Capture

- **Screenshots**: Copy any image (Ctrl+C) and type `#paste` to capture bugs, UI issues, or design feedback.
- **Files**: Copy any file (PDF, Excel, Word) and type `#paste` to import documents directly.
- **Meeting Notes**: Use `#meeting` for structured notes, `#transcript` for call recordings, or `#standup` for team syncs.
- **Quick Thoughts**: Use `#braindump` to park unstructured ideas for later triage.

### 🎯 Command Usage Tips

- **Use Hashtags**: Always start commands with `#` for automatic routing to the right agent.
- **Be Specific**: When logging bugs or features, include as much context as possible.
- **Track Boss Requests**: Use `#boss` for leadership requests to ensure high visibility.
- **Delegate Wisely**: Use `#delegate` to track tasks assigned to others across projects.

### 🔒 Privacy & Security

- **Local-First**: All data stays on your computer—nothing is sent to the cloud.
- **Control Access**: Review privacy permissions during setup to ensure appropriate access.
- **Regular Backups**: Since data is stored as text files, use your preferred backup solution.

---

## 📸 The Secret Sauce: Screenshot → Action

The Beats Brain is optimized for **Gemini** (Google's AI), which has the best "eyes" in the world.

**The Workaround:** Since Antigravity doesn't have a "File Upload" button yet, we built a pro workaround. Just **Copy** (Ctrl+C) any image or file, then type **`#paste`** in the chat.

The AI will autonomously reach out, grab your clipboard, and start analyzing:

- 🐞 **Capture a Bug**: Paste a screenshot of a crash → The AI logs it to the Bug Tracker.
- 📁 **Instant File Upload**: Press **Ctrl+C** on any **PDF, Excel, or Word doc** in your File Explorer, then type **`#paste`** → The AI pulls the actual file into your brain.
- 💬 **Meeting Notes**: Paste a call transcript → The AI extracts action items for your team.

---

### [🤖 Antigravity Auto-Accept](https://open-vsx.org/vscode/item?itemName=pesosz.antigravity-auto-accept)

**Autonomous Execution.**

Allows your Brain to execute standard system commands (like file moves or status checks) autonomously without requiring manual approval for every step.

**Manual Installation**:

```bash
antigravity --install-extension pesosz.antigravity-auto-accept
```

---

## 🔒 Privacy First

Your data **never leaves your computer**.

- ✅ All your notes, bugs, and plans are stored as simple text files on your hard drive.
- ✅ You own the data.
- ✅ No cloud subscription required.

---

## ❓ Frequently Asked Questions

<details>
<summary><strong>🤔 Do I need to be technical to use this?</strong></summary>

**No!** The system is designed for both technical and non-technical users. The AI handles all the complex routing and organization. You just need to type simple commands like `#paste` or `#morning`.

</details>

<details>
<summary><strong>❓ What if I don't know which command to use?</strong></summary>

Just describe what you want to do in plain English. The AI will figure out the right command and agent to use. For example, you can say "I need to log a bug" and it will route to the Bug Chaser.

</details>

<details>
<summary><strong>🏢 Can I use this with multiple products/companies?</strong></summary>

**Yes!** The system supports multi-product and multi-company workflows. It automatically detects context from your input and routes items to the correct trackers.

</details>

<details>
<summary><strong>🆘 What happens if I forget a command?</strong></summary>

Type `#help` anytime to see the full command menu. The AI will also suggest commands based on what you're trying to do.

</details>

<details>
<summary><strong>🔐 Is my data secure?</strong></summary>

**Absolutely.** Your data is stored locally on your computer as plain text files. Nothing is sent to the cloud. You have full control and ownership of your data.

</details>

<details>
<summary><strong>⚙️ Can I customize the system?</strong></summary>

**Yes!** The system is highly customizable. You can modify templates, adjust agent behaviors, and extend functionality to fit your specific workflow.

</details>

<details>
<summary><strong>🔧 What if something goes wrong?</strong></summary>

Type `#vibe` to run system diagnostics. The AI will check for issues and provide guidance on how to fix them.

</details>

---

## 🔧 For Technical Users

### 🏗️ System Architecture

The Beats PM Brain uses a **mesh architecture** with specialized agents that communicate through the **Universal Orchestration Protocol**. Each agent has a specific responsibility and can orchestrate other agents as needed.

### 📁 File Structure

```
beats-pm-antigravity-brain/
├── 0. Incoming/           # Drop zone for new items
├── 1. Company/            # Company profiles and context
├── 2. Products/           # Product specs and PRDs
├── 3. Meetings/           # Meeting notes and transcripts
├── 4. People/             # Stakeholder profiles
├── 5. Trackers/           # All tracking files
│   ├── bugs/             # Bug tracking
│   ├── critical/         # Boss requests and escalations
│   ├── feedback/         # User feedback
│   ├── people/           # Eng/UX tasks
│   ├── projects/         # Project tracking
│   └── strategy/         # Strategy documents
├── Beats-PM-System/
│   ├── TEMPLATES/        # Document templates
│   ├── docs/             # Documentation
│   ├── examples/         # Example files
│   └── system/
│       ├── agents/       # Agent configurations
│       ├── scripts/      # Utility scripts
│       └── queue/        # Processing queues
└── STATUS.md             # Current status dashboard
```

### 🔌 Extending the System

You can extend the system by:

1. **Adding New Agents**: Create agent files in `Beats-PM-System/system/agents/`
2. **Creating Templates**: Add templates to `Beats-PM-System/TEMPLATES/`
3. **Writing Scripts**: Add utility scripts to `Beats-PM-System/system/scripts/`
4. **Modifying Workflows**: Adjust agent behaviors by editing their configuration files

### 🧪 System Testing (Regression Suite)

To ensure the Brain is functioning correctly after updates, run the regression test suite located in `tests/`.

```bash
# Run Core Logic Tests (Clipboard, Context Loader)
python tests/test_core_components.py

# Run Structural Integrity Tests (Files, Config, Agents)
python tests/test_structure.py
```

---

## 🤝 Contributing

This is an open-source project. Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

## 👤 Created By

**[Your Name]** — Product Management leader & AI enthusiast.

<div align="center">

<a href="https://www.linkedin.com/in/productmg/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="https://x.com/officebeats"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white" alt="X/Twitter"></a>
<a href="mailto:Ernesto@ProductMG.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"></a>

---

<strong>Built by PMs, for PMs.</strong><br>
<em>Stop chasing status updates. Start driving strategy.</em>

</div>
