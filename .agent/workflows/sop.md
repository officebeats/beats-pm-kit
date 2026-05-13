---
description: Capture, normalize, and maintain privacy-safe SOPs and runbooks for product management and consulting workflows.
---

> Compatibility Directive: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# SOP Workflow

Agent: SOP Librarian -> `sop-manager` skill

Use `/sop` when the user wants to create, revise, organize, or apply a standard operating procedure, runbook, checklist, or repeatable working pattern.

## Step 1: Load The SOP Contract

Read `.agent/skills/sop-manager/SKILL.md`.

If the request includes meeting/transcript content, also read `.agent/skills/meeting-synth/SKILL.md` only for extraction guidance.

If the request includes Jira or Confluence references, use read-only Atlassian fetch/search only for the explicitly provided or scoped references.

## Step 2: Detect Input Type

Auto-detect the user's input:

| Input | Detection signal | Handling |
| --- | --- | --- |
| Transcript or meeting summary | Quill/Teams/Zoom-style notes, speakers, timestamps, or meeting title | Extract decisions, operating rules, actors, inputs, outputs, and failure modes |
| Chat excerpt | Slack/Teams text, timestamps, message authors | Extract process commitments and links only from the scoped excerpt |
| Jira/Confluence context | Jira keys, Confluence URLs, release/version pages | Fetch read-only and summarize only what is needed for the SOP |
| Existing local doc | File path to `.md`, `.docx`, `.txt`, or existing runbook | Convert or normalize into SOP structure |
| Raw notes | Unstructured text, bullets, or verbal note | Turn into SOP draft with assumptions clearly marked |

Do not ask the user to classify the input if the content makes it clear.

## Step 3: Route The SOP Folder

Choose the local output lane:

| Domain | Route |
| --- | --- |
| Company product/process work | `6. SOPs/company/product-ops/...` |
| Consulting delivery work | `6. SOPs/consulting/client-delivery/...` |
| Reusable product-management methods | `6. SOPs/shared/product-management/...` |
| Reusable consulting methods | `6. SOPs/shared/consulting/...` |

Use domain-first paths, then SOP type, then product/process name.

## Step 4: Produce The Right Artifact Set

Create only the artifacts the request needs:

* Reusable SOP: the stable process.
* Runbook template: a fill-in version for future executions.
* Worked example runbook: a release/client/project-specific example.
* Checklist: a short execution checklist.
* Manual-send comms templates: only when they help the user operate the SOP.

Use `.agent/templates/sops/` templates as the reusable skeleton. Do not put real SOP content in `.agent/templates/sops/`.

## Step 5: Privacy And Source-System Guardrails

Before completion:

* Confirm real SOP content is under `6. SOPs/`.
* Confirm `git check-ignore` marks real SOP content ignored.
* Confirm only `.gitkeep` skeleton files under `6. SOPs/` are trackable.
* Do not send, post, draft, comment, transition, assign, upload, or update external systems.
* Report all source URLs or local source files used.

## Step 6: Confirm Output

Return:

* Local SOP file paths created or updated.
* Skeleton files created or updated.
* Source references used.
* Privacy validation result.
* Any open assumptions or follow-up work.
