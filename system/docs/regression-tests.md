# 🛡️ FAANG-Grade Chaos & Regression Suite (v1.4.1+)

This suite now treats sanitized real-use workspaces as the primary release gate. Inventory and existence checks are lint signals unless they protect a real runtime contract.

Run the CI gate locally with:

```bash
python3 -B system/scripts/run_real_usecase_tests.py --ci
```

Fixtures live under `system/tests/fixtures/workspaces/` and should represent realistic PM inputs, expected artifact deltas, and scoped failure modes.

---

## Beats PM Kit Common Use-Case Regression Scenarios

These scenarios define the release gate for the core kit workflows after a safe update, merge, adapter sync, or local refactor.

### Test Scenario: Task Master Management Triage

**Test Objective:** Verify that `/track` and local triage automation preserve `5. Trackers/TASK_MASTER.md`, update only managed triage regions, and respect scoped task inputs.

**Starting Conditions:**
- `5. Trackers/TASK_MASTER.md` contains active, stale, overdue, and completed-looking tasks.
- At least one task detail file exists under `5. Trackers/tasks/`.
- No source-system connectors are required.

**User Role:** PM kit operator

**Test Steps:**
1. Run `python3 system/scripts/task_master_triage.py --apply` -> a triage report is generated and managed triage blocks are updated.
2. Run the same command with `--touched-task <ID>` -> only relevant scoped analysis is refreshed.
3. Invoke `/track` with a scoped pasted task update -> accepted changes route to local tracker files.

**Expected Outcomes:**
- Existing non-managed task content is preserved.
- Managed triage blocks identify overdue, stale, at-risk, and possibly complete tasks.
- Reports are written locally under the tracker/report paths.
- No Slack, Teams, Outlook, Calendar, Jira, or Confluence mutations occur.

**Automated Gate:** `system.tests.test_task_master_triage_real_use`

### Test Scenario: Agent Bootstrap From Repo URL

**Test Objective:** Verify that a user can provide only the GitHub URL and the agent can clone/open the repo, run one bootstrap command, and get a usable local workspace.

**Starting Conditions:**
- A clean clone of the public repo exists.
- Python 3 is available.
- No live connector credentials are required.

**Test Steps:**
1. Run `python3 system/scripts/bootstrap.py --agent --non-interactive --repo-url <url>`.
2. Verify ignored workspace folders, `.beats/`, generated adapters, promoted Codex skills, and privacy health output.
3. Confirm Obsidian guidance is suggest-only unless `--apply-obsidian` is explicitly provided.

**Expected Outcomes:**
- Bootstrap succeeds without requiring user knowledge of internal setup order.
- No external systems are mutated.
- Obsidian remains direct-vault and read/search/open-only.

**Automated Gate:** `system.tests.test_bootstrap`

### Test Scenario: Transcript Pulling And Preparation

**Test Objective:** Verify that transcript preparation normalizes date-stamped transcripts, maintains an idempotent manifest, and creates packets only for in-window unprocessed transcripts.

**Starting Conditions:**
- `3. Meetings/transcripts/` contains one in-window transcript and one out-of-window transcript.
- `3. Meetings/summaries/` contains an existing summary for one transcript.
- Connector imports may be unavailable.

**User Role:** PM kit operator

**Test Steps:**
1. Run `python3 system/scripts/transcript_pipeline.py prepare --business-days 10 --json --skip-import` -> packet output is returned for eligible transcripts.
2. Run the same command again -> already-ready packets are skipped.
3. Run prepare without `--skip-import` in a connector-limited environment -> unavailable sources are reported in the run report.

**Expected Outcomes:**
- Manifest entries are keyed by content hash and remain idempotent across repeated runs.
- Out-of-window transcripts are ignored.
- Existing summaries prevent duplicate packet creation.
- Unavailable connector imports are recorded as unavailable or skipped without failing the run.

### Test Scenario: Transcript Synthesis And Validation

**Test Objective:** Verify that generated summaries satisfy the transcript packet contract before transcripts are marked complete.

