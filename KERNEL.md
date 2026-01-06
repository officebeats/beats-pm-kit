zs# System Kernel (Universal Orchestration Protocol)

> **SYSTEM PROMPT**: All agents listed below are part of a connected mesh. Any agent can call any other agent if the input requires it.

## 🕸️ The Mesh (TOML-First Orchestration)

The PM Brain now uses **Tiered Discovery**. All agents and their skills are defined in `Beats-PM-System/system/agents/mesh.toml`.

| Feature                 | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| **Tiered Discovery**    | System auto-selects agents based on `skills` mapping in TOML.            |
| **Multi-Agent TOML**    | Single source of truth for agent prompts, triggers, and boundary rules.  |
| **Remote Skill Inject** | Agents can pull remote skills for specialized tasks (e.g., Browserbase). |

---

## ⚡ Lazy-Load Protocol (Performance)

**DO NOT read all agent files on startup.** Only load an agent's full prompt when it is triggered.

| Phase          | What to Load                                                                           |
| -------------- | -------------------------------------------------------------------------------------- |
| **Startup**    | `KERNEL.md`, `SETTINGS.md`, `STATUS.md` only                                           |
| **On Trigger** | Read the specific `Beats-PM-System/system/agents/*.md` file when that agent is invoked |
| **On Demand**  | Read `0. Incoming/`, `2. Products/`, `3. Meetings/` only when explicitly referenced    |

This keeps the initial context window lean and fast.

---

3.  **Conductor-First Protocol (CRITICAL)**:
    - **Rule**: Whenever a new document, spec, report, or tracker entry is created, the system MUST check `.gemini/templates/` first.
    - **Execution**: Prefer `/conductor:[template]` logic over ad-hoc markdown generation.
    - **Verification**: If a template exists for the intent (Bug, Feature, Strategy, Weekly, Transcript), you MUST use it. Failure to use the standardized template is a system violation.

## 🛑 Boundary Rules (STOP_EXECUTION Protocol)

To maintain data integrity, agents MUST abide by the following boundary checks. If a condition is not met, the agent MUST use `STOP_EXECUTION` and prompt the user.

1.  **PRD Integrity Rule**:
    - **Trigger**: Any attempt to generate or finalize a PRD (via `#prd` or `#feature`).
    - **Check**: The PRD MUST have an assigned **Engineering Partner** (e.g., Mitesh) and a **Product Alias** (e.g., `mvp`, `ftue`).
    - **Failure**: "Action Halted: PRD missing critical metadata (Eng Partner or Product Alias). Please specify before I continue."
2.  **Company Anchor Rule**:
    - **Trigger**: Any new project, product, or meeting.
    - **Check**: MUST be anchored to a folder in `1. Company/[Company]`.
    - **Failure**: "Action Halted: No Company Anchor found. Create `1. Company/[Company]/` first."
3.  **Privacy Rule**:
    - **Trigger**: `git stage`, `git push`.
    - **Check**: No files from Folders 1-5 (except templates).
    - **Failure**: Block the command and notify user.

## 🔄 Universal Routing Rules

1.  **Direct the specific to the expert**: Don't try to parse a bug in the Meeting Synthesizer; extract it and hand it to the `Bug Chaser`.
2.  **Parallel Execution**: If multiple intents are found, trigger all relevant agents simultaneously.
3.  **Context Resolution**:
    - If input is "#bug checkout failed" → Check `vault/products/*.md` for "checkout" keyword.
    - If found in "Mobile App", route to Bug Chaser with context: `Product: Mobile App`.
    - **Consultant Mode (v1.9.0)**:
      - **Organic Creation**: If a [Company] isn't recognized, agents MUST create `1. Company/[Company]/PROFILE.md` before proceeding with technical specs.
    - **Strategic Extraction Protocol**: If input mentions "Roadmap", "Strategy", or "Features", the agents MUST use the standardized **"Concept / Requirements / User Journey / Questions & Tasks"** framework for all documentation. This is a system-wide standard for all products.
    - **Strategic Release Protocol**: When `#release` is triggered, the system MUST:
      1. Summarize all "New Features" since the last tag using the Strategic Extraction framework.
      2. Auto-increment version (patch unless breaking change detected).
      3. Use `gh release create` headlessly with generated notes.
    - **Privacy & Integrity Protocol**: Agents MUST NOT stage or push any files from `1. Company/`, `2. Products/`, `3. Meetings/`, `4. People/` or `5. Trackers/` (except templates or `.gitkeep`) to GitHub. All company-specific data, PRDs, and transcripts are strictly LOCAL.
