---
title: Track Product Work
description: Capture, triangulate, and manage product work in canonical human-readable Markdown task notes.
---

# Track Product Work

`/track` turns current evidence into readable task and workstream state. Individual Markdown task notes are authoritative; Task Master and other visualizations are generated views.

## Workflow

1. **Check upgrade compatibility**
   - For a kit upgraded from an earlier release, run `python3 system/scripts/upgrade_compat.py --json` before changing local notes.
   - Stop on duplicate IDs, broken task links, ambiguous titles, or other blockers.
   - Apply safe title migration only through the backed-up `--apply` path.

2. **Choose the fast or full lane**
   - One pasted message or transcript excerpt: run `task_intake_fast.py` immediately.
   - Multi-source refresh, daily reconciliation, or explicit full triage: continue through the remaining steps.

3. **Collect the core evidence**
   - Use configured, named read-only source windows for Granola, Quill, Outlook, Teams, and Slack.
   - Include local meeting transcripts and previously archived evidence.
   - Archive raw evidence before interpretation and preserve timestamps, participants, and source links.
   - Never broad-scan accounts, change unread state, send messages, or mutate source systems.
   - **Completeness contract** (hard requirements):
     - Enumerate the ENTIRE source window via pagination (`@odata.nextLink` or the source's equivalent) before triage — never stop at one page.
     - For every relevant item, fetch the FULL body/transcript verbatim into `0. Incoming/` with sender, date, participants, and source links. Previews are triage hints only, never the record.
     - `$select`/`$top` tune transport only; they never justify skipping items.
     - If a source fails mid-window, record the exact gap (source + date range) in the evidence packet instead of silently continuing.

4. **Triangulate before creating work**
   - Search existing task notes and workstreams first.
   - When past context is missing or conflicting, run `/find <specific question>` once and verify any semantic-memory lead against dated Markdown.
   - Merge repeated signals from meetings, chats, and email under the same task or workstream.
   - Create a new workstream only when >=2 tasks would link to it OR it is a boss ask; otherwise attach the task to an existing lane or mark it `needs-triage`.
   - Record the first source, latest source, decision changes, blockers, and completion evidence.
   - If one source fails, label the gap and use cached evidence only for that source.

5. **Write canonical task notes**
   - Create or update a descriptive file under `5. Trackers/tasks/`.
   - Keep the internal ID in frontmatter and use a human-readable filename, title, and H1 for new notes.
   - Infer missing fields when reasonable and list them in `inferred_fields`.
   - Preserve ambiguous signals as `needs-triage` rather than dropping them.

6. **Regenerate navigation**
   - Run `python3 system/scripts/task_store.py rebuild`.
   - Refresh workstream summaries from the task notes and evidence.
   - Treat `TASK_MASTER.md` as navigation, not a competing database.

7. **Report the result**
   - Show readable workstreams first, then tasks created or updated, evidence used, inferred fields, source gaps, and unresolved questions.
   - Keep IDs in links or an `Agent refs` line only.
   - Emit the preview link for the primary updated file: `python3 system/scripts/preview_link.py <file> --open --json`.

8. **Offer Obsidian without blocking**
   - Run `python3 system/scripts/obsidian_bridge.py guide --json` after local task work.
   - If `should_prompt` is true, show the exact kit folder, task folder, Task Master, and guide paths.
   - Markdown remains canonical whether or not Obsidian is installed.

Optional integrations such as Trello are not part of `/track`. They can consume accepted Markdown state only through an explicitly enabled `/pack` workflow.
