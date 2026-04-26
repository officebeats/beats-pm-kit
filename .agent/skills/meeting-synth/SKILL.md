---
name: meeting-synth
description: "Synthesize a single meeting transcript into structured action items, decisions, follow-ups, and stakeholder profiles. Use when processing a meeting recording, cleaning up transcript notes, or extracting commitments from a conversation."
priority: P0
maxTokens: 3000
triggers:
  - "/meet"
  - "/transcript"
version: 6.0.0 (Manager Meeting Mode)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Meeting Synthesizer Skill

> **Role**: Extract signal from noise. One meeting → structured output + stakeholder intelligence.

## 1. Native Interface

- **Inputs**: /meet, /transcript. Raw transcript text, Quill paste, or file path.
- **Tools**: run_command (cat), view_file.

---

## 2. Bounded Search Protocol

1. **User provides transcript directly** (paste or Quill format) → Process immediately.
2. **User says "process latest"** → Search ONLY 3. Meetings/transcripts/ MaxDepth: 1, limit to 1-3 files.

---

## 3. Cognitive Protocol (Double-Click Integration)

1. **Ingest**: Read the transcript.
2. **Classify Meeting Type**:
   - **Manager 1:1**: Attendees include direct manager (the user's direct manager) → Activate **§ 3A Manager Meeting Mode**.
   - **Peer/Stakeholder**: Standard processing.
   - **Customer/Partner**: Standard processing + competitive intel extraction.
3. **Extract** (single-pass):
   - **Decisions**: Formalized agreements.
   - **Action Items**: Task + ID (if existing) + Owner + Due.
   - **Key Quotes**: Verbatim statements with attribution.
4. **Route & Update** (Parallel Cloud-Safe Writes):
   - **New Action items** → 5. Trackers/TASK_MASTER.md + Create 5. Trackers/tasks/{ID}.md.
   - **Existing Task Updates**: If a TASK_ID (e.g. P1-001) is mentioned, update its detail file's "Progress Log" and "Stakeholder Quotes".
   - **Stakeholder Enrichment**: Update 4. People/{firstname-lastname}.md "Interaction Stream" with quotes and the "Active Tasks" or "Awaiting" sections.
5. **Summary**: Write to 3. Meetings/summaries/ using assets/meeting_template.md. **MANDATORY**: Append the full raw transcript at the end of the file under a `# 📝 Full Transcript` section.

---

## 3A. Manager Meeting Mode

**Trigger**: Meeting includes the user's direct manager.

In ADDITION to standard extraction (§ 3), extract and route the following:

### Operating Agreements
- New rules, protocols, or standing instructions the manager establishes
- Changes to existing operating agreements
- **Route to**: `1. Company/ways-of-working.md` — append under the relevant section

### Scope Changes
- Any new "IN SCOPE" or "OUT OF SCOPE" items
- Changes to what the user should or shouldn't work on
- New task assignments vs. tasks to deprioritize
- **Route to**: `1. Company/ways-of-working.md` and `5. Trackers/TASK_MASTER.md`

### Stakeholder Dynamics
- How the manager describes other people's working styles, political positions, reliability, or goals
- Relationship advice ("route through me", "don't escalate directly", "she's approachable")
- Org chart or reporting line clarifications
- **Route to**: Relevant `4. People/{person}.md` profile under "Working Preferences" or "Context"

### Communication Preferences
- New patterns in how the manager prefers to communicate
- Things that frustrated or pleased her
- Anti-patterns she warned about
- **Route to**: `1. Company/ways-of-working.md` under "Communication Profile"

### Process Intelligence
- How things actually work at the company vs. how they're supposed to work
- Workarounds, bottlenecks, dysfunction she identifies
- PI Planning, release management, engineering process context
- **Route to**: `1. Company/ways-of-working.md` or relevant `2. Products/` files

### Strategic Context
- Product roadmap shifts, market intelligence, competitive positioning
- Partner relationship updates
- Leadership changes or upcoming org shifts
- **Route to**: Relevant `2. Products/` files or meeting summary

---

## 4. Output Format

Confirm all updates:
- Summary File created.
- Task Details updated (list IDs).
- Stakeholder Profiles updated (list Names).
- **Manager Mode** (if triggered):
  - Ways of Working sections updated (list which sections).
  - Scope changes applied (list additions/removals).
  - Stakeholder dynamics added (list people enriched with the manager context).

---

## 5. Privacy & Efficiency

- PII may be stored locally since `4. People/` is gitignored.
- Single-pass extraction.
- Skip logistics chatter.
- For external-facing outputs: No emojis unless explicitly requested.

---

## 6. Daily Synthesis Mode (`/day`, `/morning`)
**Trigger**: User requests a daily brief or status check.
1. **Hydrate**: Read `STATUS.md`, `5. Trackers/TASK_MASTER.md`, `5. Trackers/critical/boss-requests.md`, `5. Trackers/bugs/bugs-master.md`.
2. **Phase Logic**:
   - **Morning (<12:00)**: Define **"Big Rocks"** (Top 3 Absolutes).
   - **Midday**: Pivot check.
   - **EOD (>16:00)**: Audit shipped items. Update `STATUS.md`.
3. **Routing**: If Boss Ask Red → Suggest `/boss`.

---

## 7. Weekly/Monthly Synthesis Mode (`/week`, `/month`)
**Trigger**: User requests a weekly or monthly rollup.
1. **Scan Trackers**: Read `TASK_MASTER.md` (Completed this week/month) and `bugs-master.md` (New Criticals).
2. **Check Pulse**: Read `5. Trackers/critical/boss-requests.md` (Status of P0s).
3. **Synthesis**:
   - **Wins**: Shipped features, resolved P0 bugs, key decisions.
   - **Risks**: Overdue items, blocked dependencies, team burnout signals.
   - **Metric**: Calibrate a "Confidence Score" (1-10) for the sprint/month.
4. **Visuals**: Use ASCII Charts for trends and Emoji Signals (`🟢`, `🟡`, `🔴`) for Health. No fluff—outcome-oriented bullet points only.