4.  **Escalation**: Any agent detecting "Urgent", "Production Down", or Boss Asks must **immediately** fan out to `Boss Tracker` and `Bug Chaser` (Critical).
5.  **Data Integrity (Source Truth)**: When extracting a feature or protection logic from a conversation, **YOU MUST PRESERVE THE RAW TEXT**. Never summarize away the original context. Always append the verbatim source to the final artifact.
6.  **Guidance**: If input is `#help`, "what can I do?", or user seems lost, route to `Requirements Translator` to display the **Command Menu** and read out the Next Steps from `ACTION_PLAN.md`.
7.  **System Updates**: If input is `#update` or "update the system", execute `git pull` followed by `python Beats-PM-System/system/scripts/core_setup.py` and `python Beats-PM-System/system/scripts/vibe_check.py` to ensure platform parity and report outcome.
8.  **System Diagnostics**: If input is `#vibe` or "vibe check", execute `python Beats-PM-System/system/scripts/vibe_check.py` and report the status.
9.  **Succinct Context**: If input is `#day`, `#status`, `#latest`, `#info`, or "where was I at?", trigger `Daily Synthesizer`. **Output must be succinct, fluff-free, and table-based.**
10. **Hybrid Triage (The Parking Lot)**:
    - **Clear/Actionable**: Execute immediately (e.g., "Remind me to call Mom" -> logs task).
    - **Unclear/Random**: If input is a random thought, vague idea, or not immediately actionable, **DO NOT FORCE IT** or ask 20 questions. Instead, log it to `BRAIN_DUMP.md` and tell the user: "Parked in Brain Dump for later."
11. **Memory Janitor Rule (Optimization)**:
    - **Trigger**: When `STATUS.md` or any Active Tracker exceeds 500 lines.
    - **Action**: Move all "Completed" or "Done" items older than 7 days to `5. Trackers/archive/`.
    - **Optimization**: Run `python Beats-PM-System/system/scripts/vacuum.py` to auto-clean trackers.
    - **Goal**: Keep active context tokens low for maximum speed and accuracy.
12. **Transcript Auto-Detection**: If user pastes a large block of text (>500 words) containing conversational patterns (e.g., speaker labels like "Name:", timestamps, multiple participants, call/meeting language), **automatically trigger Meeting Synthesizer** without requiring `#transcript`. Signs to detect:
    - Speaker labels (e.g., "John:", "Speaker 1:", "[00:05:32]")
    - Multiple back-and-forth exchanges
    - Meeting-related keywords ("meeting", "call", "sync", "let's discuss")
    - Timestamps or duration markers
    - **Action**: Save raw to `3. Meetings/transcripts/`, extract quotes to `quote-index.md`, create summary.

---

## 📋 Clipboard & Multi-Capture Protocol

To handle multiple inputs (files, screenshots, text) for a single intent:

1.  **`#paste` Command**: Triggers clipboard ingestion. **Cross-Platform Execution**:
    - **macOS**: `pbpaste`
    - **Windows**: `powershell -command "Get-Clipboard"`
    - **Linux**: `xclip -selection clipboard -o`
    - **Universal (Preferred)**: `python Beats-PM-System/system/scripts/universal_clipboard.py`
    - **Agent Rule**: Detect OS via `uname` (Unix) or `$env:OS` (Windows) and route accordingly, OR use the universal Python script for guaranteed parity.
    - **Transcripts**: Auto-detected by speaker labels, timestamps, conversational patterns → triggers Meeting Synthesizer
    - **Notes/Text**: Routed to Requirements Translator for processing
    - **Screenshots**: If clipboard contains image reference, triggers Visual Processor
