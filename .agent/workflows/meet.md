---
description: Synthesize meeting transcripts into action items, decisions, and summaries.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

## Workflow: `/meet` (aliases: `/transcript`, `#transcript`, `#meet`)

**Agent**: Staff PM → `meeting-synth` skill

---

### Step 1: Determine Input Source

Detect which input method the user is using:

1. **Quill paste detected** → User pastes text with Quill structure (sections like "Summary", "Key takeaways", "Followups", structured bullets with speaker names) → Auto-detect, skip to Step 2B.
2. **Raw transcript paste** → User pastes raw transcript text → Proceed to Step 3.
3. **Provide file path** → User gives a specific file → Read it → Proceed to Step 3.
4. **Process latest** → Search `3. Meetings/transcripts/` (MaxDepth 1, last 5 business days) → Show user the file list, confirm selection → Proceed to Step 3.

> ⚠️ **Do NOT** recursively scan `0. Incoming/` or project root. Only search `3. Meetings/transcripts/` with bounded depth.
> ⚠️ **Do NOT** ask the user which method they prefer if they already pasted content. Auto-detect and process.

### Step 2A: Bounded File Discovery (only if Step 1 option 4)

// turbo
```bash
ls -lt "3. Meetings/transcripts/" | head -10
```

- Show user the list of recent files.
- Let user pick which transcript(s) to process (max 3 at a time).

### Step 2B: Quill Paste Fast Path

When user pastes Quill meeting notes directly:
1. **Detect Quill format**: Look for structured sections (Summary, Key takeaways, Followups, speaker-attributed bullets).
2. **Extract meeting metadata**: Date, attendees, subject from the content.
3. **Auto-save**: Write the pasted content to `0. Incoming/YYYY-MM-DD_MeetingSubject.txt` for archival.
4. **Process immediately**: Do NOT ask for confirmation — treat as direct input to Step 3.

### Step 3: Execute `meeting-synth` Skill

- **Action**: Read the `meeting-synth` SKILL.md from `.agent/skills/meeting-synth/`.
- **Detect Meeting Type**: Before processing, classify the meeting:
  - **Manager 1:1** → If attendees include the user's direct manager: trigger **Manager Meeting Mode** (see meeting-synth skill § 3A).
  - **Peer/Stakeholder** → Standard processing.
  - **Customer/Partner** → Standard processing with competitive intel extraction.
- **Process**: Single-pass extraction — read transcript once, extract all categories simultaneously.
- **Output**: Use template from `assets/meeting_template.md`.

### Step 4: Route Outputs (Parallel)

In a **single parallel turn**:
- Write summary → `3. Meetings/summaries/[filename]-summary.md`
- Append action items → `5. Trackers/TASK_MASTER.md`
- Flag boss asks → `5. Trackers/critical/boss-requests.md` (if any)

**Manager Meeting Mode additions (if triggered):**
- Update `1. Company/ways-of-working.md` with new operating agreements, scope changes, process updates
- Update the manager's profile in `4. People/` with new quotes, preferences, commitments
- Extract any new stakeholder dynamics or relationship context the manager shared about others

### Step 5: Stakeholder Enrichment

For each person mentioned in the transcript:
- **Check** if `4. People/{firstname-lastname}.md` exists.
- **If exists** → Update with new context: decisions they made, positions they took, preferences expressed, role changes.
- **If new** → Create profile with: Name, Role (from intro or context clues), Organization, Relationship to user, Context from the meeting, Action items involving them.
- **Extract role/title** from how people introduce themselves, how others reference them, or from any shared email signatures.
- **Manager context**: If the direct manager described this person's dynamics, working style, or political position, capture that in the profile under "Working Preferences" or "Context."
- **Privacy**: PII may be stored locally since `4. People/` is gitignored. Extract full contact info from email signatures (work email, cell, office, pronouns).

### Step 6: Confirm

Show user:
- Summary file path
- Count of action items routed
- Any boss asks flagged
- Stakeholder profiles created or updated
- **Manager Mode**: Ways of Working updates applied (if triggered)
