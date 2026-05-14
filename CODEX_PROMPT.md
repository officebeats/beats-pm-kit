# CODEX_PROMPT.md -- Manual Codex Bootstrap Prompt

Use this prompt when a Codex session needs to be manually re-anchored to the Beats PM Kit.

You are working in the Beats PM Kit repository.

1. Read `AGENTS.md` first.
2. Read `SETTINGS.md` and `STATUS.md` when they exist; if `STATUS.md` is absent, use the relevant tracker files under `5. Trackers/`.
3. Treat `.agent/` as the source of truth for agents, workflows, skills, templates, and rules.
4. If my message starts with /command, treat it as an explicit workflow invocation.
5. Resolve it using CODEX_COMMANDS.md, then read the mapped `.agent/workflows/<command>.md` file before doing deeper work.
6. Load only the minimum `SKILL.md` files needed for the current task.
7. Translate Antigravity-only primitives into Codex-native actions instead of failing.
8. Keep durable outputs in the repo's standard folders so Codex and compatibility runtimes share state.

This checkout currently exposes 40 slash workflows through `CODEX_COMMANDS.md`.
