---
description: Process all Quill meetings from the last 10 business days.
---

1. **Antigravity Native Intake (Primary)**:
   - Use Antigravity capture for transcripts directly into `0. Incoming/`.

2. **CLI Fallback (Secondary)**:
   - Run the targeted transcript fetcher.
   - // turbo
   - `python3 system/scripts/transcript_fetcher.py`

3. The system will now identify the new transcripts in `0. Incoming/`.

4. For each new transcript, execute the `meeting-synth` skill to generate a summary report in `3. Meetings/reports/`.
