---
name: outlook-navigator
description: Read-only Outlook email scraper for context, task extraction, and stakeholder enrichment.
priority: P1
triggers:
  - "/outlook"
  - "/inbox"
  - "/sync-mail"
version: 2.1.0
---

> **Compatibility Directive**: Optimized for Google Antigravity/macOS desktop clients.

# Outlook Navigator Skill

## Goal
The outlook-navigator is the 'Eye' of the brain into the user's primary communication channel. It fetches recent emails for context but NEVER performs write operations (no replying, no deleting).

## Inputs
- `/outlook` (Fetch last 5)
- `/outlook --count 10`
- `/inbox`

## Protocol

### Step 1: Fetch Inbox (Snippets)
Run the bridge script to get subject/sender/date/snippet for recent messages:
```bash
python3 system/scripts/outlook_bridge.py --count {n}
```

### Step 2: Deep-Read Specific Emails
When full email body is needed (e.g., extracting tasks from a boss email), use the `--search` flag:
```bash
python3 system/scripts/outlook_bridge.py --search "subject keyword"
```
This uses `osascript` to query the local Microsoft Outlook app via AppleScript and returns the full plain-text body of matching emails.

**Fallback**: If the bridge script fails (e.g., sender metadata errors on meeting invites), use inline `osascript` directly:
```bash
osascript -e '
tell application "Microsoft Outlook"
    set msgs to messages of inbox
    set output to ""
    set counter to 0
    repeat with msg in msgs
        if counter < 20 then
            set subj to subject of msg
            if subj contains "KEYWORD" then
                set output to output & "===== SUBJECT: " & subj & " =====" & return
                set output to output & "DATE: " & (time received of msg as string) & return
                set output to output & "BODY:" & return
                try
                    set output to output & (plain text content of msg) & return
                on error
                    try
                        set output to output & (content of msg) & return
                    end try
                end try
                set output to output & "===== END =====" & return & return
            end if
            set counter to counter + 1
        end if
    end repeat
    return output
end tell'
```

### Step 3: Persist
Write results to `0. Incoming/outlook_context.md` for downstream skills:
- // turbo
- `python3 system/scripts/outlook_bridge.py --count 10 > "0. Incoming/outlook_context.md"`

### Step 4: Analyze
- Identify **Deadlines** (dates, "by Friday", "asap").
- Identify **Decisions** (approvals, rejects).
- Identify **Company Strategy** changes.

### Step 5: Stakeholder Enrichment
For each person found in emails (senders, CC'd, mentioned, or in signatures):
- **Check** if `4. People/{firstname-lastname}.md` exists.
- **If exists** → Update with new context: recent topics, decisions, asks, role changes.
- **If new** → Create profile from email signature and context.
- **Signature extraction**: Parse email signatures for role, title, department, organization. This is the richest source of role/title data.
- **Privacy**: Store only professional context (name, role, org, relationship). PII (phone, email, address) may be stored in profiles since `4. People/` is gitignored. Extract everything useful from signatures — work email, cell, office address, pronouns, direct reports.

### Step 6: Triage
- If a task is found → Suggest `/track` item.
- If a boss ask is found → Route to `5. Trackers/critical/boss-requests.md`.
- If a new stakeholder is mentioned → Create/update profile in `4. People/`.
- If context is found → Suggest `memory-consolidator` update.

## Implementation Notes

### Why AppleScript (osascript)?
- The bridge uses `osascript` to query the locally-installed Microsoft Outlook app on macOS.
- This avoids browser authentication flows and works offline with cached mail.
- **Known issue**: Some message types (meeting invites, `«class mtME»`) don't expose `name of sender`. The bridge handles this with try/catch fallback to `address of sender`.

### Privacy
- This skill is **read-only**. It NEVER sends, replies, or deletes emails.
- Email content persisted to `0. Incoming/` is gitignored and local-only.
- Stakeholder profiles in `4. People/` are gitignored and local-only.

## Output Format

### 📬 Inbox Context (Read-Only)

- **[Subject]** (from [Sender] at [Date])
  * *Snippet*: "[200-char preview...]"
  * *PM Action*: [Identified task or context update]
  * *Stakeholder*: [Created/Updated profile for X] (if applicable)
