# AGENTS.md - Beats Agentic PM Harness Codex Adapter

> Thin runtime adapter. Source of truth: `.agent/`.

## Runtime Selection

Use the active runtime and its positively detected capabilities. Do not apply a permanent provider hierarchy or silently switch providers. Model defaults are inherited; local promotions require evaluation evidence. Promoted Codex commands: `/beats-comms`, `/beats-slack`, `/beats-teams`, `/boss`, `/create`, `/day`, `/deck`, `/find`, `/meet`, `/memory`, `/obsidian`, `/office-cli`, `/pack`, `/paste`, `/plan`, `/review`, `/sop`, `/track`, `/transcript`, `/update`, `/vacuum`, `/vibe`, `/week`.

Resolve the execution profile with `python system/scripts/model_policy.py resolve <command> --json`. Unknown capabilities fail closed, and missing Deep support must produce a visible downgrade warning.

## Startup

On a new Codex session:

1. If the user provides only the GitHub repo URL, clone/open the repo and run `python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>` from the repo root.
2. Read `SETTINGS.md` and `STATUS.md` first when they are relevant to the task.
3. Treat `.agent/` as the source of truth.
4. Resolve a command or skill with `python3 system/scripts/harness_registry.py resolve <target>`.
5. Read the selected workflow or skill, then load no more than five directly relevant candidate sources. Never load a candidate list wholesale or invoke a second router.
6. Keep identity, safety, and routing as a stable prefix; append dynamic evidence afterward and preserve deterministic tool order for cache reuse.
7. Use `compact_operator` narration during execution and the resolved final profile for the deliverable.
8. Translate unsupported primitives only when the active runtime reports the required capability.
9. Write durable outputs and verification traces into the standard local paths so runtime switching stays lossless.
## Token Efficiency & Bounded Context

Load and follow `.agent/rules/TOKEN_EFFICIENCY.md` for all retrieval, planning, and task execution. Use 2-tier bounded queries, preserve prompt prefix caching, and avoid full-file dumps.

## Action-First Responses
Load and follow `.agent/rules/ACTION_FIRST_OUTPUT.md` for every user-facing
response. Apply it to conversational presentation only. Safety requirements,
explicit user instructions, resolved response profiles, workflow contracts,
artifact schemas, and exact structured-output formats take precedence.

## Markdown Intake

When the user asks to convert a local file to Markdown, or a supported file
enters the intake staging lane, load `.agent/skills/markitdown/SKILL.md` and use
`system/scripts/markdown_intake.py`. Preserve the source file. Keep screenshots
on the existing visual path, and require explicit approval before networked or
billable conversion.

## Codex Browser First

When a task needs a browser for local apps, rendered UI checks, localhost demos, screenshots, click-through validation, or page inspection:

1. Use the Codex in-app Browser first.
2. Keep browser work contained in the Codex session whenever possible.
3. Start local servers with terminal commands when needed, then open and validate the URL in the Codex Browser.
4. Capture screenshots, DOM state, console warnings/errors, and interaction evidence through the Codex Browser whenever possible.
5. Do not default to macOS `open`, Chrome, Edge, Safari, Computer Use, or standalone Playwright before trying the Codex Browser.

Use an external browser only when there is a concrete reason: the user explicitly asks for it, the task needs the user's browser profile/cookies/extensions/SSO, the bug is browser-specific, the Codex Browser is unavailable or cannot reach the target after a reasonable attempt, or the workflow needs browser permissions/downloads/OS integration the Codex Browser cannot provide. State the reason briefly before using the external browser.

## Agent Bootstrap

When starting from a GitHub URL:

```bash
git clone <url>
cd beats-pm-kit
python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>
```

After bootstrap, route the user's first real PM input through `system/scripts/pm_decision_router.py` or the matching slash-command workflow.

## Slash Command Dispatch

If the user's message starts with `/command`:

1. Treat it as an explicit workflow invocation, not general conversation.
2. Resolve it with `system/scripts/harness_registry.py`; `CODEX_COMMANDS.md` is the human-readable index.
3. Read that workflow before doing deeper work.
4. Use the rest of the user's message as workflow input.
5. Follow the workflow even if a natural-language interpretation also seems possible.
6. If the command does not exist, say it is unknown and point the user to `/help`.

## Adapter Policy

Generated runtime folders such as `.codex/`, `.gemini/`, `.claude/`, and `.kilocode/` are local build artifacts and must stay ignored. Regenerate them with:

```bash
python system/scripts/sync_cli_adapters.py
python system/scripts/sync_codex_skill_adapters.py --output-dir <codex-skills-dir>
```
