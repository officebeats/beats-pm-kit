# Test Coverage Analysis

**Date:** 2026-02-11
**Suite Status:** 73 tests | 37 passed | 21 failed | 11 errors | 4 skipped

---

## Current State Summary

The test suite (`system/tests/`) contains **12 test files** covering **~1,900 lines** of test code using Python's `unittest` framework. Of 25+ source files in `system/scripts/` and `system/utils/`, only **9 have any direct test coverage**. The remaining **16 source files have zero tests**.

### Pass/Fail Breakdown

| Category | Count |
|----------|-------|
| Passing | 37 |
| Failing | 21 |
| Errors (import/load failures) | 11 |
| Skipped (missing modules) | 4 |

Key failures include: broken imports in `test_core_setup.py` and `test_features.py` (11 errors), stale skill validation assertions (frontmatter checks), missing critical files (`KERNEL.md`, `SETTINGS.md`, `requirements.txt`), and an outdated `test_vacuum.py` that references a removed function.

---

## Coverage Map

### Source Files WITH Tests

| Source File | Test File | Function Coverage | Quality |
|-------------|-----------|------------------|---------|
| `scripts/core_setup.py` | `test_core_setup.py` | 5/10 (50%) | Low - over-mocked |
| `scripts/kernel_utils.py` | `test_kernel.py`, `test_features.py`, `test_regression.py` | 3/3 (100%) | Medium - missing edge cases |
| `scripts/gps_indexer.py` | `test_gps_indexer.py` | 2/2 (100%) | High - best test file |
| `scripts/vacuum.py` | `test_vacuum.py` | 2/7 (28%) | Low - outdated, happy-path only |
| `scripts/dispatch.py` | `test_queue.py` | 2/4 (50%) | Medium |
| `scripts/queue_worker.py` | `test_queue.py` | 2/4 (50%) | Medium |
| `utils/config.py` | `test_structure.py` | Indirect | Low - existence checks only |
| `scripts/universal_clipboard.py` | `test_core_components.py` | 2/5 (40%) | Low - always skipped |
| `scripts/context_loader.py` | `test_core_components.py` | 1/3 (33%) | Low - always skipped |

### Source Files WITHOUT Any Tests (16 files)

| Source File | LOC | Risk | Side Effects | Priority |
|-------------|-----|------|-------------|----------|
| `utils/filesystem.py` | 221 | Low | File I/O (read/write/copy/delete) | **P0 - Critical** |
| `utils/subprocess_helper.py` | 328 | Medium | Subprocess execution, downloads | **P0 - Critical** |
| `utils/platform.py` | 225 | Low | OS detection | **P0 - Critical** |
| `utils/memory.py` | 123 | Low | File I/O (decision log, session state) | **P1 - High** |
| `utils/ui.py` | 274 | Low | Terminal output | P2 - Medium |
| `scripts/update.py` | 191 | **High** | Git ops, file moves, migrations | **P0 - Critical** |
| `scripts/task_queue.py` | 126 | Medium | File I/O, dynamic imports | **P1 - High** |
| `scripts/enforce_structure.py` | 135 | Medium | Pattern-based file moves | **P1 - High** |
| `scripts/optimize_skills.py` | 116 | Medium | YAML parsing, writes skills.json | **P1 - High** |
| `scripts/db_bridge.py` | 145 | Low | SQLite reads, file writes | P2 - Medium |
| `scripts/vibe_check.py` | 205 | Low | Subprocess, file writes | P2 - Medium |
| `scripts/clipboard_bridge.py` | 279 | Medium | Subprocess (PowerShell/AppleScript) | P2 - Medium |
| `scripts/transcript_fetcher.py` | 117 | Low | SQLite, file writes | P3 - Low |
| `scripts/file_organizer.py` | 58 | Low | File moves | P3 - Low |
| `scripts/pulse.py` | 120 | Low | File reads only | P3 - Low |
| `scripts/librarian.py` | 57 | Low | File archive/index | P3 - Low |

