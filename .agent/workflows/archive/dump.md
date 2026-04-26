---
description: Process captured clipboard content and route to appropriate trackers. Same behavior as /paste.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /dump - Inbox Processing Workflow

**Trigger**: User types `/dump` to process captured content in `0. Incoming/`

> **Value Prop**: Processes all pending content in `0. Incoming/`, classifies it, and routes to the correct tracker (TASK_MASTER.md, bugs-master.md, boss-requests.md, etc.)

> **Note**: This workflow has identical behavior to `/paste`. Either command can be used interchangeably.

## 1. Scan Pending Content

Scan these directories for unprocessed content:

| Directory | Content Type |
|-----------|--------------|
| `0. Incoming/raw/` | Text files from clipboard |
| `0. Incoming/staging/` | Images and files from clipboard |
| `0. Incoming/` | Direct file copies |

**Note**: Skip files already in `0. Incoming/processed/`, `0. Incoming/fyi/`

## 2. Content Classification

For each pending file:

### Text Files (`.md`, `.txt`, etc.)

1. **Read content**
2. **Apply inbox-processor logic**:
   - Extract tasks, bugs, decisions, boss asks, delegated items
   - Classify by priority (P0, P1, P2)
   - Identify company/product context from `SETTINGS.md`

### Image Files (`.png`, `.jpg`, etc.)

1. **Use visual-processor skill**
2. Extract text from image (OCR)
3. Process extracted text as above
4. If image contains UI bugs → Route to `bugs-master.md`
5. If image contains diagrams/specs → Keep in `0. Incoming/fyi/`

### File Types (`.pdf`, `.docx`, etc.)

1. **Read file content** (if text extractable)
2. Classify as:
   - **Reference material** → Move to `0. Incoming/fyi/`
   - **Spec/PRD** → Move to `2. Products/` + create task to review
   - **Meeting transcript** → Process for action items

## 3. Routing Table

| Item Type | Criteria | Destination | Status |
|-----------|----------|-------------|--------|
| **Boss Ask** | VIP request, "Urgent", "ASAP" | `5. Trackers/critical/boss-requests.md` | New |
| **Bug** | Software defect, error code, crash | `5. Trackers/bugs/bugs-master.md` | Open |
| **Task** | Any actionable item | `5. Trackers/TASK_MASTER.md` | New |
| **Delegated** | "Waiting for", "Sent to" | `5. Trackers/DELEGATED_TASKS.md` | Pending |
| **Decision** | "Agreed", "Decided", "Go/No-Go" | `5. Trackers/DECISION_LOG.md` | Logged |
| **Reference** | Non-actionable info | `0. Incoming/fyi/[Date]_[Topic].md` | N/A |
| **Unclear** | Total gibberish | `0. Incoming/BRAIN_DUMP.md` | N/A |

## 4. File Organization

After processing each file:

1. **Move to `0. Incoming/processed/`** with timestamp prefix
2. **Format**: `YYYYMMDD_HHMMSS_original_filename`

## 5. Output Confirmation

Generate a summary table:

```markdown
# 📥 Inbox Processed

| Type | Company | Ledger | Summary | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Task** | [Acme Corp] | TASK_MASTER | Fix login issue | P1 |
| **Bug** | [Acme Corp] | bugs-master | Error 500 on checkout | P0 |
| **Boss** | [Acme Corp] | boss-requests | Review Q3 deck | **P0** |

> **Next**: Run `/now` to see updated priorities.
```

## 6. Empty State Handling

If no pending content found:

```markdown
✅ Inbox is clean. No pending items to process.

> **Tip**: Use `/paste` to capture clipboard content.
```

## Notes

- **Cross-Platform**: Works on Windows and Mac
- **CLI Compatible**: Optimized for Claude Code, Kilo Code, Gemini CLI
- **Zero-Loss**: Every input is logged somewhere
- **Privacy**: PII redacted before writing to trackers
- **Interchangeable**: `/dump` and `/paste` have identical behavior
