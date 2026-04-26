---
description: Process all Quill meetings from the last 10 business days.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



1. **Antigravity Native Intake (Primary)**:
   - Use Antigravity capture for transcripts directly into `0. Incoming/`.

1b. **Outlook Context Sync (New)**:
   - Run the `outlook-navigator` skill to fetch recent inbox context (subjects, snippet).
   - // turbo
   - `python3 system/scripts/outlook_bridge.py --count 10`


1c. **Outlook Calendar Sync**:
   - Run the updated bridge to fetch upcoming calendar meetings.
   - // turbo
   - `python3 system/scripts/outlook_bridge.py --calendar 14`
   - **Action**: Check `5. Trackers/TASK_MASTER.md` for any tasks requiring a meeting to be scheduled. If that meeting exists in the calendar output, update the task status to `🗓️ Scheduled for [Date]` instead of completing it.

1d. **Teams Context Sync (New)**:
   - Run the Teams bridge to fetch recent chat context.
   - // turbo
   - `python3 system/scripts/beats.py teams --args "--json"`
   - **Action**: Analyze for task updates (especially **BOSS-001**) and new tasks.

2. **CLI Fallback (Secondary)**:
   - Run the targeted transcript fetcher.
   - // turbo
   - `python3 system/scripts/quill_mcp_client.py || python3 system/scripts/transcript_fetcher.py`
   - **Normalization step (MANDATORY)**: After import, run `python3 system/scripts/transcript_intake.py` to move any date-stamped raw meeting files from `0. Incoming/` into `3. Meetings/transcripts/`.

3. **Parallel Identification**:
   - Scan `3. Meetings/transcripts/` for new transcript files.
   - Group them for batch processing.

4. **Parallel Synthesis (Fan-Out)**:
   - **Action**: For ALL new transcripts, execute the `meeting-synth` skill in a SINGLE parallel turn.
   - **Output**: Generate summary reports in `3. Meetings/summaries/`.

5. **Stakeholder Enrichment (Post-Synthesis)**:
   - For each person mentioned in transcripts or emails:
     - Check if a profile exists in `4. People/{firstname-lastname}.md`.
     - If **exists** → Append new context (role updates, quotes, decisions, preferences).
     - If **new** → Create a profile using the standard template (see meeting-synth skill for format).
   - Extract role/title from email signatures, meeting intros, or context clues.
   - PII may be stored locally since `4. People/` is gitignored. Extract full contact info from email signatures (work email, cell, office, pronouns).

6. **Manager Meeting Auto-Enrichment**:
   - **Trigger**: If ANY transcript involves **the user's direct manager** (direct manager).
   - **Action**: Activate meeting-synth **Manager Meeting Mode (§ 3A)**:
     - Update `1. Company/ways-of-working.md` with new operating agreements, scope changes, process updates, and communication preferences.
     - Update `4. People/the manager's profile` with new quotes, commitments, and interaction patterns.
     - Extract stakeholder dynamics the manager shared about others → update relevant `4. People/` profiles.
     - Extract any scope changes → update `5. Trackers/TASK_MASTER.md` (add new tasks, deprioritize removed ones).

7. **Post-Meeting TASK_MASTER Sync**:
   - After ALL meetings are synthesized, reconcile `5. Trackers/TASK_MASTER.md`:
     - **New action items** from meetings → Add to active sprint with appropriate priority.
     - **Completed/resolved items** mentioned in meetings → Mark as ✅.
     - **Scope changes** → Move tasks to ON HOLD or OUT OF SCOPE as directed.
     - **Calendar reconciliation**: Cross-check upcoming meetings against tasks with "🗓️ Scheduled" status.
   - Run the **Priority Gate** (task-manager § 2) on any new tasks from non-manager sources.

8. **Recent Meetings Summary (Quill Output)**:
   - Extract the last 5 processed meetings.
   - For each meeting, generate a 3-point bullet summary and a list of Action Items (Owner + Task).
   - Present the meetings in a compact bullet list format:
     - 🟦 **[Title]**
       - **Date**: [Formatted Date]
       - **Participants**: [Participants]
       - **Summary**:
         - [Point 1]
         - [Point 2]
         - [Point 3]
       - **Action Items**:
         - [Action 1]
         - [Action 2]
