"""Adapter and privacy guard for cross-runtime synchronization.

Modes:
- check: CI-safe verification without mutating local Codex home
- fix: local sync path for hooks and manual maintenance
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.root_policy import generated_or_local_prefixes

GENERATED_REPO_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "CODEX_COMMANDS.md",
    ".agent/MANIFEST.json",
    ".agent/ARCHITECTURE.md",
    ".agent/rules/ROUTING.md",
    "system/docs/runtime-compatibility.md",
]
FORBIDDEN_TRACKED_PREFIXES = list(generated_or_local_prefixes())
PY_COMPILE_FILES = [
    "system/utils/command_registry.py",
    "system/utils/root_policy.py",
    "system/utils/stdio.py",
    "system/scripts/beats.py",
    "system/scripts/bootstrap.py",
    "system/scripts/codex_doctor.py",
    "system/scripts/codex_setup.py",
    "system/scripts/feature_inventory.py",
    "system/scripts/generate_registry_docs.py",
    "system/scripts/detect_runtime.py",
    "system/scripts/model_policy.py",
    "system/scripts/model_eval.py",
    "system/scripts/obsidian_bridge.py",
    "system/scripts/root_cleaner.py",
    "system/scripts/sync_cli_adapters.py",
    "system/scripts/sync_codex_skill_adapters.py",
    "system/scripts/command_integrity.py",
    "system/scripts/context_router.py",
    "system/scripts/context_store.py",
    "system/scripts/context_checkpoint.py",
    "system/scripts/knowledge_compiler.py",
    "system/scripts/harness_registry.py",
    "system/scripts/harness_telemetry.py",
    "system/scripts/harness_optimizer.py",
    "system/scripts/twg_health.py",
    "system/scripts/critical_commitment_refresh.py",
    "system/scripts/markdown_title_guard.py",
    "system/scripts/agent_memory_health.py",
    "system/scripts/personal_memory.py",
    "system/scripts/pack_manager.py",
    "system/scripts/task_store.py",
    "system/scripts/upgrade_compat.py",
    "system/scripts/run_real_usecase_tests.py",
    "system/scripts/adapter_guard.py",
    "system/scripts/privacy_guard.py",
    "system/scripts/install_git_hooks.py",
    "system/tests/test_adapter_guard.py",
    "system/tests/test_harness_registry.py",
    "system/tests/test_harness_acceptance.py",
    "system/tests/test_context_router.py",
    "system/tests/test_context_store.py",
    "system/tests/test_context_checkpoint.py",
    "system/tests/test_knowledge_compiler.py",
    "system/tests/test_harness_telemetry.py",
    "system/tests/test_harness_optimizer.py",
    "system/tests/test_twg_health.py",
    "system/tests/test_command_integrity.py",
    "system/tests/test_codex_adapter.py",
    "system/tests/test_codex_skill_adapters.py",
    "system/tests/test_critical_commitment_refresh.py",
    "system/tests/test_markdown_title_guard.py",
    "system/tests/test_registry_docs.py",
    "system/tests/test_runtime_detection.py",
    "system/tests/test_model_policy.py",
    "system/tests/test_model_eval.py",
    "system/tests/test_model_neutrality.py",
    "system/tests/test_legacy_cli.py",
    "system/tests/test_obsidian_bridge.py",
    "system/tests/test_pack_manager.py",
    "system/tests/test_personal_memory.py",
    "system/tests/test_task_store.py",
    "system/tests/test_upgrade_compat.py",
]
TEST_MODULES = [
    "system.tests.test_adapter_guard",
    "system.tests.test_harness_registry",
    "system.tests.test_harness_acceptance",
    "system.tests.test_context_router",
    "system.tests.test_context_store",
    "system.tests.test_context_checkpoint",
    "system.tests.test_knowledge_compiler",
    "system.tests.test_harness_telemetry",
    "system.tests.test_harness_optimizer",
    "system.tests.test_twg_health",
    "system.tests.test_command_integrity",
    "system.tests.test_codex_adapter",
    "system.tests.test_codex_skill_adapters",
    "system.tests.test_critical_commitment_refresh",
    "system.tests.test_markdown_title_guard",
    "system.tests.test_registry_docs",
    "system.tests.test_runtime_detection",
    "system.tests.test_model_policy",
    "system.tests.test_model_eval",
    "system.tests.test_model_neutrality",
    "system.tests.test_legacy_cli",
    "system.tests.test_obsidian_bridge",
    "system.tests.test_pack_manager",
    "system.tests.test_personal_memory",
    "system.tests.test_task_store",
    "system.tests.test_upgrade_compat",
]


def run(cmd: list[str], *, quiet: bool = False):
    """Run a command from repo root."""
    if quiet:
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return result

    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=True, text=True, encoding="utf-8", errors="replace")


def run_capture(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def sync_repo_adapters():
    """Regenerate tracked adapter stubs and ignored local adapter directories."""
    run([sys.executable, "system/scripts/sync_cli_adapters.py"])


def sync_codex_skill_adapters(output_dir: str | None = None, *, quiet: bool = False):
    """Regenerate promoted Codex skill adapters."""
    cmd = [sys.executable, "system/scripts/sync_codex_skill_adapters.py"]
    if output_dir:
        cmd.extend(["--output-dir", output_dir])
    run(cmd, quiet=quiet)


def compile_sources():
    """Compile adapter-related Python files."""
    run([sys.executable, "-m", "py_compile", *PY_COMPILE_FILES])


def run_command_integrity(codex_output_dir: str | None = None):
    """Fail on duplicate commands, alias collisions, or generated adapter drift."""
    cmd = [
        sys.executable,
        "system/scripts/command_integrity.py",
        "--require-generated",
    ]
    if codex_output_dir:
        cmd.extend(["--codex-skills-dir", codex_output_dir])
    run(cmd)


def run_registry_docs_check():
    """Fail if any tracked registry-derived surface drifted."""
    run([sys.executable, "system/scripts/generate_registry_docs.py", "--check"])


def run_public_docs_check():
    """Fail if the dependency-free public Markdown catalog drifted."""
    run(["node", "system/docs-site/scripts/generate-docs.js", "--check"])


def run_offline_model_eval():
    """Run only the deterministic sanitized evaluation; never a live provider."""
    run([sys.executable, "system/scripts/model_eval.py", "run", "--mode", "offline", "--json"])


def run_tests():
    """Run the adapter-focused regression suite."""
    run([sys.executable, "-m", "unittest", *TEST_MODULES, "-v"])


def run_privacy_guard():
    """Fail on PII, secrets, local runtime state, or private workspace content."""
    run([sys.executable, "system/scripts/privacy_guard.py", "--tree"])


def generated_files_diff() -> str:
    result = run_capture(["git", "diff", "--", *GENERATED_REPO_FILES])
    if result.returncode not in {0, 1}:
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result.stdout


def assert_repo_generated_files_clean(initial_diff: str):
    """Fail if adapter sync introduced new tracked-stub drift."""
    current_diff = generated_files_diff()
    if current_diff != initial_diff:
        print(current_diff, file=sys.stderr)
        raise SystemExit(1)


def assert_generated_adapter_dirs_untracked():
    """Fail if generated runtime adapter directories are tracked."""
    result = run_capture(["git", "ls-files", "--", *FORBIDDEN_TRACKED_PREFIXES])
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )
    tracked = [
        line
        for line in result.stdout.splitlines()
        if line.strip() and (ROOT / line.strip()).exists()
    ]
    if tracked:
        print("Generated or local runtime files are tracked:", file=sys.stderr)
        for path in tracked[:80]:
            print(f"  - {path}", file=sys.stderr)
        if len(tracked) > 80:
            print(f"  ... and {len(tracked) - 80} more", file=sys.stderr)
        raise SystemExit(1)


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
    parser.add_argument("--skip-tests", action="store_true", help="Skip unit tests")
    parser.add_argument(
        "--skip-clean-check",
        action="store_true",
        help="Skip git diff verification for generated repo files",
    )
    parser.add_argument(
        "--skip-privacy",
        action="store_true",
        help="Skip privacy guard. Intended only for local diagnosis.",
    )
    args = parser.parse_args()

    initial_generated_diff = generated_files_diff()
    sync_repo_adapters()

    temp_dir = None
    codex_output_dir = args.codex_output_dir
    quiet_codex_sync = False

    if args.mode == "check" and codex_output_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        codex_output_dir = temp_dir.name

    sync_codex_skill_adapters(codex_output_dir, quiet=quiet_codex_sync)
    run_command_integrity(codex_output_dir)
    run_registry_docs_check()
    run_public_docs_check()
    compile_sources()
    run_offline_model_eval()

    if not args.skip_tests:
        run_tests()

    assert_generated_adapter_dirs_untracked()

    if not args.skip_privacy:
        run_privacy_guard()

    if not args.skip_clean_check:
        assert_repo_generated_files_clean(initial_generated_diff)

    if temp_dir is not None:
        temp_dir.cleanup()

    print("Adapter guard passed.")


if __name__ == "__main__":
    main()
