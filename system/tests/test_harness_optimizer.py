"""Tests for bounded, eval-gated harness optimization."""

from __future__ import annotations

import unittest

from system.scripts import harness_optimizer
from system.utils.command_registry import get_harness_policy


def scenario(scenario_id: str, tokens: int, turns: int = 3, score: float = 1.0) -> dict:
    return {
        "id": scenario_id,
        "total_processed_tokens": tokens,
        "turns": turns,
        "functionality_score": score,
        "intent_score": score,
        "source_citation_recall": 1.0,
        "exact_wording_preserved": True,
        "approval_privacy_unchanged": True,
        "artifact_compatible": True,
    }


class TestHarnessOptimizer(unittest.TestCase):
    def test_allowlist_matches_canonical_harness_registry(self):
        self.assertEqual(
            harness_optimizer.ALLOWED_SURFACES,
            set(get_harness_policy()["optimizer"]["allowed_surfaces"]),
        )

    def experiment(self, surface: str = "top_k") -> dict:
        return {
            "id": "exp-001",
            "held_out": True,
            "change": {"surface": surface, "before": 8, "after": 5},
        }

    def test_passing_change_still_requires_human_promotion(self):
        baseline = {"scenarios": [scenario("a", 1000), scenario("b", 2000)]}
        candidate = {"scenarios": [scenario("a", 700), scenario("b", 1400)]}
        result = harness_optimizer.evaluate_experiment(self.experiment(), baseline, candidate)
        self.assertTrue(result["passed"])
        self.assertTrue(result["human_approval_required"])
        self.assertFalse(result["automatic_promotion"])

    def test_quality_regression_fails_per_scenario(self):
        baseline = {"scenarios": [scenario("a", 1000)]}
        degraded = scenario("a", 500, score=0.9)
        candidate = {"scenarios": [degraded]}
        result = harness_optimizer.evaluate_experiment(self.experiment(), baseline, candidate)
        self.assertFalse(result["passed"])
        self.assertIn("functionality_score regressed", result["scenarios"][0]["failures"])

    def test_protected_surface_is_rejected(self):
        payload = {"scenarios": [scenario("a", 1000)]}
        with self.assertRaisesRegex(ValueError, "may not change"):
            harness_optimizer.evaluate_experiment(self.experiment("permissions"), payload, payload)

    def test_single_scenario_token_regression_fails(self):
        baseline = {"scenarios": [scenario("a", 1000), scenario("b", 1000), scenario("c", 4000)]}
        candidate = {"scenarios": [scenario("a", 1100), scenario("b", 400), scenario("c", 1000)]}
        result = harness_optimizer.evaluate_experiment(self.experiment(), baseline, candidate)
        self.assertFalse(result["gates"]["per_scenario_token_regression"])

    def test_pairing_metadata_must_match(self):
        base = scenario("a", 1000)
        base["pairing"] = {"runtime": "codex", "model": "same", "effort": "high", "cache_state": "cold", "repository_fixture": "v1"}
        candidate = scenario("a", 700)
        candidate["pairing"] = {**base["pairing"], "effort": "low"}
        with self.assertRaisesRegex(ValueError, "pairing metadata"):
            harness_optimizer.evaluate_experiment(
                self.experiment(),
                {"scenarios": [base]},
                {"scenarios": [candidate]},
            )


if __name__ == "__main__":
    unittest.main()