**Starting Conditions:**
- At least one prepared packet exists under `3. Meetings/reports/packets/`.
- The corresponding transcript exists and has a stable content hash.

**User Role:** PM kit operator or model runtime

**Test Steps:**
1. Create a summary with `Source Transcript`, `Transcript SHA256`, `Pipeline Run ID`, `Routed Updates`, and `Key Evidence` markers -> validation should pass.
2. Create a summary missing one required marker or the source hash -> validation should fail.
3. Run `python3 system/scripts/transcript_pipeline.py validate --run-id <RUN_ID> --json` for each case.

**Expected Outcomes:**
- Passing summaries update the manifest status to `validated`.
- Failing summaries update the manifest status to `validation_failed` with explicit error codes.
- Recent-meeting output uses only validated manifest-backed summaries.

### Test Scenario: Communication Intake Safety

**Test Objective:** Verify that `/beats-comms`, `/beats-slack`, and `/beats-teams` require explicit scope, preserve read-only source-system safety, and produce local manifests/reports.

**Starting Conditions:**
- The user provides a named read-only source window such as `slack: #team channel last 5 business days` or `teams: named chat last 3 days`.
- Connector availability may vary by runtime.

**User Role:** PM kit operator

**Test Steps:**
1. Invoke `/beats-comms` without a named read-only source window -> workflow asks for the missing window instead of broad-scanning.
2. Invoke with a named Slack or Teams source window -> saved transcripts and run reports are written locally.
3. Use a dense Slack window -> chunk planning is computed before reads proceed.

**Expected Outcomes:**
- No messages, replies, reactions, read-state changes, emails, calendar events, Jira comments, or Confluence edits are created.
- Platform manifests record successful local processing and duplicate skips.
- Dense windows are chunked, and capped chunks are reported rather than treated as complete.

### Test Scenario: Adapter And Documentation Integrity

**Test Objective:** Verify that generated runtime references match `.agent/` as the source of truth after merge and regeneration.

**Starting Conditions:**
- `.agent/workflows/` contains the canonical workflow set.
- Generated adapters exist at `AGENTS.md`, `CODEX_COMMANDS.md`, `GEMINI.md`, `CLAUDE.md`, and `.codex/rules.md`.

**User Role:** Maintainer

**Test Steps:**
1. Run `python3 system/scripts/sync_cli_adapters.py` -> generated adapter stubs are refreshed.
2. Run `python3 system/scripts/adapter_guard.py --mode check` -> generated files match canonical source.
3. Inspect `CODEX_COMMANDS.md` -> every `.agent/workflows/*.md` entry has a slash-command row.

**Expected Outcomes:**
- `AGENTS.md` remains present and authoritative.
- `CODEX_COMMANDS.md` includes every workflow and marks promoted guarded skills.
- Generated local runtime directories are not force-added to git.

### Test Scenario: Safe Update And Rollback

**Test Objective:** Verify that update migration does not delete active adapters and that rollback instructions remain valid after merge conflicts or failed validation.

**Starting Conditions:**
- A safety branch or tag points to the pre-update `HEAD`.
- Local work is captured in a stash that includes untracked files.
- A temp repo root is available for destructive migration tests.

**User Role:** Maintainer

**Test Steps:**
1. Run the updater migration scan in a temp root containing active adapters and unknown scratch files -> adapters remain in root, unknown files move to `0. Incoming/`.
2. Simulate a bad merge before push -> preserve the failed state on a branch, return to the working branch, and reset only after confirming the safety branch and stash exist.
3. Re-run unit tests and adapter guard after recovery.

**Expected Outcomes:**
- `AGENTS.md`, `CODEX_COMMANDS.md`, `CODEX_PROMPT.md`, `CLAUDE.md`, and `GEMINI.md` are not deleted or moved.
- Deprecated root files can still be cleaned safely.
- Rollback uses the recorded safety branch and stash; destructive reset is not performed without confirming both.

---

## 🌪️ Chaos Engineering Benchmarks

