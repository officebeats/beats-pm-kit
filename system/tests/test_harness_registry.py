"""Runtime-neutral agentic harness registry tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from system.scripts import harness_registry
from system.utils.command_registry import get_harness_policy


ROOT = Path(__file__).resolve().parents[2]


class TestHarnessRegistry(unittest.TestCase):
    def test_primary_harness_contract_is_cross_runtime_and_one_level(self):
        policy = get_harness_policy(ROOT)

        self.assertEqual(policy["primary_runtimes"], ["antigravity", "codex", "claude"])
        self.assertEqual(policy["routing"]["strategy"], "one-level")
        self.assertEqual(policy["routing"]["maximum_initial_sources"], 5)
        self.assertEqual(policy["routing"]["maximum_reference_hops"], 1)
        self.assertTrue(policy["cache_policy"]["deterministic_tool_order"])
        self.assertTrue(policy["cache_policy"]["append_dynamic_context_after_prefix"])

    def test_alias_resolves_to_bounded_runtime_neutral_manifest(self):
        manifest = harness_registry.resolve_harness_command("/status", ROOT)

        self.assertEqual(manifest["id"], "day")
        self.assertEqual(manifest["response"]["operator"], "compact_operator")
        self.assertIn("exact transcript", manifest["response"]["verbatim_when"])
        self.assertEqual(manifest["runtimes"]["primary"], ["antigravity", "codex", "claude"])
        self.assertEqual(manifest["context"]["maximum_initial_sources"], 5)
        self.assertIn("never load this list wholesale", manifest["context"]["instruction"])
        self.assertIn("context_store.py", manifest["context"]["payload_policy"])

    def test_discovery_registry_covers_every_skill_and_workflow(self):
        registry = harness_registry.compact_discovery_registry(ROOT)

        self.assertEqual(registry["routing"], "one-level")
        self.assertEqual(len(registry["commands"]), 44)
        self.assertEqual(len(registry["skills"]), len(list((ROOT / ".agent/skills").glob("*/SKILL.md"))))

    def test_unrouted_skill_resolves_directly_without_nested_router(self):
        resolved = harness_registry.resolve_harness_target("workshop-facilitation", ROOT, record_usage=False)
        self.assertEqual(resolved["kind"], "skill")
        self.assertEqual(resolved["entrypoint"], ".agent/skills/workshop-facilitation/SKILL.md")
        self.assertEqual(resolved["context"]["maximum_reference_hops"], 1)
        self.assertIn("do not invoke another routing hierarchy", resolved["context"]["instruction"])

    def test_command_manifest_has_full_harness_contract(self):
        resolved = harness_registry.resolve_harness_command("create", ROOT)
        for field in ["triggers", "inputs", "context", "tools", "permissions", "quality_gate", "response", "checkpoint_policy", "cache_policy", "outputs", "runtimes", "recovery"]:
            self.assertIn(field, resolved)
        self.assertIn("completion_criteria", resolved["quality_gate"])

    def test_context_budgets_are_enforced(self):
        report = harness_registry.audit_budgets(ROOT)

        self.assertTrue(report["ok"], report["violations"])
        self.assertLessEqual(report["measurements"]["registry_tokens"], 2500)

    def test_resolution_records_one_usage_ledger_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "workflows").mkdir()
            (root / "workflows" / "day.md").write_text("w" * 40, encoding="utf-8")
            (root / "sources").mkdir()
            (root / "sources" / "a.md").write_text("s" * 60, encoding="utf-8")
            manifest = {
                "kind": "command",
                "id": "day",
                "workflow": "workflows/day.md",
                "context": {"candidate_required": ["sources/a.md", "sources/missing.md"]},
            }
            with mock.patch.object(harness_registry, "resolve_command_name", return_value="day"), \
                    mock.patch.object(harness_registry, "resolve_harness_command", return_value=manifest):
                resolved = harness_registry.resolve_harness_target("/day", root)
            self.assertIs(resolved, manifest)
            ledger = root / ".beats" / "usage.jsonl"
            lines = ledger.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertEqual(entry["command"], "day")
            self.assertEqual(entry["sources_loaded"], 2)
            self.assertEqual(entry["source_bytes"], 100)
            self.assertGreaterEqual(entry["wall_ms"], 0)

    def test_usage_telemetry_failure_never_breaks_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {"kind": "skill", "id": "broken", "entrypoint": "missing.md"}
            with mock.patch.object(harness_registry, "resolve_command_name", return_value=None), \
                    mock.patch.object(harness_registry, "resolve_harness_skill", return_value=manifest), \
                    mock.patch.object(
                        harness_registry.harness_telemetry, "append_usage", side_effect=OSError("disk full")
                    ):
                resolved = harness_registry.resolve_harness_target("broken", root)
            self.assertIs(resolved, manifest)
            self.assertFalse((root / ".beats" / "usage.jsonl").exists())

    def test_record_usage_opt_out_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {"kind": "skill", "id": "quiet", "entrypoint": "missing.md"}
            with mock.patch.object(harness_registry, "resolve_command_name", return_value=None), \
                    mock.patch.object(harness_registry, "resolve_harness_skill", return_value=manifest):
                harness_registry.resolve_harness_target("quiet", root, record_usage=False)
            self.assertFalse((root / ".beats").exists())


if __name__ == "__main__":
    unittest.main()
