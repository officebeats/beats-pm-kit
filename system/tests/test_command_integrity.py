"""Command integrity regression tests."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import command_integrity  # noqa: E402
from utils.command_registry import build_command_catalog  # noqa: E402


def write_workflow(root: Path, name: str) -> None:
    path = root / ".agent" / "workflows" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ndescription: {name} workflow\n---\n\n# /{name}\n", encoding="utf-8")


def write_registry(root: Path, commands: dict) -> None:
    path = root / ".agent" / "command-registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "commands": commands}, indent=2), encoding="utf-8")


class TestCommandIntegrity(unittest.TestCase):
    def test_alias_cannot_collide_with_canonical_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "archive")
            write_workflow(root, "vacuum")
            write_registry(root, {"vacuum": {"aliases": ["archive"]}})

            with self.assertRaisesRegex(ValueError, "collides with canonical workflow /archive"):
                build_command_catalog(root)

    def test_alias_cannot_belong_to_multiple_workflows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_workflow(root, "week")
            write_registry(root, {"day": {"aliases": ["status"]}, "week": {"aliases": ["/status"]}})

            with self.assertRaisesRegex(ValueError, "assigned to both /day and /week"):
                build_command_catalog(root)

    def test_codex_skill_names_must_be_unique(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_workflow(root, "week")
            write_registry(
                root,
                {
                    "day": {"codex": {"promotion": "skill", "skill_name": "beats-plan"}},
                    "week": {"codex": {"promotion": "skill", "skill_name": "beats-plan"}},
                },
            )

            with self.assertRaisesRegex(ValueError, "assigned to both /day and /week"):
                build_command_catalog(root)

    def test_registry_cannot_reference_missing_workflows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_registry(root, {"missing": {}})

            with self.assertRaisesRegex(ValueError, "workflows that do not exist: missing"):
                build_command_catalog(root)

    def test_generated_codex_index_must_match_catalog(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_workflow(root, "week")
            write_registry(root, {})
            (root / "CODEX_COMMANDS.md").write_text(
                "# CODEX_COMMANDS.md\n\n| Command | Workflow | Promoted Codex Skill |\n"
                "| --- | --- | --- |\n"
                "| `/day` | `.agent/workflows/day.md` | Dispatch only |\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(command_integrity.CommandIntegrityError, "CODEX_COMMANDS.md rows"):
                command_integrity.validate_command_integrity(root)

    def test_current_repo_command_integrity_passes_without_generated_requirement(self):
        catalog = command_integrity.validate_command_integrity(ROOT_DIR)
        command_names = {entry["name"] for entry in catalog}
        self.assertIn("archive", command_names)
        self.assertIn("vacuum", command_names)
        vacuum = next(entry for entry in catalog if entry["name"] == "vacuum")
        self.assertNotIn("archive", vacuum["aliases"])
        self.assertIn("cleanup", vacuum["aliases"])


if __name__ == "__main__":
    unittest.main()
