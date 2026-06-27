"""Slash command surface audit regression tests."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import command_surface_audit  # noqa: E402


def write_workflow(root: Path, name: str) -> None:
    path = root / ".agent" / "workflows" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ndescription: {name} workflow\n---\n\n# /{name}\n", encoding="utf-8")


def write_registry(root: Path, commands: dict) -> None:
    path = root / ".agent" / "command-registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "commands": commands}, indent=2), encoding="utf-8")


def write_skill(root: Path, name: str, content: str) -> None:
    path = root / ".agent" / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestCommandSurfaceAudit(unittest.TestCase):
    """Ensure project skills do not advertise canonical slash command entrypoints."""

    def test_current_repo_skill_metadata_has_no_duplicate_command_claims(self):
        findings = command_surface_audit.find_command_surface_collisions(ROOT_DIR)
        self.assertEqual(findings, [])

    def test_flags_canonical_commands_and_aliases_in_skill_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "archive")
            write_workflow(root, "vacuum")
            write_registry(root, {"vacuum": {"aliases": ["cleanup"]}})
            write_skill(
                root,
                "vacuum-protocol",
                "---\n"
                "name: vacuum-protocol\n"
                "description: Use for /vacuum, /cleanup, and /unknown.\n"
                "---\n"
                "\n"
                "Body references to /archive are workflow routing docs and are allowed here.\n",
            )

            findings = command_surface_audit.find_command_surface_collisions(root)

            self.assertEqual({finding.command for finding in findings}, {"vacuum", "cleanup"})
            self.assertEqual({finding.owner for finding in findings}, {"vacuum"})

    def test_ignores_body_mentions_urls_paths_and_noncanonical_slashes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "body")
            write_workflow(root, "vacuum")
            write_registry(root, {})
            write_skill(
                root,
                "office-helper",
                "---\n"
                "name: office-helper\n"
                "description: Handles Office selector /body/p[3], URL https://example.com/vacuum, and /ask.\n"
                "---\n"
                "\n"
                "The public workflow can still be referenced in the body as /vacuum.\n",
            )

            findings = command_surface_audit.find_command_surface_collisions(root)

            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