| Category             | Metric          | Failure Threshold                        |
| :------------------- | :-------------- | :--------------------------------------- |
| **Recursive Depth**  | Loop Detection  | Rejected after 3 hops.                   |
| **Syntax Injection** | Table Escape    | 0% breakage of Markdown schema.          |
| **Naming Collision** | Resolution Rate | > 98% accuracy on similar entities.      |
| **Graceful Failure** | System Recovery | Manual re-read / self-heal on file lock. |

---

## 🧪 Edge Case Scenarios

### 1. Semantic Collision (The "Which One?" Test)

| ID          | Title                 | Input Signal                                                            | Expected Handling                                                         |
| :---------- | :-------------------- | :---------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **EDGE-01** | **Product Ambiguity** | "Login is broken on the app." (Folders: `mobile-ios`, `mobile-android`) | Prompts user for platform selection or checks recent history for context. |
| **EDGE-02** | **Entity Clash**      | "Mark said it's fine." (Team: `Mark S.`, `Mark D.`)                     | Checks project affiliation or prompts: "Which Mark? (S. or D.)".          |
| **EDGE-03** | **Nickname Overload** | "The Big Kahuna wants it."                                              | Fails gracefully -> Logs under `Unknown Stakeholder` + flags for Triage.  |

### 2. Syntax Malformation (The "Markdown Killer")

| ID          | Title                | Input Signal                                             | Expected Handling                                        |
| :---------- | :------------------- | :------------------------------------------------------- | :------------------------------------------------------- | ----- | ----- | ------ | ------- | ------------------------------------------------------------------------- |
| **EDGE-04** | **Pipe Injection**   | `Bug: User name                                          | with                                                     | extra | pipes | breaks | tables` | Sanitizes pipes or uses HTML entity `&#124;` to prevent table corruption. |
| **EDGE-05** | **Backtick Nesting** | ` Task: review this code: ```javascript var x = 1 ```  ` | Prevents code block bleeding into the tracker structure. |
| **EDGE-06** | **Unclosed Formats** | `Feature Request: *Bold text that never ends...`         | Self-closes formatting tags before writing to file.      |

### 3. State & Race Conditions

| ID          | Title                | Input Signal                                                         | Expected Handling                                                                    |
| :---------- | :------------------- | :------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| **EDGE-07** | **Concurrent Write** | 2 agents writing to `ACTION_PLAN.md` within 50ms.                    | File-level atomic write or retry-after-lock pattern.                                 |
| **EDGE-08** | **Recursive Loop**   | Agent A yields to Agent B, which contains a rule to trigger Agent A. | "Depth Counter" trigger: Halt and log "Critical Orchestration Error: Loop Detected". |
| **EDGE-09** | **Deleted Context**  | Tracking a bug for a Product whose `.md` file was just deleted.      | Reports "Context Missing" -> Creates `vault/products/RECOVERED-[Name].md` baseline.  |

---

## ⚡ Concurrency & Stress Scenarios

| ID            | Load Type           | Stress Pattern                                             | Validation                                                                        |
| :------------ | :------------------ | :--------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| **STRESS-01** | **Burst Ingestion** | Input 50+ lines of raw Slack chat containing 10+ bugs.     | 10+ unique IDs generated; zero loss of context.                                   |
| **STRESS-02** | **Deep Tree Scan**  | Force a `#status` command while `vault/` has 1,000+ files. | Validates lazy-loading protocol (KERNEL.md) performance; avoids context overflow. |
| **STRESS-03** | **Big Binary Drop** | Drop a 1GB MKV file in `00-DROP-FILES-HERE-00/`.           | Graceful rejection/triage: "Skipping large binary file; metadata scan only."      |

---

## 🏁 Verification Script (`system/scripts/chaos_runner.py`)

This script automates the validation of the above.

1. **Initialize Chaos**: Create 2 similarly named products and 2 similar stakeholders.
2. **Inject Malformed Input**: Send `/bug` commands with table-breaking characters.
3. **Trigger Concurrent Agents**: Simulate 3 handoffs in a single turn.
4. **Audit Structural Integrity**: Run `grep` for broken pipes or unassigned `null` entities.
