---
description: Prepare for your 1:1 with your boss. Tracks all Boss Asks, pulls recent transcripts, and generates a prep doc.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /boss - Boss 1:1 Preparation Protocol

**Trigger**: User types `/boss`.

> **🗓️ Key Checkpoint**: Boss 1:1 is **every Friday around lunch**. This workflow prepares you for that meeting by synthesizing all open commitments and recent context.

## 1. Context Acquisition (Parallel)

In a **single turn**, read:
1.  `5. Trackers/TASK_MASTER.md` → Filter for `Reason = Boss Ask`.
2.  `5. Trackers/critical/boss-requests.md` → Get the canonical list of active Boss Asks.
3.  **Last 2 Boss Meeting Transcripts**: Search `3. Meetings/transcripts/` for files containing your boss's name in the filename. Select the 2 most recent.
4.  **Last 2 Boss Meeting Reports**: Search `3. Meetings/reports/` for files containing your boss's name in the filename. Select the 2 most recent.

## 2. Transcript Analysis

For each of the last 2 boss transcripts/reports:
1.  **Extract Open Items**: Identify any action items your boss assigned that are NOT marked complete.
2.  **Extract Themes**: Note any recurring topics or concerns your boss mentioned.
3.  **Extract "Closing the Loop" Items**: Identify things your boss asked you to follow up on.

## 3. Stale Workstream Detection (CRITICAL)

**Definition**: A workstream is "stale" if:
- It has a `Boss Ask` reason AND
- The `Status` has not changed in >3 days OR
- It has no recent transcript/report mentions.

**Action**: Flag stale items in the output with a `🔴 STALE` warning and recommend:
> "Get progress on this FIRST THING Friday morning before your 1:1."

## 4. Synthesis & Output

Generate a structured 1:1 Prep Document:

``> **Output Formatting**: Read the template at .agent/skills/boss-tracker/assets/boss_prep_template.md and use it to format your output.``

## 5. Output Location

Save the generated prep doc to:
`5. Trackers/critical/boss-prep-[date].md`

---

## Example Stale Detection Logic

| Workstream | Last Mentioned | Days Stale | Flag |
|------------|----------------|------------|------|
| **Steering Agent Deck** | 2026-01-27 | 2 | ✅ OK |
| **KU Residents Fix** | 2026-01-25 | 4 | 🔴 STALE |
| **Athena Logic** | 2026-01-29 | 0 | ✅ OK |

For 🔴 STALE items, the output should say:
> "🔴 **KU Residents Fix** has no updates since Jan 25. Get status from the owner FIRST THING Friday morning."
