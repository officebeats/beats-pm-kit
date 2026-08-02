# Atlassian Teamwork Graph CLI — Optional Read-Only Policy

TWG is an optional context accelerator. It is not a required dependency, a replacement for local trackers, or permission to broaden a source window.

## Authority

1. Accepted local task/workstream artifacts remain the operating source of truth.
2. Use runtime Atlassian/Rovo reads first for exact Jira keys, Confluence URLs, JQL/CQL, and native objects.
3. Use TWG only for a bounded personal rollup, cross-product relationship context, or dependency discovery that can change status, risk, ownership, a decision, or the next action.

Search results and graph proximity are candidate evidence. Hydrate the small set of native anchors that materially affect the answer.

## Activation and bounds

- TWG must be enabled in `SETTINGS.md` and pass `python3 system/scripts/twg_health.py --pretty`.
- Its absence does not block work when Rovo, referenced Atlassian artifacts, or local evidence are sufficient.
- Setup, login, update, upkeep, and Bitbucket configuration require separate user authorization.
- For `/day`, `/week`, `/boss`, or an explicit live `/track` refresh, keep the named time window and request compact, ranked output with at most five items per section.
- Inspect compact output first. Full output is a last resort.
- Do not include viewed activity by default. Viewing, mentioning, commenting, or graph proximity does not prove ownership, authority, approval, dependency, or commitment.
- Never run tenant-wide fuzzy searches during `/beats-comms` or referenced-only Atlassian intake.
- Stop after the first policy denial or the second identical auth, ACL, contract, or backend error.

## Mutation and privacy boundary

The kit's TWG mode is read-only even when OAuth scopes are broader. Never create, edit, assign, transition, comment, link, move, archive, delete, upload, change permissions, or otherwise mutate a connected product without an explicit current-turn request and a workflow that permits it.

Never read, print, retain, or summarize tokens, OAuth state, user/cloud IDs, tenant details, or TWG temporary output. Save only the minimum cited conclusion or accepted source reference. Label TWG findings as live external context until reconciled with the matching local workstream or task.
