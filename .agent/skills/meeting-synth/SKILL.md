---
name: meeting-synth
description: "Synthesize a single meeting transcript into structured action items, decisions, follow-ups, and stakeholder profiles. Use when processing a meeting recording, cleaning up transcript notes, or extracting commitments from a conversation."
priority: P0
maxTokens: 3000
triggers:
  - "/meet"
  - "/transcript"
version: 5.5.0 (Double-Click Integrated)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.
> **Cloud Safe**: Use run_command for file operations to bypass iCloud sync-locks.


# Meeting Synthesizer Skill

> **Role**: Extract signal from noise. One meeting → structured output + stakeholder intelligence.

## 1. Native Interface

- **Inputs**: /meet, /transcript. Raw transcript text or file path.
- **Tools**: run_command (cat), view_file.

---

## 2. Bounded Search Protocol

1. **User provides transcript directly** → Process immediately.
2. **User says "process latest"** → Search ONLY 3. Meetings/transcripts/ MaxDepth: 1, limit to 1-3 files.

---

## 3. Cognitive Protocol (Double-Click Integration)

1. **Ingest**: Read the transcript.
2. **Extract** (single-pass):
   - **Decisions**: Formalized agreements.
   - **Action Items**: Task + ID (if existing) + Owner + Due.
   - **Key Quotes**: Verbatim statements with attribution.
3. **Route & Update** (Parallel Cloud-Safe Writes):
   - **New Action items** → 5. Trackers/TASK_MASTER.md + Create 5. Trackers/tasks/{ID}.md.
   - **Existing Task Updates**: If a TASK_ID (e.g. P1-001) is mentioned, update its detail file's "Progress Log" and "Stakeholder Quotes".
   - **Stakeholder Enrichment**: Update 4. People/{firstname-lastname}.md "Interaction Stream" with quotes and the "Active Tasks" or "Awaiting" sections.
4. **Summary**: Write to 3. Meetings/summaries/ using assets/meeting_template.md. **MANDATORY**: Append the full raw transcript at the end of the file under a `# 📝 Full Transcript` section.

---

## 4. Output Format

Confirm all updates:
- Summary File created.
- Task Details updated (list IDs).
- Stakeholder Profiles updated (list Names).

---

## 5. Privacy & Efficiency

- Redact PII.
- Single-pass extraction.
- Skip logistics chatter.
