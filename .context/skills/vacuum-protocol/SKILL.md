---
name: vacuum-protocol
description: "Execute the full Centrifuge Protocol to keep the brain lean, private, and organized. Use when the user requests system optimization, task archiving, hierarchical integrity auditing, or explicitly triggers /vacuum, /archive, or /cleanup. Do NOT use to archive active code or configurations."
source_tool: antigravity
source_path: .agents\skills\vacuum-protocol\SKILL.md
imported_at: 2026-04-25T21:29:42.830Z
ai_context_version: 0.9.2
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Vacuum Protocol Skill

## Core Protocol

You operate under the `System Optimizer` identity. Your sole purpose is to process the local runtime environment to ensure maximum performance while maintaining strict privacy boundaries.

1.  **Identity Load**: Read `references/rules.md` (if it exists) to verify base exclusions. (Note: currently defer to `.gitignore` status).
2.  **Audit & Cleanup Execution**: Execute the python script located at `system/scripts/vacuum.py` using `python system/scripts/vacuum.py`. Wait for the script to finish running.
3.  **Transcripts Processing**: Ensure that any un-synthesized transcripts located in `0. Incoming/` or `3. Meetings/transcripts` are routed to the `meeting-synth` skill.
4.  **Archive Phase**: Scan `5. Trackers/` for any lines starting with `- [x]`. Programmatically append these to `5. Trackers/archive/`.
5.  **Status Reporting**: Output a summary table showing:
    - How many items were archived.
    - Which files were cleaned up.
    - The boolean PASS/FAIL states for Integrity, Privacy, and Access sweeps.

## Execution Blockers to Avoid

- NEVER delete active content from the track or logs; strictly use system-level `archive_` behaviors.
- ALWAYS verify `.gitignore` integrity to ensure Folders 1-5 remain protected.

## Skill Hierarchy

| Command | Skill | Purpose |
|---------|-------|---------|
| `/vacuum` | `core-utility` | Routine task/archive cleanup |
| `/vacuum-protocol` | `vacuum-protocol` | Full Centrifuge Protocol with privacy audit |
