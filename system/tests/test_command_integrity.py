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
    names = sorted(item.stem for item in (root / ".agent" / "workflows").glob("*.md"))
    path.write_text(
        json.dumps(
            {
                "schema_version": 3,
                "runtime_policy": {
                    "selection": "active-runtime",
                    "unknown_capabilities": "deny",
                    "allow_cross_provider": False,
                },
                "harness": {
                    "primary_runtimes": ["antigravity", "codex", "claude"],
                    "routing": {
                        "strategy": "one-level",
                        "maximum_initial_sources": 5,
                        "maximum_reference_hops": 1,
                    },
                    "context_budgets": {
                        "runtime_bootstrap_tokens": 1500,
                        "registry_tokens": 2500,
                        "skill_entrypoint_tokens": 2500,
                        "initial_command_tokens": 6000,
                    },
                    "cache_policy": {
                        "stable_prefix": ["identity", "safety", "routing"],
                        "append_dynamic_context_after_prefix": True,
                        "deterministic_tool_order": True,
                    },
                    "response_profiles": {
                        "operator_default": "compact_operator",
                        "final_default": "artifact",
                        "available": ["compact_operator", "artifact", "verbatim"],
                        "selection": {
                            "compact_operator": "execution",
                            "artifact": "deliverable",
                            "verbatim": "exact wording",
                        },
                    },
                    "optimizer": {"promotion": "human-approved"},
                },
                "execution_profiles": {
                    "fast": {"rank": 1},
                    "balanced": {"rank": 2},
                    "deep": {"rank": 3},
                },
                "command_profiles": {"fast": names, "balanced": [], "deep": []},
                "escalation_signals": ["conflicting_evidence"],
                "commands": commands,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


class TestCommandIntegrity(unittest.TestCase):
    def test_schema_v3_requires_every_workflow_in_exactly_one_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_workflow(root, "week")
            write_registry(root, {"day": {}, "week": {}})
            registry_path = root / ".agent" / "command-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["command_profiles"]["fast"] = ["day"]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing execution profiles: week"):
                build_command_catalog(root)

    def test_schema_v3_rejects_duplicate_profile_assignment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_registry(root, {"day": {}})
            registry_path = root / ".agent" / "command-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["command_profiles"]["balanced"] = ["day"]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "multiple execution profiles: day"):
                build_command_catalog(root)

    def test_catalog_exposes_registry_execution_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_workflow(root, "day")
            write_registry(root, {"day": {}})

            entry = build_command_catalog(root)[0]

            self.assertEqual(entry["execution_profile"], "fast")

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
