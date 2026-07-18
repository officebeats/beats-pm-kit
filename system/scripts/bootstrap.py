#!/usr/bin/env python3
"""Agent-native first-run bootstrap for Beats PM Kit."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts import core_setup
from system.scripts import upgrade_compat
from system.scripts.root_cleaner import clean_root


WORKSPACE_DIRS = (
    ".beats/cache",
    ".beats/diagnostics",
    ".beats/reports",
    ".beats/test-logs",
    "0. Incoming/staging",
    "0. Incoming/archive",
    "1. Company",
    "2. Products",
    "3. Meetings/transcripts",
    "3. Meetings/daily-briefs",
    "3. Meetings/weekly-digests",
    "4. People",
    "5. Trackers/archive",
    "6. Resources",
    "6. SOPs",
    "7. Partners",
    "8. Clients",
)


@dataclass
class Phase:
    name: str
    status: str
    detail: str = ""


def run_command(root: Path, command: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=root,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def short_output(result: subprocess.CompletedProcess[str], limit: int = 1400) -> str:
    output = (result.stdout or "").strip()
    if len(output) <= limit:
        return output
    return output[: limit - 3] + "..."


def add_phase(phases: list[Phase], name: str, status: str, detail: str = "") -> None:
    phases.append(Phase(name, status, detail))


def repo_version(root: Path) -> str:
    version_path = root / "VERSION"
    if not version_path.exists():
        return "unknown"
    return version_path.read_text(encoding="utf-8", errors="replace").strip() or "unknown"


def git_origin(root: Path) -> str:
    result = run_command(root, ["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def verify_repo(root: Path, repo_url: str | None, phases: list[Phase]) -> None:
    required = [root / ".agent", root / "system", root / "AGENTS.md", root / "README.md"]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        add_phase(phases, "verify_repo", "failed", f"missing: {', '.join(missing)}")
        return
    origin = git_origin(root)
    detail = f"version={repo_version(root)}"
    if repo_url:
        detail += f"; requested_repo={repo_url}"
    if origin:
        detail += f"; origin={origin}"
    add_phase(phases, "verify_repo", "ok", detail)


def upgrade_compatibility(root: Path, phases: list[Phase], *, apply: bool) -> None:
    """Gate existing workspaces before setup changes local Markdown."""
    report = upgrade_compat.inspect(root)
    if report.blockers:
        detail = f"blockers={len(report.blockers)}; run system/scripts/upgrade_compat.py --json"
        add_phase(phases, "upgrade_compatibility", "failed", detail)
        return
    if report.changes and not apply:
        detail = (
            f"safe_title_updates={len(report.changes)}; review with upgrade_compat.py --json, "
            "then rerun bootstrap with --apply-upgrade"
        )
        add_phase(phases, "upgrade_compatibility", "failed", detail)
        return
    if report.changes:
        result = upgrade_compat.apply_safe_changes(root, report)
        add_phase(
            phases,
            "upgrade_compatibility",
            "ok",
            f"migrated={result['changed']}; backup={result['backup']}",
        )
        return
    add_phase(phases, "upgrade_compatibility", "ok", "existing Markdown is v11-compatible")


def create_workspace(root: Path, phases: list[Phase]) -> None:
    created = 0
    for rel in WORKSPACE_DIRS:
        path = root / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created += 1
    marker = root / ".beats" / "initialized"
    if not marker.exists():
        marker.touch()
    add_phase(phases, "workspace", "ok", f"created_or_verified={len(WORKSPACE_DIRS)}; new_dirs={created}")


def seed_templates(root: Path, phases: list[Phase]) -> None:
    original_cwd = Path.cwd()
    original_argv = sys.argv[:]
    buffer = io.StringIO()
    try:
        os.chdir(root)
        sys.argv = [sys.argv[0], "--headless"]
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            core_setup.create_directories()
            core_setup.run_memory_init()
            core_setup.copy_templates()
        add_phase(phases, "seed_templates", "ok", "local tracker and settings templates verified")
    except Exception as exc:  # pragma: no cover - defensive reporting
        add_phase(phases, "seed_templates", "failed", str(exc))
    finally:
        sys.argv = original_argv
        os.chdir(original_cwd)


def sync_adapters(root: Path, phases: list[Phase], codex_output_dir: str | None) -> None:
    cli = run_command(root, [sys.executable, "system/scripts/sync_cli_adapters.py"])
    if cli.returncode != 0:
        add_phase(phases, "sync_cli_adapters", "failed", short_output(cli))
    else:
        add_phase(phases, "sync_cli_adapters", "ok", short_output(cli, 500))

    cmd = [sys.executable, "system/scripts/sync_codex_skill_adapters.py"]
    if codex_output_dir:
        cmd.extend(["--output-dir", codex_output_dir])
    codex = run_command(root, cmd)
    if codex.returncode != 0:
        add_phase(phases, "sync_codex_skills", "failed", short_output(codex))
    else:
        add_phase(phases, "sync_codex_skills", "ok", short_output(codex, 500))


def install_hooks(root: Path, phases: list[Phase]) -> None:
    result = run_command(root, [sys.executable, "system/scripts/install_git_hooks.py"])
    status = "ok" if result.returncode == 0 else "warning"
    add_phase(phases, "git_hooks", status, short_output(result, 500))


def run_health(root: Path, phases: list[Phase], *, skip_guards: bool) -> None:
    privacy = run_command(root, [sys.executable, "system/scripts/privacy_guard.py", "--tree"])
    add_phase(
        phases,
        "privacy_guard",
        "ok" if privacy.returncode == 0 else "failed",
        short_output(privacy, 700),
    )

    if skip_guards:
        add_phase(phases, "adapter_guard", "skipped", "--skip-guards requested")
        return

    adapter = run_command(
        root,
        [
            sys.executable,
            "system/scripts/adapter_guard.py",
            "--mode",
            "check",
            "--skip-tests",
            "--skip-clean-check",
        ],
    )
    add_phase(
        phases,
        "adapter_guard",
        "ok" if adapter.returncode == 0 else "failed",
        short_output(adapter, 900),
    )


def suggest_obsidian(root: Path, phases: list[Phase], *, apply_obsidian: bool) -> None:
    setup_cmd = [sys.executable, "system/scripts/obsidian_bridge.py"]
    if apply_obsidian:
        setup_cmd.extend(["configure", "--mode", "kit-vault", "--vault", str(root)])
    else:
        setup_cmd.extend(["guide", "--json"])
    setup = run_command(root, setup_cmd)
    add_phase(
        phases,
        "obsidian_direct_vault",
        "ok" if setup.returncode == 0 else "warning",
        short_output(setup, 700),
    )

    mcp = run_command(root, [sys.executable, "system/scripts/obsidian_mcp_health.py", "--pretty"])
    add_phase(
        phases,
        "obsidian_mcp",
        "ok" if mcp.returncode == 0 else "unavailable",
        short_output(mcp, 700) or "Use repo-local rg fallback.",
    )


def root_cleanup_phase(root: Path, phases: list[Phase], *, apply: bool) -> None:
    actions = clean_root(root, apply=apply)
    mode = "applied" if apply else "dry_run"
    add_phase(phases, "root_cleaner", "ok", f"{mode}; actions={len(actions)}")


def next_steps(root: Path) -> list[str]:
    return [
        "Open this folder in Codex or Antigravity.",
        "Run /start for guided profile setup when you want personalized local settings.",
        "Run /paste to process messy PM input or /day to see current priorities.",
        f"Optional Obsidian: run /obsidian, then open this existing folder as the vault: {root}",
    ]


def print_human(phases: list[Phase]) -> None:
    print("Beats PM Kit bootstrap")
    for phase in phases:
        detail = f" - {phase.detail}" if phase.detail else ""
        print(f"[{phase.status}] {phase.name}{detail}")
    print("")
    print("Next steps:")
    for step in next_steps():
        print(f"- {step}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Repo root to bootstrap")
    parser.add_argument("--repo-url", default=None, help="Repository URL supplied to the agent")
    parser.add_argument("--agent", action="store_true", help="Use agent-oriented output and defaults")
    parser.add_argument("--non-interactive", action="store_true", help="Do not prompt for personal setup values")
    parser.add_argument("--codex-output-dir", default=None, help="Override Codex skill adapter output directory")
    parser.add_argument("--skip-adapter-sync", action="store_true", help="Skip runtime adapter generation")
    parser.add_argument("--skip-hooks", action="store_true", help="Skip git hook installation")
    parser.add_argument("--skip-guards", action="store_true", help="Skip adapter guard; privacy guard still runs")
    parser.add_argument("--skip-obsidian", action="store_true", help="Skip Obsidian direct-vault and MCP checks")
    parser.add_argument("--apply-obsidian", action="store_true", help="Apply local Obsidian direct-vault settings")
    parser.add_argument("--clean-root", action="store_true", help="Apply root cleaner instead of dry-run preview")
    parser.add_argument("--apply-upgrade", action="store_true", help="Back up and apply safe v11 Markdown-title migrations")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    phases: list[Phase] = []

    verify_repo(root, args.repo_url, phases)
    upgrade_compatibility(root, phases, apply=args.apply_upgrade)
    if any(phase.status == "failed" for phase in phases):
        payload = {
            "agent": bool(args.agent),
            "non_interactive": bool(args.non_interactive),
            "root": root.as_posix(),
            "phases": [asdict(phase) for phase in phases],
            "next_steps": ["Resolve the compatibility report before bootstrap changes local workspace files."],
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print_human(phases)
        return 1
    create_workspace(root, phases)
    seed_templates(root, phases)
    root_cleanup_phase(root, phases, apply=args.clean_root)

    if args.skip_adapter_sync:
        add_phase(phases, "sync_adapters", "skipped", "--skip-adapter-sync requested")
    else:
        sync_adapters(root, phases, args.codex_output_dir)

    if args.skip_hooks:
        add_phase(phases, "git_hooks", "skipped", "--skip-hooks requested")
    else:
        install_hooks(root, phases)

    run_health(root, phases, skip_guards=args.skip_guards)

    if args.skip_obsidian:
        add_phase(phases, "obsidian", "skipped", "--skip-obsidian requested")
    else:
        suggest_obsidian(root, phases, apply_obsidian=args.apply_obsidian)

    payload = {
        "agent": bool(args.agent),
        "non_interactive": bool(args.non_interactive),
        "root": root.as_posix(),
        "phases": [asdict(phase) for phase in phases],
        "next_steps": next_steps(root),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(phases)

    return 1 if any(phase.status == "failed" for phase in phases) else 0


if __name__ == "__main__":
    raise SystemExit(main())
