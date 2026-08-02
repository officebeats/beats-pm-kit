---
name: weekly-synth
description: Weekly rollup and planning with critical commitment preflight.
priority: P0
triggers:
  - "/week"
---

# Weekly Synth

Use this skill for weekly planning, boss-readiness, and commitment rollups.

## Required Preflight

Before synthesizing, run the critical commitment preflight:

```bash
python3 system/scripts/critical_commitment_refresh.py plan --mode week --json
python3 system/scripts/critical_commitment_refresh.py rank --mode week --json
```

If the plan reports `should_pause_for_user: true`, stop and show the user:
- What integration failed.
- Why the skipped source puts commitments at risk.
- The recommended fix.
- Safe options: reconnect/configure, paste/export for this run, skip once, or disable from defaults.

Do not continue with degraded source coverage until the user explicitly chooses a path.

## Source Policy

- Use manifest-backed named read-only source windows by default for Slack, Outlook, Calendar, Teams, transcripts, Quill, Granola, Obsidian, Atlassian, and agent memory.
- Enabled, healthy TWG may supplement the named Atlassian window with one bounded personal work rollup under `.agent/rules/TWG_READ_ONLY.md`. Rovo/native reads remain primary for exact Jira or Confluence evidence.
- Backward source windows default to the last 5 business days and may shorten only when the chat/source manifest or command-run manifest shows a successful prior run for the same source/window. Calendar includes the last 5 business days of changes plus forward lookahead for upcoming active-workstream gates.
- Treat third-party systems as read-only. Never send, draft, reply, react, schedule, create, assign, transition, comment, upload, patch, delete, or move third-party state unless the user explicitly confirms that exact mutation in the current turn.
- Use parallel agents for independent source reads and synthesis passes when the runtime supports them.
- Keep shared writes serialized: Markdown task updates, source manifests, generated indexes, and final consolidation.
- Stay within the 90-second wall-clock budget where possible. Prefer visible partial source gaps over silent skips.

## Synthesis Rules

- Anchor the week around Friday boss readiness.
- Leadership and external commitments outrank generic stale work.
- Completed outcomes stay visible with completion date/source.
- Implied completions become confirmation questions.
- Create or update `5. Trackers/WEEKLY_PLAN.md` with workstream-first sections.
- User-facing task and workstream descriptions must use `display_title` plus source provenance, not hard IDs. Keep internal and source IDs only in local links, metadata, or an `Agent refs` line.
- Evidence lines use this shape: `[Task/workstream title]; started from [initial source label] on [date]; latest progress from [latest source label] on [date].`

## Weekly Output Shape

```markdown
# Weekly Plan: [Date Range]

## Outcomes
- [Outcome or committed result] by [date/gate]
  - Evidence: [task/workstream title; started from initial source on date; latest progress from latest source on date]

## Completed Outcomes
- [Completed item]
  - Completed: [date/source]

## Workstreams

### Workstream Title
- Latest outcome: [result, decision, or state]
  - Evidence: [task/workstream title; started from initial source on date; latest progress from latest source on date]
- Completed: [done item or "None newly confirmed"]
  - Completed: [date/source]
- Open items: [count or short list]
  - [Owner] - [action] by [date/gate], from [source]
- Recommended next 3:
  - [Action 1]
  - [Action 2]
  - [Action 3]

## Source Gaps / Questions
- [integration gap, stale workstream, or possibly-complete item]
```
