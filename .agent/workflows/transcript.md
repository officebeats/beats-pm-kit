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

2. **CLI Fallback (Secondary)**:
   - Run the targeted transcript fetcher.
   - // turbo
   - `python3 system/scripts/quill_mcp_client.py || python3 system/scripts/transcript_fetcher.py`

3. **Parallel Identification**:
   - Scan `0. Incoming/` for new transcript files.
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
