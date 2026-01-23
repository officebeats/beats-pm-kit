<div align="center">

<!-- HERO BANNER -->
<img src="system/docs/assets/hero-banner.png" alt="Beats PM Antigravity Kit" width="100%"/>

<br/>

# 🧠 Beats PM Antigravity Kit

<h3><em>The AI Operating System That Thinks Like a Product Manager</em></h3>

<p><strong>Paste anything. Get structured tasks. Zero manual tracking.</strong></p>

<!-- BADGES -->
<p>
  <a href="https://github.com/officebeats/beats-pm-antigravity-brain/releases"><img src="https://img.shields.io/badge/v6.0.0-stable-00A651?style=for-the-badge&labelColor=1a1a2e" alt="Version"/></a>
  &nbsp;
  <a href="#"><img src="https://img.shields.io/badge/Powered%20by-Antigravity-00A651?style=for-the-badge&logo=google&logoColor=white&labelColor=1a1a2e" alt="Antigravity"/></a>
  &nbsp;
  <a href="https://github.com/officebeats/beats-pm-antigravity-brain/stargazers"><img src="https://img.shields.io/github/stars/officebeats/beats-pm-antigravity-brain?style=for-the-badge&logo=github&labelColor=1a1a2e&color=E6B422" alt="Stars"/></a>
  &nbsp;
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge&labelColor=1a1a2e" alt="License"/></a>
</p>

<!-- VALUE PROP PILLS -->
<p>
  <img src="https://img.shields.io/badge/🎯_FAANG_Rigor-Amazon_&_Meta_Templates-00A651?style=flat-square" alt="FAANG"/>
  &nbsp;•&nbsp;
  <img src="https://img.shields.io/badge/🔒_100%25_Local-Zero_Cloud_Storage-00A651?style=flat-square" alt="Privacy"/>
  &nbsp;•&nbsp;
  <img src="https://img.shields.io/badge/💸_Free_Forever-Multi_Model_Rotation-00A651?style=flat-square" alt="Free"/>
</p>

<br/>

<!-- CTA BUTTONS -->
<p>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/🚀_Get_Started-in_60_seconds-00A651?style=for-the-badge" alt="Get Started"/></a>
  &nbsp;
  <a href="#-all-commands-press--to-see"><img src="https://img.shields.io/badge/📖_16_Commands-Press_/_to_see-555555?style=for-the-badge" alt="Commands"/></a>
</p>

</div>

---

## 🚀 Quick Start

### 🐣 For Everyone (Simple)

**Step 1: Get the Tools**

Install your preferred AI coding assistant:

| Tool            | Install Command                                                                             | Auth Command         |
| --------------- | ------------------------------------------------------------------------------------------- | -------------------- |
| **Gemini CLI**  | `npm install -g @anthropic-ai/claude-code`                                                  | `gemini login`       |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code`                                                  | `claude login`       |
| **Kilo Code**   | [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=kilocode.kilo-code) | Configure in VS Code |

**Step 2: Get the Brain**

1. Scroll to the top of this page.
2. Click the green **Code** button → **Download ZIP**.
3. Extract the ZIP file to a folder on your computer (e.g., `Documents/Antigravity`).

**Step 3: Launch**

1. Open your AI tool (terminal or VS Code).
2. Navigate to the extracted folder.
3. Type `/setup` and hit Enter.

### ⚡ For Engineers (Advanced)

```bash
git clone https://github.com/officebeats/beats-pm-antigravity-brain
cd beats-pm-antigravity-brain
# Type /setup in your AI CLI to initialize
```

---

## 🔧 Works With Your Favorite AI Tool

This kit uses a **single source of truth** (`.agent/`) that automatically syncs to all three major AI coding assistants via symlinks.

```
.agent/                    ← SOURCE OF TRUTH (edit here)
    │
    ├── .gemini/           ← Gemini CLI reads this
    ├── .claude/           ← Claude Code reads this
    └── .kilocode/         ← Kilo Code reads this
