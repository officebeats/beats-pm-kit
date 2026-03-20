---
name: meeting-synth
description: "Synthesize a single meeting transcript into structured action items, decisions, and follow-ups. Use when processing a meeting recording, cleaning up transcript notes, or extracting commitments from a conversation."
priority: P0
maxTokens: 3000
triggers:
  - "/meet"
  - "/transcript"
version: 4.0.0 (Token Optimized)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Meeting Synthesizer Skill

> **Role**: Extract signal from noise. One meeting → structured output.

## 1. Native Interface

- **Inputs**: `/meet`, `/transcript`. Raw transcript text, pasted content, or file path.
- **Tools**: `view_file` (transcript files), `write_to_file`.
- **Template**: `assets/meeting_template.md` (JIT loaded — read only when generating output).

## 2. Search Constraints (CRITICAL)

> **Anti-Pattern**: Do NOT recursively scan `0. Incoming/` or `3. Meetings/` broadly.
> Searching too many files wastes tokens and slows processing.

### Bounded Search Protocol

1. **User provides transcript directly** (paste or file path) → Skip all search. Process immediately.
2. **User says "process latest transcript"** → Search ONLY `3. Meetings/transcripts/` with `MaxDepth: 1`, sort by modified date, take most recent **1-3 files only**.
3. **User says "process all new transcripts"** → Search `3. Meetings/transcripts/` with `MaxDepth: 1`, limit to files modified in the **last 5 business days** only.
4. **Never** use `grep_search` or `find_by_name` with unbounded recursion on the project root.
5. **Never** read files outside `3. Meetings/` and `0. Incoming/` for transcript processing.

### File Identification Heuristic

Transcripts match: `*.md`, `*.txt` files containing participant names, timestamps, or dialog markers (`:`).
**Do NOT** open non-transcript files (PRDs, trackers, configs) — check filename first.

## 3. Cognitive Protocol

1. **Ingest**: Read the transcript (pasted, file path, or bounded search).
2. **Extract** (single-pass — do NOT re-read):
   - **Decisions Made**: What was agreed on.
   - **Action Items**: Who does what by when (`Owner + Due Date`).
   - **Open Questions**: Unresolved topics needing follow-up.
   - **Key Quotes**: Verbatim stakeholder statements worth preserving.
3. **Route** (parallel writes):
   - Action items → `5. Trackers/TASK_MASTER.md`
   - Boss Asks → `5. Trackers/critical/boss-requests.md`
4. **Write Summary**: Output to `3. Meetings/summaries/` using template from `assets/meeting_template.md`.

## 4. Output Format

Read the template at `assets/meeting_template.md` and format output exactly as shown.

## 5. Token Efficiency Rules

- **Single-pass extraction**: Read the transcript once, extract all four categories simultaneously.
- **No re-reads**: If a transcript is >1000 lines, summarize in chunks — never load full transcript twice.
- **Parallel writes**: Write summary + route action items in the same turn.
- **Skip boilerplate**: Ignore "hi how are you" and logistics chatter — focus on substance.

## 6. Boundary

- **This skill handles**: Single meeting transcript → structured summary with action items.
- **NOT for**: Daily tactical planning (use `daily-synth`). Weekly/monthly rollups (use `weekly-synth`).
