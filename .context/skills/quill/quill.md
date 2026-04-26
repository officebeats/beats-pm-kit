---
description: Process and display the last 5 Quill meetings in a compact, color-coded bullet list with 3-point summaries and action items.
source_tool: antigravity
source_path: .agents\workflows\quill.md
imported_at: 2026-04-25T21:29:42.797Z
ai_context_version: 0.9.2
---

1. Run the Quill export script to fetch the last 5 meetings.
// turbo
2. `python system/scripts/quill_export.py`

3. For each meeting in the output:
   - Extract **Title**, **Timestamp**, **Participants**, and **Transcript**.
   - Generate a **3-point bullet summary** from the Transcript.
   - Extract a list of **Action Items** (Owner + Task) from the Transcript.
   - Format the **Date** from the Timestamp using 'EEEE, MMMM d, yyyy h:mm a' (e.g., Monday, December 8, 2025 7:23 PM).
   - Format the **Title** in bold with a distinct color emoji for visibility (e.g., 🟦 **[Title]**).

4. Present the meetings in a compact bullet list format:
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
