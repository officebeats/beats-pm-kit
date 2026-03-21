---
description: Capture clipboard content (text, images, files) and save for processing.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /paste - Clipboard Capture & Triage

**Trigger**: User types `/paste` to capture whatever is on their clipboard.

> **Value Prop**: One command to capture **both** the active clipboard (Slack, images, files) **and** any items manually dropped into the `0. Incoming/` folder (The Drop Zone).

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
    - **Option B (Image)**: Save to `0. Incoming/staging/` and invoke `visual-processor`.
    - **Option C (File)**: Move to `0. Incoming/staging/`.
    - Use Antigravity clipboard ingest for text/images/files.
    - Proceed directly to classification via `inbox-processor`.

5.  **CLI Fallback (Secondary)**:
    - Run: `python system/scripts/clipboard_bridge.py`
    - Script auto-detects content type (text, image, or files).

6.  **Execute File Organizer (The Concierge)**:
    - Run: `python system/scripts/file_organizer.py`
    - Scans `0. Incoming/` for new files.
    - Prompts user for intent: "Task Source? Reference? Spec?"
    - Moves processed files to `0. Incoming/processed/`.

7.  **Content Detection Priority**:
    - **Files** (copied from file manager) → Saved to `0. Incoming/staging/`
    - **Image** (screenshot to clipboard) → Saved to `0. Incoming/staging/`
    - **Text** (copied text) → Saved to `0. Incoming/raw/`

8.  **Classification** (via `inbox-processor` skill):
    - **Bug** (error, crash, broken) → Route to `5. Trackers/bugs/bugs-master.md`
    - **Boss Ask** (VIP speaker, urgent, ASAP) → Route to `5. Trackers/critical/boss-requests.md`
    - **Task** (TODO, action item, deadline) → Route to `5. Trackers/TASK_MASTER.md`
    - **Decision** (decided, agreed, go/no-go) → Route to `5. Trackers/DECISION_LOG.md`
    - **FYI** (heads up, no action) → Keep in `0. Incoming/fyi/`
    - **Unclear** → Route to `BRAIN_DUMP.md` (Parking Lot)

9.  **Entity Tagging**:
    - Tag with `[Company A]`, `[Company B]`, or ask if unclear.

10. **Output**:
    - Confirmation table of what was captured and where it was routed.

## Supported Content Types

| Type      | Windows             | Mac              | Destination            |
| :-------- | :------------------ | :--------------- | :--------------------- |
| **Text**  | ✅ PowerShell       | ✅ `pbpaste`     | `0. Incoming/raw/`     |
| **Image** | ✅ PIL.ImageGrab    | ✅ PIL.ImageGrab | `0. Incoming/staging/` |
| **Files** | ✅ PowerShell + PIL | ✅ AppleScript   | `0. Incoming/staging/` |

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
- **Screenshot Support**: Win+Shift+S or Cmd+Shift+4 → `/paste` → Image saved.
- **Zero-Loss**: Every input is logged somewhere. If uncertain, defaults to `BRAIN_DUMP.md`.
