---
description: Capture clipboard content (text, screenshots/images, files) and route task signals to TASK_MASTER by default.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.



# /paste - Clipboard Capture & Triage

**Trigger**: User types `/paste` to capture whatever is on their clipboard, or `/paste --teams` (or `/ingest-teams`) to trigger Microsoft Teams ingest.

> **Value Prop**: One command to capture **both** the active clipboard (Slack, images, files) **and** any items manually dropped into the `0. Incoming/` folder (The Drop Zone).

---

## PM Decision Router Preflight

Load `.agent/skills/pm-decision-router/SKILL.md` before extraction. When text is available from chat, clipboard, OCR, or file preview, classify it with:

```bash
python3 system/scripts/pm_decision_router.py --text "<captured text>"
```

Use the router result to decide whether the capture should become an existing-task update, new task, discovery brief, scope challenge, prioritization pass, document request, decision log, archive-only note, or explicit user question. If the router returns `scope_challenge` or `ask_user`, do not silently create an active task; return the candidate update and blocking question.

---

## Default Intent Contract

Screenshots/images and transcript-like clipboard text are task-master management inputs unless the user explicitly says otherwise.

- Do not ask "what should I do with this?" for a screenshot or transcript that contains visible work signal.
- Extract tasks, status changes, blockers, owners, due dates, source references, and referenced tickets/links first.
- For screenshots/images and user-provided excerpts, transcribe the full visible text verbatim (privacy-redacted; mark `[REDACTED]`/`[ILLEGIBLE]`) into the evidence transcript's `Extracted Text` section per `chat-transcript-archive`, so the evidence is reusable later without the image.
- Route accepted work through `task-manager` Priority Gate into `5. Trackers/TASK_MASTER.md` and `5. Trackers/tasks/`.
- Render user-facing task/workstream labels from readable titles and source provenance. Keep Task Master IDs, Jira IDs, Trello IDs, and source IDs only in local links, metadata, or an `Agent refs` line.
- If the evidence is ambiguous, return concrete candidate tracker updates for user confirmation instead of switching to profile lookup, reply drafting, or generic summarization.

---

## Fast Path: Evidence Already In Chat

When the screenshot/image/text is already attached to the current chat turn, skip clipboard ingest and drop-zone scanning. Treat the attachment as the captured input and proceed directly to extraction and local routing.

Use this fast path when:
- The input is a single screenshot, email/chat snippet, or short transcript excerpt.
- It clearly maps to an existing task or a small number of candidate tasks.
- No fresh Slack, Teams, Outlook, Calendar, Jira, or Confluence read is required.

Fast-path steps:
1. Extract status, owner, due date, dependency, source platform, participants, and exact follow-up date.
2. Search local trackers for a matching existing item before creating anything new.
3. Read only `TASK_MASTER.md`, the matched task detail file(s), and relevant people profiles.
4. Save the compact local evidence transcript/report when the screenshot represents communication evidence: `3. Meetings/chat-transcripts/{platform}/...` with a run entry in `3. Meetings/chat-transcripts/_manifest.json`, including the verbatim `Extracted Text` section. The attached-chat fast path does not stage anything in `0. Incoming/`.
5. Capture display provenance for touched work: readable title, started date/source, latest progress source, and internal refs.
6. Apply local tracker/profile updates.
7. Refresh task health with targeted triage:

```bash
python3 system/scripts/task_master_triage.py --apply --touched-task <TASK_ID>
```

Run the full `/paste` dual-path capture only when the user invokes `/paste`, asks to ingest the clipboard/drop zone, or the attached evidence is ambiguous enough that local capture/scanning is needed.

---

## ⚡ Step 1: Dual-Path Capture (Parallel)

In a **single turn**, perform BOTH of the following:

1. **Clipboard Ingest**: Capture text, images, or files currently on the system clipboard.
2. **Drop Zone Scan**: Scan `0. Incoming/` for new, unprocessed files.

// turbo
```powershell
# Scan for unprocessed items in the Drop Zone
Get-ChildItem -Path "0. Incoming/" -Recurse | Where-Object { $_.PSIsContainer -eq $false -and $_.FullName -notmatch "processed" } | Select-Object Name, FullName, LastWriteTime
```

---

