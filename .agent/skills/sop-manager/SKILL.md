---
name: sop-manager
description: Create, normalize, organize, and validate privacy-safe SOPs, runbooks, checklists, and worked examples for product management and consulting workflows. Use for `/sop`, SOP capture from transcripts or docs, release/process runbooks, and local-only operating procedures.
---

# SOP Manager

## Storage Contract

Real SOP content goes under `6. SOPs/` and is local-only.

Tracked toolkit skeletons go under:

```text
.agent/templates/sops/
.agent/workflows/sop.md
.agent/skills/sop-manager/SKILL.md
```

Never store sensitive, stakeholder-specific, customer-specific, or meeting-specific SOP content in `.agent/` templates.

## Folder Taxonomy

Use domain-first routing:

```text
6. SOPs/
  company/
    product-ops/
      release-management/
  consulting/
    client-delivery/
  shared/
    product-management/
    consulting/
```

Extend this structure only when the new folder is meaningful for repeated use.

## SOP Artifact Types

Choose the smallest useful artifact set:

* `sop.md`: stable, ticket/client/project-agnostic operating procedure.
* `runbook-template.md`: fill-in template for the next execution.
* `example-runbook.md`: specific worked example that may contain sensitive details.
* `checklist.md`: operational checklist for repeated execution.
* `comms-template.md`: manual-send message draft.

## Workflow

1. Identify audience: product manager, program manager, consultant, CTT/release team, or leadership operator.
2. Extract the stable process from the source material.
3. Separate reusable process from one-time example details.
4. Route the SOP to `6. SOPs/<domain>/<type>/<process>/`.
5. Use templates from `.agent/templates/sops/` when creating new artifacts.
6. Keep source systems read-only.
7. Validate privacy with `git check-ignore` for real SOP content.
8. Report file paths, sources, and any assumptions.

## Source-System Rules

Allowed:

* Read local files.
* Read scoped transcript/meeting/chat excerpts.
* Read explicitly provided Jira or Confluence references.
* Use source links in the SOP for traceability.

Prohibited:

* Sending or drafting Slack/Teams/email messages unless explicitly asked for local copy text only.
* Editing Jira or Confluence.
* Adding comments, worklogs, transitions, assignments, or page updates.
* Uploading files or transmitting sensitive data.

## Quality Bar

Each reusable SOP must include:

* Purpose.
* When to use.
* Inputs.
* Roles.
* Workflow steps.
* Output artifacts.
* Guardrails.
* Validation checklist.
* Template/runbook relationship when applicable.

Each runbook template must include:

* Fill-in placeholders.
* Source links.
* environment/context fields when relevant.
* Result capture.
* Closeout checklist.

Each worked example must clearly say:

* It is an example, not the reusable SOP.
* It may contain local-only sensitive detail.
* It should remain under `6. SOPs/` and ignored by git.

## Privacy Validation

For every real SOP content file, run:

```bash
git check-ignore -v "<path>"
```

For every skeleton `.gitkeep` file intended to preserve folder structure, confirm it is not ignored:

```bash
git check-ignore -v "<path-to-.gitkeep>"
```

If a real SOP file is not ignored, stop and fix `.gitignore` before reporting completion.
