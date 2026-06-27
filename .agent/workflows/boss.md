---
description: Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /boss - Boss 1:1 Preparation Protocol

**Trigger**: User types `/boss`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday @ 10:05 AM**. This workflow prepares you for that meeting by synthesizing progress, identifying blockers, and drafting a pre-brief DM.

## 1. Context Acquisition (Parallel)

In a **single turn**, read:
1. `5. Trackers/WORKSTREAMS.md` and relevant `5. Trackers/workstreams/` files → Get the human-facing workstream list.
2. `5. Trackers/TASK_MASTER.md` → Get internal task refs and detailed execution state.
3. `5. Trackers/critical/boss-requests.md` → Get leadership commitments and unresolved asks.
4. `1. Company/ways-of-working.md` → Review standing agreements and operating rules.
5. The boss's people profile (e.g., `4. People/{boss-name}.md`) → Check committed tasks ("Awaiting") and interaction patterns.
6. **Last 2 boss meeting summaries**: Search `3. Meetings/summaries/` for files containing the boss's name. Select the 2 most recent.
7. **Calendar**: Prefer `/beats-comms calendar: next 7 days` with read-only MS365 MCP/connector access to pull upcoming meetings. Use `python3 system/scripts/outlook_bridge.py --calendar 7` only as a less-portable macOS AppleScript fallback and label that limitation in the prep notes.

## 2. Progress Analysis

For the period since last 1:1:
1. **Outcomes**: Succinct action-item style commitments or expected results, grouped by workstream.
2. **Completed outcomes**: Tasks, decisions, checklist items, or commitments completed since last Friday, with completion date/source.
3. **Readiness checks**: Short checklist of upcoming validation, prep, or follow-up actions.
4. **What's in progress**: Active workstreams with status updates.
5. **People connected with**: New stakeholder interactions from meeting summaries and people profiles.
6. **What's been learned**: Self-study, product insights, strategic context gathered.
7. **Blockers**: Anything stuck, awaiting someone, or missing information.

Paru outcome format:

```markdown
Outcomes:

[Date/Gate]: [succinct expected result]
[Date/Gate]: [succinct expected result]

Readiness checks:
- [Owner] will [action]
- [Owner] please [action]
- [Owner] will [action]
```

Use that concise action-item style, but group the underlying evidence and next actions under the relevant workstream.

## 3. Boss's Commitments Check

Review the boss's people profile Active Tasks section:
- Items the boss committed to deliver (Confluence links, Slack access, introductions, etc.)
- Flag any that are overdue or still pending — these are good follow-up items.

## 4. Stale Workstream Detection

**Definition**: A workstream is "stale" if:
- The `Status` has not changed in >3 days OR
- It has no recent transcript/report mentions.

**Action**: Flag stale items with `🔴 STALE` warning.

## 5. Question Generation

Based on the analysis above, generate 3-4 targeted questions that:
- Reference specific context (not generic)
- Address current blockers or decision points
- Leverage the boss's direct candor (ask for opinions, not just information)
- Include "Listen for" hints — what signals to pick up from her answer

Reference `1. Company/ways-of-working.md` → "How to DM Her" section for framing style.

## 6. Output — Two Deliverables

### A. Cheat Sheet (Internal Reference)

Save to `3. Meetings/summaries/YYYY-MM-DD_Boss_Prep.md`:

Structure:
- **PART 0: Outcomes** — Succinct action-item style outcomes grouped by workstream and date/gate
- **PART 0B: Completed Outcomes** — Completed work and checked-off items with completion date/source
- **PART 1: Workstream Status** — Latest outcome, completed items, open items, and recommended next 3
- **PART 2: Blockers & FYIs** — What's stuck, what the boss needs to know
- **PART 3: Questions** — 3-4 targeted questions with context and "Listen for" hints
- **PART 4: Talking Points** — Optional strategic topics if conversation opens up

### B. Teams DM Draft (External Send)

Generate a copy-paste-ready Teams DM that:
- Uses **no emojis** (looks AI-generated)
- Is succinct — bullets only, no prose
- Covers: Outcomes, Completed outcomes, Readiness checks, Blockers/FYIs, and Questions for today
- Tone: Professional but personable, shows initiative without overdoing it
- Uses workstream titles of 9 words or fewer and does not expose internal task/card/source IDs

Present the DM to the user for review before they send it.

## 7. Post-Meeting Hook

After the 1:1 concludes:
- Remind user to run `/meet` or `/transcript` to process the boss transcript.
- When processed, meeting-synth will auto-trigger **Manager Meeting Mode** (§ 3A) to update Ways of Working, scope, and stakeholder dynamics.

---

## Example DM Output

```
Hi [Boss Name] — ahead of our sync, quick recap:

Outcomes
- [Date/Gate]: [succinct expected result]
- [Date/Gate]: [succinct expected result]

Completed outcomes
- [Completed result]
  - Completed: [date/source]

Readiness checks
- [Owner] will [action]
- [Owner] please [action]
- [Owner] will [action]

Workstreams
- [Workstream title]
  - Latest outcome: [current state]
  - Open items: [owner/action/date]

Questions for Today
1. [Direct, specific question]
2. [Direct, specific question]
3. [Direct, specific question]

Looking forward to it!
```
