---
description: Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /boss - Boss 1:1 Preparation Protocol

**Trigger**: User types `/boss`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday @ 10:05 AM**. This workflow prepares you for that meeting by synthesizing progress, identifying blockers, and drafting a pre-brief DM.

## 1. Context Acquisition (Parallel)

In a **single turn**, read:
1. `5. Trackers/TASK_MASTER.md` → Get full current sprint view.
2. `1. Company/ways-of-working.md` → Review standing agreements and operating rules.
3. The boss's people profile (e.g., `4. People/{boss-name}.md`) → Check committed tasks ("Awaiting") and interaction patterns.
4. **Last 2 boss meeting summaries**: Search `3. Meetings/summaries/` for files containing the boss's name. Select the 2 most recent.
5. **Calendar**: Prefer `/beats-comms calendar: next 7 days` with read-only MS365 MCP/connector access to pull upcoming meetings. Use `python3 system/scripts/outlook_bridge.py --calendar 7` only as a less-portable macOS AppleScript fallback and label that limitation in the prep notes.

## 2. Progress Analysis

For the period since last 1:1:
1. **Outcomes for Manager**: Date-bound commitments and readiness checks, written as action items.
2. **Completed outcomes**: What got checked off, when, and from what evidence source.
3. **What's in progress**: Active tasks with status updates.
4. **People connected with**: New stakeholder interactions from meeting summaries and people profiles.
5. **What's been learned**: Self-study, product insights, strategic context gathered.
6. **Blockers**: Anything stuck, awaiting someone, or missing information.

When the boss is Manager, "outcomes" means:
- A short list of dated readiness commitments, not a narrative recap.
- A short **Completed outcomes** section with completion date and source evidence.
- A follow-on **Readiness checks** list with named owners and concrete actions.
- Scope caveats inline, e.g. "UX may not be perfect" or "pending CTT confirmation."
- Triangulate against `5. Trackers/WORKSTREAMS.md`, task details, recent chat transcripts, and meeting transcripts before finalizing.

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
- **PART 0: Outcomes** — Dated commitments and readiness checks in Manager's preferred action-item style
- **PART 0B: Completed Outcomes** — Checked-off outcomes with completion date and evidence source
- **PART 1: Progress Report** — Who I connected with, what I learned, deliverables in progress
- **PART 2: Blockers & FYIs** — What's stuck, what the boss needs to know
- **PART 3: Questions** — 3-4 targeted questions with context and "Listen for" hints
- **PART 4: Talking Points** — Optional strategic topics if conversation opens up

### B. Teams DM Draft (External Send)

Generate a copy-paste-ready Teams DM that:
- Uses **no emojis** because they can make the message look AI-generated
- Is succinct — short headings and bullets, no prose
- Starts with **Outcomes** in the action-item format Manager expects
- Covers: Outcomes, Completed outcomes, Readiness checks, Blockers/FYIs, Questions for today
- Tone: Professional but personable, shows initiative without overdoing it

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
[Date]: [Workstream/deliverable] will be ready - [scope/caveat if needed]
[Date]: [Decision/checkpoint] will be confirmed

Completed outcomes
[Date completed]: [Completed item] - [source/evidence]

Readiness checks
- [Owner] will [specific action] by [date]
- [Owner] will [specific action] by [date]

Blockers/FYIs
- [Issue] - [what I am doing about it]

Questions for Today
1. [Direct, specific question]
2. [Direct, specific question]
3. [Direct, specific question]

Looking forward to it!
```