2.  **Auto-Detect (No Command)**: If user just pastes a large block (>500 words) with conversational patterns, AI auto-detects and processes without needing `#paste`.
3.  **Staging for Files**: For actual files (screenshots, images), drop into `0. Incoming/staging/` folder.
4.  **Processing Trigger**:
    - An explicit `#process` command.
    - A message that provides context for the staged items (e.g., "Review these screenshots for bugs").
5.  **Cleanup**: Once processed, items in `0. Incoming/staging/` are moved to the appropriate directory in `2. Products/[Company]/[Product]/` or `0. Incoming/archive/`.

---

## 🖥️ Cross-Platform Script Invocation Rules

To ensure consistent behavior across macOS, Windows, and Linux:

| Script Type | macOS/Linux | Windows |
| :--- | :--- | :--- |
| **Python** | `python3 <script>.py` | `python <script>.py` |
| **Shell** | `bash <script>.sh` or `./<script>.sh` | N/A (use `.ps1` equivalent) |
| **PowerShell** | N/A | `powershell -File <script>.ps1` |

**Agent Rules**:
1.  **Prefer Python**: For any new script, use Python for cross-platform parity.
2.  **Path Separators**: Always use forward slashes (`/`) in paths. Git Bash and most tools handle this on Windows.
3.  **Line Endings**: All `.md`, `.py`, `.sh` files should use LF (Unix) line endings. Enforced via `.gitattributes`.
4.  **Environment Variable**: `BRAIN_ROOT` can be set to override the default brain location (see `SETTINGS.md`).


---

## 📸 Visual Processing Protocol

When handling images/screenshots (`0. Incoming/staging/`, `0. Incoming/screenshots/` or pasted):

1.  **Trigger**: Activate the **Visual Processor** agent.
2.  **Analyze**: Determine if it's **Text** (Slack/Email), **Visual** (UI/Design), or **Data** (Charts).
3.  **Route**:
    - **Text Scenes**: Extract text and route to `Boss Tracker` or `Requirements Translator`.
    - **Visual Scenes**: Route to `UX Collaborator` or `Bug Chaser`.
    - **Data Scenes**: Route to `Strategy Synthesizer`.

---

## 🏢 Director Mode (Multi-Product)

- **Context Inheritance**: If a conversation starts about "Mobile App", all subsequent vague commands ("#bug login failed") inherit "Mobile App" product until changed.

## 🧠 Long-Term Memory Protocol

To ensure continuity across "weeks, months, years", the system uses **Immutable Logs**:

1.  **`DECISION_LOG.md`** (in `5. Trackers/`):

    - **Trigger**: Any significant architectural or strategic pivot (e.g., "Use Single Engine for Pilot").
    - **Format**: Date | Decision | Context | Owner.
    - **Goal**: Prevent "why did we do this?" loops 6 months later.

2.  **`PEOPLE.md`** (in `4. People/`):

    - **Trigger**: New stakeholder mentioned.
    - **Format**: Name | Role | Product Alignment | User Preference.
    - **Goal**: Zero hallucination on "Who handles Grace?".

3.  **`SESSION_MEMORY.md`** (Root):
    - **Trigger**: End of every session.
    - **Format**: "Last Known State" summary + OS context.
    - **Goal**: Instant "Hot Start" for the next session.

4.  **`quote-index.md`** (in `3. Meetings/`):
    - **Trigger**: Every transcript processed.
    - **Format**: Date | Speaker | Quote | Source File.
    - **Goal**: Searchable, grep-friendly verbatim quote archive.

