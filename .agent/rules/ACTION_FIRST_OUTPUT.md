# Action-First Output Policy

Use this policy for every user-facing conversational response. It changes how an
answer is presented, not how the kit routes commands, retrieves context, writes
artifacts, or executes workflows.

## Default Response Shape

1. Lead with the answer, completed outcome, or smallest useful next action. Do
   not begin with an announcement about what you are going to say or do.
2. Use a numbered list when the reader must perform multiple steps. Keep each
   step bounded, and keep any single list to five items or fewer. Split longer
   material into ranked groups such as `Do now` and `Later`.
3. Finish the requested topic before surfacing a separate concern. Omit
   tangents that do not change the result or the reader's next action.
4. On continued work, state the current result or position so the reader does
   not have to reconstruct it from earlier turns. Make completed work visible.
   State failures matter-of-factly: what failed, the evidence or cause when
   known, and the next corrective action. Give time estimates only when useful
   and grounded; use concrete ranges instead of vague language.
5. If work remains, end with one concrete next action. If the request is fully
   complete, end after the result without a generic recap, invitation, or
   closing pleasantry.

Use short headings when they materially improve scanning. Brevity must not
remove evidence, required context, uncertainty, or the answer itself.

## Precedence and Exceptions

Apply higher-priority requirements before this response style, in this order:

1. Runtime safety, privacy, approval, and destructive-action requirements.
2. The user's explicit request for a format, tone, depth, explanation, or
   walkthrough.
3. Canonical workflow contracts, templates, external-communication rules, and
   durable artifact schemas.
4. Exact machine-readable, CLI, API, code, table, or structured-output formats.
5. Harness-required response profiles, progress updates, questions, citations,
   and completion directives.

When a higher-priority requirement conflicts with this policy, preserve the
required content and apply the action-first shape only to the surrounding
conversation. Never rewrite a workflow artifact, command result, or structured
payload merely to satisfy this style.

## Compatibility Boundary

- This is the default response style; it has no slash command, session flag, or
  runtime hook.
- It does not change the PM Decision Router, harness registry, context scoring,
  retrieval, task ledgers, source-system permissions, or workflow execution.
- Existing workflow-specific response profiles and structures remain
  authoritative.

## Acknowledgement

This independently worded policy is inspired by the action-first response
principles in the MIT-licensed
[`i-have-adhd`](https://github.com/ayghri/i-have-adhd) project. The upstream
plugin, hooks, and executable code are not vendored here.
