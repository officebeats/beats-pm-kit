"""
Adapter guard for Codex-first cross-runtime synchronization.

Modes:
- check: CI-safe verification without mutating tracked files or local Codex home
- fix: local sync path for hooks and manual maintenance
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED_REPO_FILES = [
    "AGENTS.md",
    "CODEX_COMMANDS.md",
    "CODEX_PROMPT.md",
    ".codex/rules.md",
    ".claude/CLAUDE.md",
]
PY_COMPILE_FILES = [
    "system/utils/command_registry.py",
    "system/utils/stdio.py",
    "system/scripts/beats.py",
    "system/scripts/codex_doctor.py",
    "system/scripts/codex_setup.py",
    "system/scripts/feature_inventory.py",
    "system/scripts/sync_cli_adapters.py",
    "system/scripts/sync_codex_skill_adapters.py",
    "system/scripts/adapter_guard.py",
    "system/scripts/install_git_hooks.py",
    "system/tests/test_adapter_guard.py",
    "system/tests/test_codex_adapter.py",
    "system/tests/test_codex_skill_adapters.py",
]
TEST_MODULES = [
    "system.tests.test_adapter_guard",
    "system.tests.test_codex_adapter",
    "system.tests.test_codex_skill_adapters",
]


def run(cmd: list[str], *, quiet: bool = False, cwd: Path | None = None):
    """Run a command from repo root."""
    workdir = cwd or ROOT
    if quiet:
        result = subprocess.run(
            cmd,
            cwd=workdir,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return result

    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=workdir, check=True, text=True)


def sync_repo_adapters():
    """Regenerate tracked adapter artifacts."""
    run([sys.executable, "system/scripts/sync_cli_adapters.py"])


def _copy_for_generation(temp_root: Path):
    """Copy only the repo surfaces needed to regenerate adapters."""
    ignore = shutil.ignore_patterns(
        ".git",
        ".pytest_cache",
        "__pycache__",
        "tmp",
        ".omx",
        "0. Incoming",
        "1. Company",
        "2. Products",
        "3. Meetings",
        "4. People",
        "5. Trackers",
        "6. SOPs",
        "7. Partners",
        "8. Clients",
        "node_modules",
    )
    shutil.copytree(ROOT, temp_root, symlinks=True, ignore=ignore, dirs_exist_ok=True)


def assert_repo_generated_files_current():
    """Fail if adapter regeneration would change generated files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir) / "repo"
        _copy_for_generation(temp_root)
        run([sys.executable, "system/scripts/sync_cli_adapters.py"], cwd=temp_root, quiet=True)

        drifted = []
        for relative in GENERATED_REPO_FILES:
            current = ROOT / relative
            regenerated = temp_root / relative
            if not current.exists() or not regenerated.exists():
                drifted.append(relative)
                continue
            if not filecmp.cmp(current, regenerated, shallow=False):
                drifted.append(relative)

        if drifted:
            joined = ", ".join(drifted)
            raise SystemExit(
                "Generated adapter drift detected. Run "
                "`python system/scripts/adapter_guard.py --mode fix` and commit the result. "
                f"Drifted files: {joined}"
            )


def sync_codex_skill_adapters(output_dir: str | None = None, *, quiet: bool = False):
    """Regenerate promoted Codex skill adapters."""
    cmd = [sys.executable, "system/scripts/sync_codex_skill_adapters.py"]
    if output_dir:
        cmd.extend(["--output-dir", output_dir])
    run(cmd, quiet=quiet)


def compile_sources():
    """Compile adapter-related Python files."""
    run([sys.executable, "-m", "py_compile", *PY_COMPILE_FILES])


def run_tests():
    """Run the adapter-focused regression suite."""
    run([sys.executable, "-m", "unittest", *TEST_MODULES, "-v"])


def assert_repo_generated_files_clean():
    """Fail if regenerating adapters changed tracked files."""
    run(["git", "diff", "--exit-code", "--", *GENERATED_REPO_FILES])


def main():
    parser = argparse.ArgumentParser(description="Verify or sync runtime adapters")
    parser.add_argument(
        "--mode",
        choices=["check", "fix"],
        default="check",
        help="check is CI-safe; fix syncs local Codex skills too",
    )
    parser.add_argument(
        "--codex-output-dir",
        default=None,
        help="Override Codex skill output directory",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip unit tests",
    )
    parser.add_argument(
        "--skip-clean-check",
        action="store_true",
        help="Skip git diff verification for generated repo files",
    )
    args = parser.parse_args()

    if args.mode == "fix":
        sync_repo_adapters()
    else:
        assert_repo_generated_files_current()

    temp_dir = None
    codex_output_dir = args.codex_output_dir
    quiet_codex_sync = False

    if args.mode == "check" and codex_output_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        codex_output_dir = temp_dir.name
    elif args.mode == "fix":
        quiet_codex_sync = False

    sync_codex_skill_adapters(codex_output_dir, quiet=quiet_codex_sync)
    compile_sources()

    if not args.skip_tests:
        run_tests()

    if args.mode == "fix" and not args.skip_clean_check:
        assert_repo_generated_files_clean()

    if temp_dir is not None:
        temp_dir.cleanup()

    print("Adapter guard passed.")


if __name__ == "__main__":
    main()