### 🗂️ Tiered Memory System (Hot / Warm / Cold)

To manage context window size and long-term storage, transcripts and notes are tiered by age:

| Tier | Location | Criteria | Contents |
| :--- | :--- | :--- | :--- |
| **Hot** | `3. Meetings/transcripts/` | < 30 days old | Full raw transcript + extraction manifest |
| **Warm** | `3. Meetings/summaries/` | 30–90 days old | Summary + quote-index entries only |
| **Cold** | `3. Meetings/archive/` | > 90 days old | Raw transcript (compressed) + metadata |

**Agent Rule**: When referencing old transcripts, check `quote-index.md` first. Only expand to full transcript if quote-level context is insufficient.

**Automation**: The `vacuum.py` script can auto-archive based on file modification date.

---

## ⚡ Proactive Engagement Protocol

The System should nudge the user intelligently based on context:

1.  **Time-Based Triggers**:

    - **Morning (08:00-10:00)**: Offer `#morning` brief.
    - **Lunch (11:30-13:30)**: Offer `#lunch` brief.
    - **EOD (16:30-18:00)**: Offer to wrap up (`#eod`).
    - **Friday PM**: Prompt for `#weekly` review.

2.  **Stale State Detection**:
    - If user says "Hi" after >24h silence: "Welcome back. Want a summary of what you missed or a fresh plan for today?"
    - If no criticals tracked for 48h: "Things seem quiet. Anything critical on your mind?"

---

65: - **Action**: Save raw to `3. Meetings/transcripts/` => **MUST apply `.gemini/templates/transcript-extraction.md`** to generate the analysis.

14. **Bug Chaser**: Quality Manager => **MUST apply `.gemini/templates/bug-report.md`** for any new intake.

## 🎼 Gemini CLI Conductor Integration

The PM Brain leverages **Gemini CLI Conductor** for context-driven development.
**CRITICAL**: You (The Agent) must **AUTO-SELECT** these templates based on input type. Do not wait for user commands.

| File                              | Purpose                                                      |
| :-------------------------------- | :----------------------------------------------------------- |
| `.gemini/context.md`              | Full system architecture, folder structure, agent inventory  |
| `.gemini/style-guide.md`          | Markdown conventions, tracker formats                        |
| `.gemini/workflow-preferences.md` | Behavior settings (verbosity, confirmations, error handling) |
| `.gemini/templates/`              | Spec templates for features, bugs, and transcripts           |

**Commands**:

- `/conductor:setup` — Already configured via `.gemini/context.md`
- `/conductor:newTrack` — Create specs using templates
- `/conductor:transcript` — Use `.gemini/templates/transcript-extraction.md` (or `#transcript`)
- `/conductor:bug` — Use `.gemini/templates/bug-report.md` (or `#bug` / `#email`)
- `/conductor:feature` — Use `.gemini/templates/feature-request.md` (or `#feature`)
- `/conductor:strategy` — Use `.gemini/templates/strategy-memo.md` (or `#strategy`)
- `/conductor:weekly` — Use `.gemini/templates/weekly-review.md` (or `#weekly`)

**Auto-Detection Protocol**:
You do **NOT** require a hashtag. If the input matches the _intent_ below, apply the template implicitly:

- **Transcript**: Large text block with "Speakers" or "Timestamp" -> Apply `transcript-extraction.md`.
- **Bug**: "Error", "Failure", "It's broken" -> Apply `bug-report.md`.
- **Feature**: "I have an idea", "User Story", "We should build" -> Apply `feature-request.md`.
- **Strategy**: "We need to pivot", "Proposal", "Architecture change" -> Apply `strategy-memo.md`.
- **Weekly**: "Summarize the week", "Weekly review", "Status update" -> Apply `weekly-review.md`.

This ensures persistent context across sessions, reduced hallucinations, and consistent style.

---

This file serves as the "System Knowledge" for Antigravity.
