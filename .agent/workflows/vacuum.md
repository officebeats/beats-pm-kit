---
description: System optimization, task archiving, and hierarchical integrity auditing.
---

# Vacuum Protocol Workflow

Execute the full Centrifuge Protocol to keep the brain lean, private, and organized.

## 1. System Vision Check (Native)

    - **Action**: In a SINGLE turn, `list_dir` on `5. Trackers/` and `3. Meetings/summaries/`.
    - **Logic**: Identify items matching `[x]` (Completed) or older than 30 days.

## 2. Validation & Audit

    - **Privacy**: Check `grep_search` for sensitive keys in root.
    - **Integrity**: Audit of hierarchical structure (Folders 1, 2, 4).
    - **Cleanup**: Move completed items to `archive/2026/`.

## 3. Processing (New)

    - **Action**: Run `/transcript` to process any pending meetings since the last run.
    - **Logic**: Ensure all warm meetings are synthesized into reports.

## 4. Storage Hierarchy

| Tier     | Duration  | Location                 |
| :------- | :-------- | :----------------------- |
| **Hot**  | Active    | `5. Trackers/`           |
| **Warm** | 7-30 Days | `3. Meetings/summaries/` |
| **Cold** | 30+ Days  | `archive/`               |

> [!NOTE]
> Running this workflow automatically moves completed items (`- [x]`) from your active trackers to the yearly archive.