```

### Supported Tools

| Tool            | Config Folder | Status             |
| --------------- | ------------- | ------------------ |
| **Gemini CLI**  | `.gemini/`    | ✅ Auto-configured |
| **Claude Code** | `.claude/`    | ✅ Auto-configured |
| **Kilo Code**   | `.kilocode/`  | ✅ Auto-configured |

### Setup by Tool

<details>
<summary><strong>🟢 Gemini CLI</strong></summary>

1. Install: `npm install -g @google/gemini-cli`
2. Authenticate: `gemini login`
3. Navigate to this folder and type `gemini`
4. The kit loads automatically via `.gemini/GEMINI.md`

</details>

<details>
<summary><strong>🟣 Claude Code</strong></summary>

1. Install: `npm install -g @anthropic-ai/claude-code`
2. Authenticate: `claude login`
3. Navigate to this folder and type `claude`
4. The kit loads automatically via `.claude/CLAUDE.md`

</details>

<details>
<summary><strong>🔵 Kilo Code (VS Code)</strong></summary>

1. Install from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=kilocode.kilo-code)
2. Open this folder in VS Code
3. Kilo Code reads `.kilocode/rules/` automatically
4. Skills and workflows are pre-configured

</details>

> 💡 **Single Source of Truth**: Edit files in `.agent/` only. Changes sync to all tools automatically via symlinks.

---

## 💡 Why This Exists

**Product Management is drowning in noise.**

Slack messages piling up. Meeting notes with hidden action items. Emails that say "Can you look into this?" Screenshots of bugs you'll forget about tomorrow.

**This kit solves it—without ever touching the cloud.**

### How It Works

Copy anything to your clipboard. Type `/paste`. Watch the AI:

1. **Detect** what type of content it is (text, image, file)
2. **Extract** every hidden task, bug, and decision—even implicit ones
3. **Route** each item to the correct tracker automatically
4. **Tag** it with the correct company and product context

**No commands to memorize. No manual filing. No lost context.**

### 🔒 100% Local. 100% Private.

| Your Data           | Where It Lives                 | Cloud Access |
| :------------------ | :----------------------------- | :----------- |
| Company strategy    | `1. Company/` on YOUR machine  | ❌ Never     |
| PRDs & specs        | `2. Products/` on YOUR machine | ❌ Never     |
| Meeting transcripts | `3. Meetings/` on YOUR machine | ❌ Never     |
| Stakeholder info    | `4. People/` on YOUR machine   | ❌ Never     |
| Task trackers       | `5. Trackers/` on YOUR machine | ❌ Never     |

**No cloud sync. No telemetry. No API calls with your data.**

The AI processes everything locally. Your company secrets, roadmaps, and stakeholder notes never leave your laptop.

> 🛡️ **Enterprise-Ready**: Folders 1-5 are `.gitignored` by default. Even if you push to GitHub, your private data stays private.

---

## 💸 Free Forever (Multi-Model Architecture)

Here's the secret: **You may never pay for AI again.**

Antigravity supports multiple AI models with generous free tiers. This kit works identically across all of them.

| Model              | Provider  | Free Tier (Est.) | Best For                |
| :----------------- | :-------- | :--------------- | :---------------------- |
| **Gemini 3 Flash** | Google    | High Daily Quota | Fast daily tasks        |
| **Gemini 3 Pro**   | Google    | **Weekly Quota** | Complex PRDs & Strategy |
| **Claude Sonnet**  | Anthropic | **Weekly Quota** | Balanced work           |
| **Claude Opus**    | Anthropic | Limited Weekly   | Maximum quality         |

_\*Both Google Antigravity and Anthropic have shifted to Weekly Quotas for their best models._

### The Rotation Strategy

**Never hit a wall.** Antigravity's multi-model support means you have a massive combined pool of intelligence.

- **Primary Driver**: Use **Gemini 3 Flash** for your daily routine (`/day`, `/paste`, `/vibe`).
- **Heavy Lifting**: Switch to **Gemini 3 Pro** or **Claude Sonnet** for deep work (`/create`, `/plan`).
- **Weekly Rotation**: If you push one model hard during a "Sprint Week", simply rotate to another for the rest of the week to stay free.

**Result**: A professional-grade AI PM assistant for **$0/month**.

> 💡 **Pro Tip**: Use Flash for high-volume tasks. Save Pro/Opus for high-value reasoning.

---

## 🎯 Built for Every PM

| If You're...                            | This Kit Gives You...                                   |
| :-------------------------------------- | :------------------------------------------------------ |
| **A Startup PM** juggling chaos         | A single source of truth that auto-organizes everything |
| **A FAANG PM** with exec visibility     | Amazon 6-Pager & Meta PRD templates, Boss Ask tracking  |
| **An ex-MBB Consultant**                | Strategy frameworks built-in (MECE, SCQA, 7 Powers)     |
| **A Growth PM** running experiments     | Data-driven PRD templates with success metrics          |
| **A Platform PM** managing dependencies | Multi-company context tagging and stakeholder mapping   |

**Same tool. Adapts to your rigor level.**

---

## 🤖 Zero-Command Intelligence

The magic isn't in learning commands—it's in **not needing them**.

### What Happens When You `/paste`

| You Paste...                     | AI Detects...               | Auto-Routes To...       |
| :------------------------------- | :-------------------------- | :---------------------- |
| "Can you fix the checkout bug?"  | **Bug**                     | `bugs-master.md`        |
| Email from your VP               | **Boss Ask** (VIP detected) | `boss-requests.md` (P0) |
| "We should probably look into X" | **Implicit Task**           | `TASK_MASTER.md`        |
| "Decided to go with Option B"    | **Decision**                | `DECISION_LOG.md`       |
| "Waiting on legal review"        | **Delegation**              | `DELEGATED_TASKS.md`    |
| Random FYI with no action        | **Reference**               | `0. Incoming/fyi/`      |

### Smart Context Recognition

The AI reads your `SETTINGS.md` to understand:

- **Who your boss is** → Escalates their requests automatically
- **What companies you manage** → Tags items with `[Company A]`, `[Company B]`
- **Your product keywords** → Associates items to the right product

---

---

## 📖 All Commands (Press `/` to See)

Type `/` in the chat to see available commands. The AI auto-detects intent, but you can trigger workflows directly.

### 🎯 The Diamond 6 (Core)

| Command   | What It Does                   | Example                      |
| :-------- | :----------------------------- | :--------------------------- |
| `/paste`  | Capture anything, auto-route   | Screenshot, email, Slack     |
| `/day`    | Today's priorities (Big Rocks) | "What's critical today?"     |
| `/week`   | Weekly tactical plan           | "Plan my week"               |
| `/plan`   | Strategy, OKRs, roadmaps       | "Draft Q2 roadmap"           |
| `/create` | Generate PRDs, specs, memos    | "Write a PRD for X"          |
| `/meet`   | Meeting prep & transcripts     | "Prep me for 1:1 with Sarah" |

### ⚡ Quick Actions

| Command  | What It Does                       |
| :------- | :--------------------------------- |
| `/setup` | Initialize your brain (first-time) |
| `/vibe`  | System health check                |
| `/pulse` | Context-aware nudges               |
| `/help`  | Full user manual                   |

### 🛠️ Power User

| Command   | What It Does                        |
| :-------- | :---------------------------------- |
| `/prep`   | 30-second cheat sheet for any topic |
| `/review` | Quality check PRDs or code          |
| `/draft`  | Create placeholder doc that evolves |
| `/sprint` | Generate dev sprint backlog         |
| `/data`   | Data analysis & SQL help            |
| `/launch` | GTM planning                        |

> 💡 **You don't need to memorize these.** Just describe what you want—the AI figures it out.

---

## ⚡ The Architecture

This kit uses the **Antigravity Modular Architecture**—the same pattern used in Google's internal AI tools.

### Three Layers

```
┌─────────────────────────────────────────────┐
│  📋 WORKFLOWS (16)                          │
│  Playbooks triggered by /commands           │
│  → /paste, /day, /create, /meet...          │
├─────────────────────────────────────────────┤
│  🧠 SKILLS (18)                             │
│  Modular AI expertise, loaded on-demand     │
│  → inbox-processor, prd-author, boss-tracker│
├─────────────────────────────────────────────┤
│  🤖 AGENTS (7)                              │
│  Virtual team personas with behaviors       │
│  → Staff PM, CPO, Strategist, Tech Lead...  │
└─────────────────────────────────────────────┘
```

### 18 Skills (AI Expertise)

| Skill                    | Purpose                       |
| :----------------------- | :---------------------------- |
| `inbox-processor`        | Aggressive task extraction    |
| `daily-synth`            | Daily brief with Big Rocks    |
| `task-manager`           | Priority & staleness tracking |
| `boss-tracker`           | VIP escalation & SLAs         |
| `meeting-synth`          | Transcript → Actions          |
| `prd-author`             | FAANG-standard PRDs           |
| `chief-strategy-officer` | Roadmaps & 7 Powers           |
| `context-retriever`      | History recall                |
| `stakeholder-mgr`        | Relationship health           |
| `bug-chaser`             | Bug lifecycle                 |
| `data-analytics`         | SQL & metrics                 |
| `ux-researcher`          | Personas                      |
| `product-marketer`       | Launch plans                  |
| `engineering-collab`     | Tech debt                     |
| `code-simplifier`        | Refactoring                   |
| `visual-processor`       | Image analysis                |
| `frontend-engineer`      | UI components                 |
| `core-utility`           | System diagnostics            |

### 7 Virtual Agents

| Agent              | Role                              |
| :----------------- | :-------------------------------- |
| **CPO**            | Portfolio strategy, multi-company |
| **Staff PM**       | Execution, Working Backwards      |
| **Strategist**     | MECE, SCQA, 7 Powers              |
| **Data Scientist** | Metrics, A/B tests                |
| **UX Researcher**  | Personas, interviews              |
| **Tech Lead**      | Feasibility, architecture         |
| **GTM Lead**       | Launch, marketing                 |

---

## 📁 Directory Structure

```
beats-pm-antigravity-brain/
├── 0. Incoming/           # Drop Zone (Screenshots, Notes)
├── 1. Company/            # Strategy & Profiles (LOCAL ONLY)
├── 2. Products/           # PRDs & Specs (LOCAL ONLY)
├── 3. Meetings/           # Transcripts (LOCAL ONLY)
├── 4. People/             # Stakeholders (LOCAL ONLY)
├── 5. Trackers/           # Task Ledgers (LOCAL ONLY)
│
├── .agent/                # ⭐ SOURCE OF TRUTH
│   ├── agents/            # Virtual Team Personas
│   ├── rules/GEMINI.md    # Core Rules File
│   ├── skills/            # 18 Modular Skills
│   ├── templates/         # FAANG Document Templates
│   └── workflows/         # 16 Playbooks
│
├── .gemini/               # Gemini CLI (symlinks to .agent/)
│   ├── GEMINI.md          → .agent/rules/GEMINI.md
│   └── settings.json      # Gemini CLI config
│
├── .claude/               # Claude Code (symlinks to .agent/)
│   ├── CLAUDE.md          → .agent/rules/GEMINI.md
│   └── commands/          → .agent/workflows/
│
├── .kilocode/             # Kilo Code (symlinks to .agent/)
│   ├── rules/             → .agent/rules/
│   ├── skills/            → .agent/skills/
│   └── workflows/         → .agent/workflows/
│
├── system/                # Python Scripts & Utils
├── SETTINGS.md            # Your Configuration
└── STATUS.md              # Current Dashboard
```

---

## 🤝 Contributing

Open source and community driven. Pull Requests welcome.

---

## 👨‍💻 About the Creator

<div align="center">

**Ernesto "Beats"**

_ex-BCG Digital Product Lead · ex-Fetch Rewards Senior Product Lead_

Building the future of AI-powered product management.

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/productmg/)
&nbsp;
[![X (Twitter)](https://img.shields.io/badge/X-Follow-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/officebeats)
&nbsp;
[![GitHub](https://img.shields.io/badge/GitHub-officebeats-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/officebeats)

</div>

---

<div align="center">

**Built by PMs, for PMs.**

_Stop chasing status updates. Start driving strategy._

<br/>

⭐ **Star this repo** if it saves you time.

</div>