## ⚡ Step 2: Intake & Classification
    - **Option A (Text)**: Append to `0. Incoming/raw/YYYY-MM-DD_clipboard.md`.
    - **Option B (Image/Screenshot)**: Save to `0. Incoming/staging/`, extract visible text/context, then treat as task-master evidence by default.
    - **Option C (File)**: Move to `0. Incoming/staging/`. For a supported non-Markdown file, load `.agent/skills/markitdown/SKILL.md`, run `python3 system/scripts/markdown_intake.py "<staged-file>" --automatic`, preserve the original, and use the sibling `.md` file for extraction and routing.
    - **Option D (Teams Context - if `--teams` flag used)**: Run `python3 system/scripts/beats.py teams --args "--json"` to ingest Teams chat.
    - Use Antigravity clipboard ingest for text/images/files.
    - Proceed directly to task classification via `inbox-processor` plus `task-manager`.

5.  **CLI Fallback (Secondary)**:
    - Run: `python system/scripts/clipboard_bridge.py`
    - Script auto-detects content type (text, image, or files).

6.  **Execute File Organizer (The Concierge)**:
    - Run: `python system/scripts/file_organizer.py`
    - Scans `0. Incoming/` for new files.
    - Do not prompt for intent when the item is a screenshot/image or transcript with task/status signal; assume task-master management.
    - Prompt only when the item has no task signal and the durable destination is unclear.
    - Moves processed files to `0. Incoming/processed/`.

7.  **Content Detection Priority**:
    - **Files** (copied from file manager) → Saved to `0. Incoming/staging/`
      - PDF, DOCX, PPTX, XLS/XLSX, MSG, HTML, CSV, JSON, XML, and EPUB files are converted locally to a sibling Markdown intake file before classification.
      - Screenshots/images stay on the existing visual-extraction path; ZIP and audio conversion remain explicit-only.
    - **Image** (screenshot to clipboard) → Saved to `0. Incoming/staging/`, then extracted for `TASK_MASTER.md` updates by default
    - **Text** (copied text) → Saved to `0. Incoming/raw/`; transcript-like text is routed as task-master evidence by default
    - **Teams** (if `--teams` used) → Fetch via Teams API/Bridge and route to `inbox-processor`.

8.  **Classification** (via `inbox-processor` and `task-manager` skills):
    - **Bug** (error, crash, broken) → Route to `5. Trackers/bugs/bugs-master.md`
    - **Boss Ask** (VIP speaker, urgent, ASAP) → Route to `5. Trackers/critical/boss-requests.md`
    - **Task** (TODO, action item, deadline) → Route to `5. Trackers/TASK_MASTER.md`
    - **Existing Task Update** (status/progress/blocker on known work) → Update `TASK_MASTER.md` and the matching detail file
    - **Decision** (decided, agreed, go/no-go) → Route to `5. Trackers/DECISION_LOG.md`
    - **FYI** (heads up, no action) → Keep in `0. Incoming/fyi/`
    - **Unclear screenshot/transcript** → Return candidate local tracker updates for confirmation with readable task/workstream labels
    - **Unclear non-task input** → Route to `BRAIN_DUMP.md` (Parking Lot)

9.  **Entity Tagging**:
    - Tag with `[Company A]`, `[Company B]`, or ask if unclear.

10. **Output**:
    - Confirmation table of what was captured and where it was routed.
    - Human-readable task/workstream labels plus source provenance; IDs only in internal refs.

## Supported Content Types

| Type      | Windows             | Mac              | Destination            |
| :-------- | :------------------ | :--------------- | :--------------------- |
| **Text**  | ✅ PowerShell       | ✅ `pbpaste`     | `0. Incoming/raw/`     |
| **Image** | ✅ PIL.ImageGrab    | ✅ PIL.ImageGrab | `0. Incoming/staging/` |
| **Files** | ✅ PowerShell + PIL | ✅ AppleScript   | `0. Incoming/staging/` + supported sibling `.md` |

## Example Usage

```
User: /paste
Agent: --- 📋 Clipboard Bridge (/paste) ---
       ✅ Saved text: 2026-01-19_094500_slack.md

       ## Captured & Routed

       | Type | Company | Routed To | Summary |
       | :--- | :--- | :--- | :--- |
       | Task | [Company A] | TASK_MASTER.md | Review Q3 deck by Friday |
```

## Notes

- **Cross-Platform**: Works on Windows and Mac.
- **File Manager Support**: Copy files in Explorer/Finder → `/paste` → They're imported.
- **Screenshot Support**: Win+Shift+S or Cmd+Shift+4 → `/paste` → Image saved and interpreted as task-master evidence by default.
- **Zero-Loss**: Every input is logged somewhere. If uncertain, defaults to `BRAIN_DUMP.md`.
