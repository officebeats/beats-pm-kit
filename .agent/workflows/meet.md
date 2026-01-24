---
description: Prepare for meetings or process transcripts.
---

# 🎙️ Meeting Playbook

This workflow guides the **Staff PM** to handle the meeting lifecycle.

## Steps

1.  **Mode Selection**:
    - **Prep**: "Get me ready for the 1:1 with [Name]".
    - **Process**: "Summarize this transcript".

2.  **Parallel Prep Mode**:
    - **Action**: In a SINGLE turn, read `4. People/[Name].md` AND `5. Trackers/critical/boss-requests.md`.
    - **Synthesis**: Cross-reference open tasks with the person's profile.
    - **Output**: A 3-bullet agenda with "Previous Action Item" status usage.

3.  **Process Mode**:
    - **Input**: A new transcript file (txt/md) in `0. Incoming/` or `3. Meetings/transcripts/`.
    - **Action**: Run `meeting-synth` skill.
    - **Extract**:
      - **Action Items** -> Add to `/track`.
      - **Decisions** -> Add to `5. Trackers/DECISION_LOG.md`.
      - **Quotes** -> Add to `quote-index.md`.

4.  **Output**:
    - A clean Meeting Note file in `3. Meetings/reports/`.
