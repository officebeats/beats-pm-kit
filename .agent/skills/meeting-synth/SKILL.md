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

- **Inputs**: /meet, /transcript. Synthesis packet JSON, raw transcript text, Quill paste, or file path.
- **Tools**: run_command (cat), view_file.

---

## 2. Bounded Search Protocol

1. **Pipeline packet provided** (`3. Meetings/reports/packets/*.json`) → Process that packet and its referenced transcript.
2. **User provides transcript directly** (paste or Quill format) → Process immediately.
3. **User says "process latest"** → Run `/transcript` preparation first; use generated packets instead of broad transcript scans.

---

## 2A. Slack Task Evidence Guardrail

When `/transcript` provides Slack messages as scoped context, treat Slack content as read-only evidence for local task extraction only.

- Extract candidate action items, decisions, blockers, owners, due dates, and source references.
- Never send, schedule, draft, reply, react, edit, delete, pin, bookmark, create canvases/files, or mutate Slack state.
- Preserve unread state. Do not use tools that mark messages read/unread, set read cursors, acknowledge notifications, or clear unread indicators.
- Do not quote full Slack conversations into summaries. Use short evidence snippets and source channel/thread/timestamp references.
- Route accepted tasks only to local repo files such as `5. Trackers/TASK_MASTER.md` and task detail files; list uncertain Slack items for manual user handling.

---

## 3. Cognitive Protocol (Double-Click Integration)

1. **Ingest**: Prefer a pipeline packet. Read the transcript path referenced by the packet and preserve packet metadata (`run_id`, `content_sha256`, `expected_summary_path`).
2. **Classify Meeting Type**:
   - **Manager 1:1**: Attendees include direct manager (the user's direct manager) → Activate **§ 3A Manager Meeting Mode**.
   - **Peer/Stakeholder**: Standard processing.
   - **Customer/Partner**: Standard processing + competitive intel extraction.
   - **Packet Override**: If the packet marks `manager_mode_required` or `partner_customer_mode_required`, treat that as required unless the transcript clearly proves otherwise.
3. **Extract** (single-pass):
   - **Decisions**: Formalized agreements.
   - **Action Items**: Task + ID (if existing) + Owner + Due.
   - **Key Quotes**: Verbatim statements with attribution.
4. **Route & Update** (Parallel Cloud-Safe Writes):
   - **New Action items** → 5. Trackers/TASK_MASTER.md + Create 5. Trackers/tasks/{ID}.md.
   - **Existing Task Updates**: If a TASK_ID (e.g. P1-001) is mentioned, update its detail file's "Progress Log" and "Stakeholder Quotes".
   - **Stakeholder Enrichment**: Update 4. People/{firstname-lastname}.md "Interaction Stream" with quotes and the "Active Tasks" or "Awaiting" sections.
5. **Summary**: Write to the packet's `expected_summary_path` when provided, otherwise use `3. Meetings/summaries/` and assets/meeting_template.md.
6. **Hybrid Appendix (MANDATORY for `/transcript`)**: Include `Source Transcript`, `Transcript SHA256`, `Pipeline Run ID`, `Key Evidence`, and `Routed Updates`. Do **not** append the full raw transcript by default. The full raw transcript remains in `3. Meetings/transcripts/`.

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
- Source Transcript / hash / run ID included when a packet was used.
- Task Details updated (list IDs).
- Stakeholder Profiles updated (list Names).
- Routed Updates section lists exact files changed or says `No durable update required`.
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
