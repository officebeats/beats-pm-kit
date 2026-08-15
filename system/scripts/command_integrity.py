#!/usr/bin/env python3
"""Validate canonical workflow commands and generated runtime adapters."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.command_registry import (  # noqa: E402
    get_promoted_codex_commands,
    validate_command_catalog,
)


class CommandIntegrityError(RuntimeError):
    """Raised when the command/adaptor catalog has drifted."""


def _format_errors(errors: list[str]) -> str:
    return "Command integrity check failed:\n" + "\n".join(f"- {error}" for error in errors)


def _parse_codex_rows(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        raise CommandIntegrityError(f"Missing generated Codex command index: {path}")
    rows: list[tuple[str, str]] = []
    pattern = re.compile(r"^\|\s+`/([^`]+)`\s+\|\s+`([^`]+)`\s+\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            rows.append((match.group(1), match.group(2)))
    return rows


def _markdown_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {item.name for item in path.glob("*.md") if item.is_file()}


def validate_generated_adapters(
    root: Path,
    catalog: list[dict[str, object]],
    *,
    require_generated: bool = False,
    codex_skills_dir: Path | None = None,
) -> list[str]:
    """Return generated-adapter drift errors for the validated catalog."""
    errors: list[str] = []
    expected_workflows = [f"{entry['name']}.md" for entry in catalog]
    expected_workflow_set = set(expected_workflows)

    codex_rows = _parse_codex_rows(root / "CODEX_COMMANDS.md")
    expected_rows = [(str(entry["name"]), str(entry["workflow"])) for entry in catalog]
    if codex_rows != expected_rows:
        errors.append("CODEX_COMMANDS.md rows do not exactly match the command catalog")

    adapter_dirs: list[str] = []
    for rel_path in adapter_dirs:
        adapter_dir = root / rel_path
        if not adapter_dir.exists():
            if require_generated:
                errors.append(f"Missing generated adapter directory: {rel_path}")
            continue
        actual = _markdown_files(adapter_dir)
        if actual != expected_workflow_set:
            missing = sorted(expected_workflow_set - actual)
            extra = sorted(actual - expected_workflow_set)
            details: list[str] = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if extra:
                details.append("extra " + ", ".join(extra))
            errors.append(f"{rel_path} does not match workflows ({'; '.join(details)})")

    if codex_skills_dir is not None:
        expected_skills = {
            str(entry["codex_skill_name"])
            for entry in get_promoted_codex_commands(root)
        }
        if not codex_skills_dir.exists():
            errors.append(f"Missing Codex skills directory: {codex_skills_dir}")
        else:
            actual_skills = {
                item.name
                for item in codex_skills_dir.iterdir()
                if item.is_dir() and (item / "SKILL.md").exists()
            }
            if actual_skills != expected_skills:
                missing = sorted(expected_skills - actual_skills)
                extra = sorted(actual_skills - expected_skills)
                details = []
                if missing:
                    details.append("missing " + ", ".join(missing))
                if extra:
                    details.append("extra " + ", ".join(extra))
                errors.append(f"Codex skill adapters do not match registry ({'; '.join(details)})")

    return errors


def validate_command_integrity(
    root: Path | str | None = None,
    *,
    require_generated: bool = False,
    codex_skills_dir: Path | str | None = None,
) -> list[dict[str, object]]:
    """Validate canonical commands plus generated runtime adapters."""
    repo_root = Path(root) if root is not None else ROOT
    catalog = validate_command_catalog(repo_root)
    errors = validate_generated_adapters(
        repo_root,
        catalog,
        require_generated=require_generated,
        codex_skills_dir=Path(codex_skills_dir) if codex_skills_dir else None,
    )
    if errors:
        raise CommandIntegrityError(_format_errors(errors))
    return catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Beats PM Kit command/adaptor integrity")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument(
        "--require-generated",
        action="store_true",
        help="Require generated runtime adapter directories to exist and match workflows",
    )
    parser.add_argument(
        "--codex-skills-dir",
        type=Path,
        default=None,
        help="Optional generated Codex skills directory to validate",
    )
    args = parser.parse_args(argv)

    try:
        catalog = validate_command_integrity(
            args.root,
            require_generated=args.require_generated,
            codex_skills_dir=args.codex_skills_dir,
        )
    except (CommandIntegrityError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Command integrity passed: {len(catalog)} canonical workflow command(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