---

## Proposed Improvements

### Priority 0: Foundational Utility Tests (Highest Impact)

These modules are imported by nearly every script. A bug here cascades everywhere.

#### 1. `utils/filesystem.py` — needs `test_filesystem.py`

This is the most critical gap. Every script depends on `ensure_directory()`, `read_file()`, `write_file()`, `copy_file()`, `delete_file()`, etc. Zero tests exist.

**What to test:**
- `ensure_directory()` — creates nested directories, idempotent on existing dirs, handles permission errors
- `read_file()` / `read_file_lines()` — reads UTF-8 content, returns empty string for missing files, handles encoding errors
- `write_file()` / `append_file()` — creates parent dirs, overwrites correctly, append adds to end
- `copy_file()` / `copy_directory()` — copies content and preserves structure, handles missing source
- `delete_file()` / `delete_directory()` — removes files, handles missing targets gracefully
- `list_files()` — glob patterns, empty directories, nested results
- `sanitize_filename()` — strips invalid chars, handles empty strings, preserves extensions
- `path_exists()` / `file_exists()` / `directory_exists()` — symlinks, missing paths, relative vs absolute

**Why:** A silent bug in `write_file()` or `delete_directory()` could destroy user data.

#### 2. `utils/subprocess_helper.py` — needs `test_subprocess_helper.py`

Wraps all external command execution. Untested subprocess calls are a reliability and security risk.

**What to test:**
- `run_command()` — success and failure cases, timeout behavior, shell flag differences
- `check_command_exists()` — installed vs missing commands
- `get_command_output()` — captures stdout correctly, handles stderr
- `run_python_script()` — correct Python executable resolution, exit code handling
- `run_command_silent()` — truly silent (no exceptions, no output)
- Input sanitization — ensure command arguments can't cause injection

#### 3. `utils/platform.py` — needs `test_platform.py`

Cross-platform correctness is load-bearing for clipboard, setup, and extension operations.

**What to test:**
- `get_system()` — returns correct platform identifier
- `is_windows()` / `is_macos()` / `is_linux()` — mutually exclusive, one is always True
- `get_python_executable()` — returns valid executable name
- `get_clipboard_command()` — returns platform-appropriate command
- `get_home_directory()` — returns existing directory
- `get_platform_info()` — returns complete dict with expected keys

#### 4. `scripts/update.py` — needs `test_update.py`

This is the **highest-risk untested file**. It runs `git stash`, `git pull`, moves files, deletes deprecated content, and calls three other scripts. A bug here can cause data loss.

**What to test:**
- `pre_flight_check()` — stashes dirty working tree, no-ops on clean tree
- `migration_scan()` — correctly identifies deprecated files, safely moves unknown files
- `verify_structure()` — calls core_setup correctly
- `restore_stash()` — pops stash only if one was created
- Error recovery — what happens if `git pull` fails mid-update?
- Zero Data Loss guarantee — files are moved, never deleted

### Priority 1: Core Logic Tests

#### 5. `scripts/enforce_structure.py` — needs `test_enforce_structure.py`

Moves files based on pattern matching. Incorrect patterns could misplace user documents.

**What to test:**
- `scan_and_migrate()` — pattern matching accuracy (PRD-*.md → specs, transcripts → meetings)
- Files that don't match any pattern are left in place
- Already-correctly-placed files are not moved
- `cleanup_legacy_folders()` — only removes truly empty directories

#### 6. `scripts/optimize_skills.py` — needs `test_optimize_skills.py`

Generates the skill index. A bad index means skills stop being discoverable.

**What to test:**
- `parse_frontmatter()` — valid YAML, missing frontmatter, malformed YAML
- `index_skills()` — produces valid JSON with correct structure per skill
- Skills with no triggers get legacy keyword extraction fallback
- KERNEL.md cleanup doesn't remove non-skill content

#### 7. `scripts/task_queue.py` — needs `test_task_queue.py`

