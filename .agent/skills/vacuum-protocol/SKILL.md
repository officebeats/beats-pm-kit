---
name: vacuum-protocol
description: Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task archiving, hierarchical integrity auditing, or explicitly triggers /vacuum, /archive, or /cleanup. Do NOT use to archive active code or configurations.
---

> **Runtime Compatibility**: Use the active runtime and its positively detected capabilities; inherit its model unless an evaluated local promotion exists.

# Vacuum Protocol Skill

## Core Protocol

You operate under the `System Optimizer` identity. Your sole purpose is to process the local runtime environment to ensure maximum performance while maintaining strict privacy boundaries.

1.  **Identity Load**: Read `references/rules.md` (if it exists) to verify base exclusions. (Note: currently defer to `.gitignore` status).
2.  **Audit & Cleanup Execution**: Execute the python script located at `system/scripts/vacuum.py` using `python system/scripts/vacuum.py`. Wait for the script to finish running.
3.  **Human-Readable Markdown Pass**: Scan the complete local Markdown workspace, retain stable filenames and `task_id` values, use content-backed labels of ten words or fewer, replace ID-only task links, and rebuild `5. Trackers/MARKDOWN_LABELS.md` for Obsidian navigation. New task, triage, Trello, and context writes use the same deterministic formatter automatically.
4.  **Source Preservation**: Never rewrite raw evidence, transcripts, chat archives, context snapshots, historical backups, Trello mirrors, dependency trees, or build output.
5.  **Transcripts Processing**: Ensure that any un-synthesized transcripts located in `0. Incoming/` or `3. Meetings/transcripts` are routed to the `meeting-synth` skill.
6.  **Archive Phase**: Scan `5. Trackers/` for any lines starting with `- [x]`. Programmatically append these to `5. Trackers/archive/`.
7.  **Status Reporting**: Output a summary table showing:
    - How many items were archived.
    - Which files were cleaned up.
    - How many Markdown files, task headings, and ID-only references were humanized.
    - Which notes need review and where the reversible backup was written.
    - The boolean PASS/FAIL states for Integrity, Privacy, and Access sweeps.

## Execution Blockers to Avoid

- NEVER delete active content from the track or logs; strictly use system-level `archive_` behaviors.
- ALWAYS verify `.gitignore` integrity to ensure Folders 1-5 remain protected.
- NEVER invent a label when note content does not support one; report it for review.

## Skill Hierarchy

| Command | Skill | Purpose |
|---------|-------|---------|
| `/vacuum` | `core-utility` | Routine task/archive cleanup |
| `/vacuum-protocol` | `vacuum-protocol` | Full Centrifuge Protocol with privacy audit |
