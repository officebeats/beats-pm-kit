# 📥 Transcript Intake Template

> **Usage**: Pre-process raw transcripts BEFORE feeding to the Meeting Synthesizer.
> **Goal**: Structure metadata and pre-extract Fathom action items to reduce context window load.

---

## Metadata

- **Date**: [YYYY-MM-DD]
- **Duration**: [XX mins]
- **Participants**: [Comma-separated list]
- **Recording Link**: [Fathom/Loom URL]
- **Meeting Type**: [Quick Sync / Strategy / 1:1 / Standup / Other]

---

## Pre-Extracted Action Items (from Fathom)

> These are auto-tagged by Fathom with `ACTION ITEM:`. Copy them here verbatim.

| Timestamp | Action | Assigned To | Link |
| :--- | :--- | :--- | :--- |
| 0:00 | [Action description] | [Name] | [Fathom link] |

---

## Key Topics (Timestamp Ranges)

| Time Range | Topic |
| :--- | :--- |
| 0:00–5:00 | [Topic 1] |
| 5:00–10:00 | [Topic 2] |

---

## Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

[Paste raw transcript here]

</details>

---

## Extraction Manifest (Agent Output)

> Filled by the agent after processing.

- **Decisions Logged**: [Count] → `DECISION_LOG.md`
- **Tasks Created**: [Count] → `tasks-master.md`
- **Quotes Indexed**: [Count] → `quote-index.md`
- **Items Parked**: [Count] → `BRAIN_DUMP.md`

---
_Template Version: 1.0 | Cross-Platform Ready_
