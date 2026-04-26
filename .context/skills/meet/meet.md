---
description: Synthesize meeting transcripts into action items, decisions, and summaries.
source_tool: antigravity
source_path: .agents\workflows\meet.md
imported_at: 2026-04-25T21:29:42.772Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

## Workflow: `/meet` (aliases: `/transcript`, `#transcript`, `#meet`)

**Agent**: Staff PM → `meeting-synth` skill

---

### Step 1: Determine Input Source

Ask the user which input method they prefer:

1. **Paste transcript** → User pastes raw text → Proceed to Step 3.
2. **Provide file path** → User gives a specific file → Read it → Proceed to Step 3.
3. **Process latest** → Search `3. Meetings/transcripts/` (MaxDepth 1, last 5 business days) → Show user the file list, confirm selection → Proceed to Step 3.

> ⚠️ **Do NOT** recursively scan `0. Incoming/` or project root. Only search `3. Meetings/transcripts/` with bounded depth.

### Step 2: Bounded File Discovery (only if Step 1 option 3)

// turbo
```bash
ls -lt "3. Meetings/transcripts/" | head -10
```

- Show user the list of recent files.
- Let user pick which transcript(s) to process (max 3 at a time).

### Step 3: Execute `meeting-synth` Skill

- **Action**: Read the `meeting-synth` SKILL.md from `.agent/skills/meeting-synth/`.
- **Process**: Single-pass extraction — read transcript once, extract all categories simultaneously.
- **Output**: Use template from `assets/meeting_template.md`.

### Step 4: Route Outputs (Parallel)

In a **single parallel turn**:
- Write summary → `3. Meetings/summaries/[filename]-summary.md`
- Append action items → `5. Trackers/TASK_MASTER.md`
- Flag boss asks → `5. Trackers/critical/boss-requests.md` (if any)

### Step 5: Stakeholder Enrichment

For each person mentioned in the transcript:
- **Check** if `4. People/{firstname-lastname}.md` exists.
- **If exists** → Update with new context: decisions they made, positions they took, preferences expressed, role changes.
- **If new** → Create profile with: Name, Role (from intro or context clues), Organization, Relationship to user, Context from the meeting, Action items involving them.
- **Extract role/title** from how people introduce themselves, how others reference them, or from any shared email signatures.
- **Privacy**: Store only professional context. No PII (personal phone, home address, personal email).

### Step 6: Confirm

Show user:
- Summary file path
- Count of action items routed
- Any boss asks flagged
- Stakeholder profiles created or updated
