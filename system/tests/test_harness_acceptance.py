"""Contract checks for the representative harness acceptance corpus."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from system.scripts import model_eval
from system.scripts import harness_registry


ROOT = Path(__file__).resolve().parents[2]


class TestHarnessAcceptanceCorpus(unittest.TestCase):
    def test_primary_commands_and_required_risk_scenarios_are_covered(self):
        payload = json.loads((ROOT / "system/evals/scenarios.json").read_text(encoding="utf-8"))
        scenarios = payload["scenarios"]
        covered = {scenario.get("command") for scenario in scenarios}
        self.assertEqual(set(payload["primary_commands"]) - covered, set())
        identifiers = {scenario["id"] for scenario in scenarios}
        for required in {
            "source-heavy-bounded-research",
            "long-session-checkpoint-continuity",
            "exact-language-preservation",
            "blocked-external-write",
            "artifact-contract-compatibility",
            "privacy-minimum-necessary",
            "raw-source-after-compaction",
        }:
            self.assertIn(required, identifiers)
        self.assertEqual(payload["paired_runtimes"], ["antigravity", "codex", "claude"])
        self.assertEqual(payload["cache_states"], ["cold", "warm"])

    def test_offline_baselines_pass_all_hard_gates(self):
        result = model_eval.run_offline()
        self.assertTrue(result["summary"]["safety_gates_passed"])
        self.assertEqual(result["summary"]["quality"], 100.0)

    def test_static_hot_path_reduction_exceeds_fifty_percent(self):
        report = harness_registry.audit_budgets(ROOT)
        largest_initial = max(report["measurements"]["commands"].values())
        self.assertLessEqual(largest_initial, 7000)  # half of the lowest audited 14k baseline hot path
        refactored = {
            "team-orchestrator",
            "ai-shaped-readiness-advisor",
            "deep-interview",
            "context-engineering-advisor",
            "engineering-planner",
        }
        total = sum(
            report["measurements"]["skills"][f".agent/skills/{name}/SKILL.md"]
            for name in refactored
        )
        self.assertLessEqual(total, 21147)  # half of the audited 42,294-token baseline


if __name__ == "__main__":
    unittest.main()
