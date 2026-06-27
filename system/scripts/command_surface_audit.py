#!/usr/bin/env python3
"""Audit duplicate slash-command claims in project skill metadata."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.command_registry import build_command_catalog  # noqa: E402


SLASH_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.:-])/(?!/)([A-Za-z][A-Za-z0-9_-]*)(?![A-Za-z0-9_/-])"
)


@dataclass(frozen=True)
class SurfaceFinding:
    """A duplicate command claim found in project skill metadata."""

    path: Path
    line_number: int
    command: str
    owner: str
    line: str

    def format(self, root: Path) -> str:
        rel_path = self.path.relative_to(root)
        return (
            f"{rel_path}:{self.line_number}: /{self.command} belongs to /{self.owner}; "
            f"project skill metadata should use natural-language triggers: {self.line.strip()}"
        )


def command_owner_map(root: Path) -> dict[str, str]:
    """Map canonical command names and aliases to their owning workflow."""
    owners: dict[str, str] = {}
    for entry in build_command_catalog(root):
        name = str(entry["name"])
        owners[name] = name
        for alias in entry["aliases"]:
            owners[str(alias)] = name
    return owners


def frontmatter_lines(path: Path) -> list[tuple[int, str]]:
    """Return frontmatter lines with 1-based line numbers."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    result: list[tuple[int, str]] = []
    for index, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return result
        result.append((index, line))
    return []


def find_command_surface_collisions(root: Path | str | None = None) -> list[SurfaceFinding]:
    """Return project skill metadata that claims canonical slash commands."""
    repo_root = Path(root) if root is not None else ROOT
    owners = command_owner_map(repo_root)
    findings: list[SurfaceFinding] = []

    skills_dir = repo_root / ".agent" / "skills"
    if not skills_dir.exists():
        return findings

    for path in sorted(skills_dir.glob("*/SKILL.md")):
        for line_number, line in frontmatter_lines(path):
            for match in SLASH_TOKEN_RE.finditer(line):
                command = match.group(1)
                owner = owners.get(command)
                if owner is None:
                    continue
                findings.append(
                    SurfaceFinding(
                        path=path,
                        line_number=line_number,
                        command=command,
                        owner=owner,
                        line=line,
                    )
                )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when project skill metadata advertises canonical Beats slash commands"
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to audit")
    args = parser.parse_args(argv)

    findings = find_command_surface_collisions(args.root)
    if findings:
        print("Command surface audit failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.format(args.root)}", file=sys.stderr)
        return 1

    print("Command surface audit passed: project skill metadata has no duplicate command claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
