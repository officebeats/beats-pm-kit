---
description: Capture clipboard content (text, images, files) and save for processing.
---

# /paste - Clipboard Capture & Triage

**Trigger**: User types `/paste` to capture whatever is on their clipboard.

> **Value Prop**: One command to capture Slack messages, screenshots, emails, or files directly from the clipboard, classify them, and route to the correct tracker.

## Steps

// turbo

1.  **Antigravity Native Capture (Primary)**:
    - Use Antigravity clipboard ingest for text/images/files.
    - Proceed directly to classification via `inbox-processor`.

2.  **CLI Fallback (Secondary)**:
    - Run: `python system/scripts/clipboard_bridge.py`
    - Script auto-detects content type (text, image, or files).

3.  **Execute File Organizer (The Concierge)**:
    - Run: `python system/scripts/file_organizer.py`
    - Scans `0. Incoming/` for new files.
    - Prompts user for intent: "Task Source? Reference? Spec?"
    - Moves processed files to `0. Incoming/processed/`.

4.  **Content Detection Priority**:
    - **Files** (copied from file manager) → Saved to `0. Incoming/staging/`
    - **Image** (screenshot to clipboard) → Saved to `0. Incoming/staging/`
    - **Text** (copied text) → Saved to `0. Incoming/raw/`

5.  **Classification** (via `inbox-processor` skill):
    - **Bug** (error, crash, broken) → Route to `5. Trackers/bugs/bugs-master.md`
    - **Boss Ask** (VIP speaker, urgent, ASAP) → Route to `5. Trackers/critical/boss-requests.md`
    - **Task** (TODO, action item, deadline) → Route to `5. Trackers/TASK_MASTER.md`
    - **Decision** (decided, agreed, go/no-go) → Route to `5. Trackers/DECISION_LOG.md`
    - **FYI** (heads up, no action) → Keep in `0. Incoming/fyi/`
    - **Unclear** → Route to `BRAIN_DUMP.md` (Parking Lot)

6.  **Entity Tagging**:
    - Tag with `[Company A]`, `[Company B]`, or ask if unclear.

7.  **Output**:
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