The background task processing engine. Existing `test_queue.py` only tests `queue_worker.py`.

**What to test:**
- `TaskQueue.submit_job()` — creates valid JSON in PENDING directory
- `TaskQueue.process_next()` — picks oldest job, moves through states correctly
- `TaskQueue._execute_job()` — routes to correct handler per job type
- Concurrent submissions don't collide
- Failed jobs land in FAILED directory with error details

#### 8. `utils/memory.py` — needs `test_memory.py`

Manages persistent session state and decision logging.

**What to test:**
- `log_decision()` — appends correctly formatted entry to DECISION_LOG.md
- `read_recent_decisions()` — returns last N entries, handles empty log
- `get_session_memory()` / `save_session_memory()` — round-trips correctly
- Concurrent appends don't corrupt files

### Priority 2: Fix Existing Test Quality

#### 9. Fix `test_vacuum.py`

- Currently references a non-existent `manage_tiered_memory()` function
- Only tests 2 of 7+ functions (28% coverage)
- Add tests for: `ensure_dirs()`, `update_index()`, `clean_skeleton()`, `check_system_access()`, `check_git_safety()`
- Add error path tests (unreadable files, invalid markdown)

#### 10. Fix `test_core_setup.py`

- Currently errors on import (11 test errors)
- Over-mocked — tests verify mock calls, not actual behavior
- Missing tests for: `run_vibe_check()`, `run_skill_optimizer()`, `run_structure_enforcement()`, `main()`
- Add at least one integration test that creates real temp directories

#### 11. Fix `test_core_components.py`

- All 4 tests currently skip due to missing modules
- `calculate_hash()` test only checks one input — add empty string, unicode, large input
- stdout capture doesn't restore on exception — use `contextlib.redirect_stdout` instead
- Add transcript detection edge cases (mixed formats, false positives)

#### 12. Fix `test_regression.py`

- 21 failures due to stale command routing assertions
- `test_all_commands_route_correctly` references commands (`ux`, `ux discovery`, `ux wireframe`) that no longer map to existing skill directories
- Hardcoded counts (`assertGreaterEqual(len(...), 45)`) will drift over time
- Should dynamically check what exists rather than asserting fixed counts

#### 13. Strengthen `test_kernel.py`

- Missing edge cases for `check_anchor_rule()`: empty string, paths with `..`, special characters
- `check_privacy_rule()` only tests 2 violations — add mixed-case folder names, absolute paths
- `get_suggested_template()` only tests 3 of 7 known mappings

### Priority 3: Structural Improvements

#### 14. Add test configuration

There is no `conftest.py`, `pytest.ini`, or centralized test configuration. Each test file independently manages path resolution and module imports. This should be standardized:
- Add a `conftest.py` or shared test base class for consistent path setup
- Add a `pytest.ini` or `setup.cfg` for test discovery configuration
- Standardize the mocking patterns (pre-import mocking is fragile)

#### 15. Add integration tests with real file I/O

Most tests mock all file operations. While this makes tests fast, it means bugs in actual file handling go undetected. Add a small suite of integration tests that:
- Create real temp directories
- Write and read actual files
- Verify the full pipeline from input to output

#### 16. Add CI/CD test execution

There is no evidence of automated test execution (no GitHub Actions, no `.github/workflows/`). Setting up CI would catch regressions automatically.

---

## Estimated Impact

| Improvement | Tests Added | Risk Mitigated |
|-------------|-------------|----------------|
| P0: Utility module tests | ~40-50 | Foundation reliability |
| P0: update.py tests | ~10-15 | Data loss prevention |
| P1: Core logic tests | ~25-30 | Skill discovery, file organization |
| P2: Fix existing tests | ~20 fixes | 32 currently broken tests pass |
| P3: Infrastructure | 0 (structural) | Maintainability, CI automation |

**Current effective coverage: ~15-20% of source functions have meaningful tests.**
**Target after P0+P1: ~60-70% of source functions covered.**
