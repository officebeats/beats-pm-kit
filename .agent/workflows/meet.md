---
description: Synthesize meeting transcripts into action items, decisions, and summaries.
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
Get-ChildItem -Path "3. Meetings/transcripts/" -File -Filter "*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, LastWriteTime
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

### Step 5: Confirm

Show user:
- Summary file path
- Count of action items routed
- Any boss asks flagged
