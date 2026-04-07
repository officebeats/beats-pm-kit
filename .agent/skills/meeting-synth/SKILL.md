---
name: meeting-synth
description: "Synthesize a single meeting transcript into structured action items, decisions, follow-ups, and stakeholder profiles. Use when processing a meeting recording, cleaning up transcript notes, or extracting commitments from a conversation."
priority: P0
maxTokens: 3000
triggers:
  - "/meet"
  - "/transcript"
version: 5.0.0 (Stakeholder-Aware)
author: Beats PM Brain
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Meeting Synthesizer Skill

> **Role**: Extract signal from noise. One meeting → structured output + stakeholder intelligence.

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
4. **Stakeholder Enrichment** (parallel with routing):
   - For each person mentioned or participating in the meeting:
     - Check if `4. People/{firstname-lastname}.md` exists.
     - **If exists** → Append new context under a dated section: decisions, positions taken, preferences, quotes, action items involving them.
     - **If new** → Create profile using the Stakeholder Profile Template (see §7).
   - **Extract role/title** from: meeting intros, how others address them, context clues, any shared email signatures in the transcript.
   - **Privacy Rule**: PII may be stored locally since `4. People/` is gitignored. Extract full contact info from signatures, intros, and context (work email, cell, office, pronouns).
5. **Write Summary**: Output to `3. Meetings/summaries/` using template from `assets/meeting_template.md`.

## 4. Output Format

Read the template at `assets/meeting_template.md` and format output exactly as shown.

## 5. Token Efficiency Rules

- **Single-pass extraction**: Read the transcript once, extract all five categories simultaneously (decisions, actions, questions, quotes, stakeholders).
- **No re-reads**: If a transcript is >1000 lines, summarize in chunks — never load full transcript twice.
- **Parallel writes**: Write summary + route action items + update stakeholder profiles in the same turn.
- **Skip boilerplate**: Ignore "hi how are you" and logistics chatter — focus on substance.

## 6. Boundary

- **This skill handles**: Single meeting transcript → structured summary with action items + stakeholder updates.
- **NOT for**: Daily tactical planning (use `daily-synth`). Weekly/monthly rollups (use `weekly-synth`).

## 7. Stakeholder Profile Template

When creating a new stakeholder profile in `4. People/`, use this format:

```markdown
# {Full Name}

> **Role**: {Title from intro, signature, or context}
> **Organization**: {Company/Team}
> **Relationship**: {Boss / Peer / Cross-Functional / Engineering / etc.}

---

## Context

- {How you know them, who introduced them, first interaction}

## Action Items

- [ ] {Any pending actions involving this person}

---

*Last Updated: {date} · Source: {transcript name or email subject}*
```

When updating an existing profile, append a new section:

```markdown
## Update — {date}

- {New context, decisions, positions, quotes from this interaction}
- Source: {transcript or email reference}
```
