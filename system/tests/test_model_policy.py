"""Execution-profile resolution and local promotion tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from system.scripts import model_policy


def runtime(primary: str = "codex", profiles: list[str] | None = None) -> dict:
    supported = profiles if profiles is not None else ["fast", "balanced", "deep"]
    return {
        "schema_version": 2,
        "primary": primary,
        "primary_display": primary.title(),
        "primary_version": "test 1.0",
        "capabilities": ["filesystem_read", "structured_output"],
        "supported_profiles": supported,
        "selection_status": "active" if primary != "unknown" else "none",
        "available_runtimes": [] if primary == "unknown" else [primary],
        "details": [],
    }


class TestModelPolicy(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        source_registry = Path(__file__).resolve().parents[2] / ".agent" / "command-registry.json"
        registry = json.loads(source_registry.read_text(encoding="utf-8"))
        workflows = self.root / ".agent" / "workflows"
        workflows.mkdir(parents=True)
        commands = {
            command
            for profile_commands in registry["command_profiles"].values()
            for command in profile_commands
        }
        for command in commands:
            (workflows / f"{command}.md").write_text(
                f"---\ndescription: {command}\n---\n\n# {command.title()}\n",
                encoding="utf-8",
            )
        (self.root / ".agent" / "command-registry.json").write_text(
            json.dumps(registry), encoding="utf-8"
        )

    def test_resolve_inherits_runtime_model_and_command_profile(self):
        result = model_policy.resolve("find", root=self.root, runtime_result=runtime())

        self.assertEqual(result["base_profile"], "fast")
        self.assertEqual(result["profile"], "fast")
        self.assertEqual(result["model"], "inherit")
        self.assertEqual(result["model_source"], "runtime")

    def test_risk_signal_escalates_to_deep(self):
        result = model_policy.resolve(
            "track",
            signals=["conflicting_evidence"],
            root=self.root,
            runtime_result=runtime(),
        )

        self.assertEqual(result["base_profile"], "balanced")
        self.assertEqual(result["profile"], "deep")
        self.assertEqual(result["escalated_by"], ["conflicting_evidence"])

    def test_unknown_signal_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsupported escalation signal"):
            model_policy.resolve(
                "find", signals=["guess"], root=self.root, runtime_result=runtime()
            )

    def test_missing_deep_support_uses_inherit_with_visible_warning(self):
        result = model_policy.resolve(
            "review",
            root=self.root,
            runtime_result=runtime(profiles=["fast", "balanced"]),
        )

        self.assertEqual(result["model"], "inherit")
        self.assertTrue(result["downgraded"])
        self.assertTrue(any("Deep" in warning for warning in result["warnings"]))

    def test_adapter_only_runtime_does_not_suppress_unavailable_override_warning(self):
        policy_path = self.root / ".beats" / "model-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy_path.write_text(
            json.dumps({"schema_version": 1, "overrides": {"claude": {"deep": "candidate"}}}),
            encoding="utf-8",
        )
        detected = runtime(primary="unknown")
        detected["all_runtimes"] = ["claude"]
        detected["details"] = [
            {"name": "claude", "available": False, "adapter_present": True}
        ]

        result = model_policy.status(root=self.root, runtime_result=detected)

        self.assertTrue(any("not currently available" in warning for warning in result["warnings"]))

    def test_promote_requires_matching_recommended_evaluation_and_backs_up(self):
        policy_path = self.root / ".beats" / "model-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy_path.write_text(
            json.dumps({"schema_version": 1, "overrides": {"codex": {"fast": "old-model"}}}),
            encoding="utf-8",
        )
        evaluation = self.root / ".beats" / "evals" / "candidate.json"
        evaluation.parent.mkdir(parents=True)
        evaluation.write_text(
            json.dumps(
                {
                    "comparison": {"recommended": True, "safety_gates_passed": True},
                    "candidate": {
                        "runtime": "codex",
                        "profile": "fast",
                        "model": "candidate-model",
                    },
                }
            ),
            encoding="utf-8",
        )

        result = model_policy.promote(
            "codex", "fast", "candidate-model", evaluation=evaluation, root=self.root
        )

        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(policy["overrides"]["codex"]["fast"], "candidate-model")
        self.assertTrue((self.root / result["backup"]).is_file())

    def test_promotion_rejects_failed_or_mismatched_evaluation(self):
        evaluation = self.root / ".beats" / "evals" / "candidate.json"
        evaluation.parent.mkdir(parents=True)
        evaluation.write_text(
            json.dumps(
                {
                    "comparison": {"recommended": False, "safety_gates_passed": False},
                    "candidate": {
                        "runtime": "codex",
                        "profile": "fast",
                        "model": "candidate-model",
                    },
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "not recommended"):
            model_policy.promote(
                "codex", "fast", "candidate-model", evaluation=evaluation, root=self.root
            )

    def test_promotion_rejects_evidence_outside_ignored_eval_storage(self):
        evaluation = self.root / "candidate.json"
        evaluation.write_text("{}", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, r"\.beats/evals"):
            model_policy.promote(
                "codex", "fast", "candidate-model", evaluation=evaluation, root=self.root
            )

    def test_reset_is_backed_up_and_idempotent(self):
        policy_path = self.root / ".beats" / "model-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy_path.write_text("{}\n", encoding="utf-8")

        result = model_policy.reset(root=self.root)

        self.assertFalse(policy_path.exists())
        self.assertTrue((self.root / result["backup"]).is_file())
        self.assertEqual(model_policy.reset(root=self.root)["status"], "unchanged")


if __name__ == "__main__":
    unittest.main()
