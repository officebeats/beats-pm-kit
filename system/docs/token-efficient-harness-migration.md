# Token-Efficient Harness Migration Report

## Safe base

- The original recovery checkout was retained untouched.
- The recovery checkout is on the older `v10.15.0` history, 89 commits ahead and 99 behind `origin/main`; Git reports no merge base after upstream history replacement.
- Implementation was performed in a separate temporary worktree.
- Branch: `codex/token-efficient-agentic-harness` from `origin/main` (`v11.2.0`, commit `6d0707c`).
- `git pull --ff-only origin main` completed before edits and reported that the branch was current.
- Clean baseline ran 270 tests with 4 intentional skips. One runner-only error was present because `codex_doctor.py` assumed `sys.stdout.encoding`; the implementation now uses a safe optional attribute lookup.
- Final validation ran 304 tests with the same 4 intentional skips; all tests passed. Registry, generated-doc, cross-runtime adapter, offline evaluation, and privacy guards also passed.

## Local recovery changes compared with v11.2.0

| Recovery change | Migration decision |
| --- | --- |
| Native Quill MCP transcript staging and `--quill-mode native-mcp` | Replayed and shortened for runtime-neutral bounded context. Default bridge/fallback behavior remains compatible. |
| Optional read-only TWG policy, sanitized health probe, settings, and daily/weekly/boss/task integration | Replayed against the newer v11.2.0 skills. Rovo/native exact reads remain primary; TWG cannot widen scopes or mutate sources. |
| PowerPoint corruption guard | Replayed as a writer-neutral requirement: prefer `python-pptx` for native compatibility and validate any alternative OpenXML output. |
| Older task/workstream prose | Replaced upstream by the leaner v11.2.0 task-manager contract. Only the still-relevant TWG boundary was merged. |
| Generated `CODEX_COMMANDS.md` edit | Not replayed directly; it is regenerated from schema v3. |
| Recovery README additions | Folded into the new harness/TWG documentation rather than copied verbatim. |
| `.agent/workflows/testapi.md` | Intentionally not promoted or replayed. It is a company-specific local API workflow without a generic routed PM use case, so it remains available only in the recovery checkout. |
| `.claudian/` session state | Not replayed; local generated runtime state is outside the core and must stay ignored. |
| `outputs/` documents and partner artifacts | Not replayed; private/local deliverables remain in the recovery checkout. |
| Local partner-specific build tooling under `tools/` | Not replayed; it is tied to local partner artifacts and is not harness infrastructure. |

No recovery artifact was deleted or overwritten.

## Static efficiency result

Token counts use the stable UTF-8 byte estimate used by `harness_registry.py`.

| Measure | Baseline | Candidate | Change |
| --- | ---: | ---: | ---: |
| Five largest routed skill entrypoints | 42,294 | 2,640 | -93.8% |
| All skill entrypoints | 95,526 | 56,460 | -40.9% |
| Complete discovery registry | not previously bounded | 715 | within 2,500 budget |
| Largest runtime bootstrap | 1,121 before refactor | 1,038 | -7.4%; within 1,500 budget |
| Largest initial command context | previously reported 14,000-36,000 hot paths | 3,800 workflow/bootstrap estimate | at least -72.9%; within 6,000 budget |

The original detailed guides remain available under each refactored skill's `references/full-guide.md`; this is progressive disclosure, not deletion of capability.

Static context reduction does not prove whole-trajectory savings. The telemetry, paired acceptance corpus, cold/warm split, and bounded optimizer are now implemented so Antigravity, Codex, and Claude trials can prove the 25% median trajectory target without hiding per-scenario regressions. Live provider trials are never run or promoted implicitly.
