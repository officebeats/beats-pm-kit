"""Runtime-neutral agentic harness registry tests."""

from __future__ import annotations

import unittest
from pathlib import Path

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
        resolved = harness_registry.resolve_harness_target("workshop-facilitation", ROOT)
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


if __name__ == "__main__":
    unittest.main()
