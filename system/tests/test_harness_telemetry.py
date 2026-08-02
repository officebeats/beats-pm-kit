"""Tests for harness trajectory telemetry."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import harness_telemetry


def sample_record() -> dict:
    return {
        "workflow": "create",
        "scenario": "source-heavy",
        "runtime": "codex",
        "model": "gpt-test",
        "effort": "high",
        "registry_version": "3",
        "repository_fixture": "fixture-v1",
        "cache_state": "cold",
        "uncached_input_tokens": 1000,
        "cached_input_tokens": 200,
        "cache_write_tokens": 100,
        "output_tokens": 300,
        "tool_payload_tokens": 400,
        "turns": 3,
        "retries": 0,
        "compactions": 1,
        "source_loads": 4,
        "elapsed_seconds": 12.5,
        "quality_result": {"passed": True, "score": 1.0},
    }


class TestHarnessTelemetry(unittest.TestCase):
    def test_record_separates_processed_billable_and_cost(self):
        enriched = harness_telemetry.enrich_record(
            sample_record(),
            uncached_input_cost_per_million=10,
            cached_input_cost_per_million=1,
            cache_write_cost_per_million=2,
            output_cost_per_million=20,
        )
        self.assertEqual(enriched["total_processed_tokens"], 2000)
        self.assertEqual(enriched["estimated_billable_tokens"], 1600)
        self.assertAlmostEqual(enriched["estimated_billable_cost_usd"], 0.0164)

    def test_append_and_summary_keep_cache_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "telemetry.jsonl"
            harness_telemetry.append_record(sample_record(), ledger=ledger)
            warm = sample_record()
            warm["cache_state"] = "warm"
            warm["turns"] = 2
            harness_telemetry.append_record(warm, ledger=ledger)
            summary = harness_telemetry.summarize(harness_telemetry.load_records(ledger))
            self.assertEqual(summary["count"], 2)
            self.assertEqual(summary["median_turns"], 2.5)
            self.assertEqual(summary["by_cache_state"], {"cold": 1, "warm": 1})

    def test_missing_measurement_is_rejected(self):
        record = sample_record()
        del record["source_loads"]
        with self.assertRaisesRegex(ValueError, "source_loads"):
            harness_telemetry.enrich_record(record)

    def test_export_builds_runtime_and_cache_matched_optimizer_ids(self):
        record = harness_telemetry.enrich_record(sample_record())
        record["quality_result"] = {
            "functionality_score": 1.0,
            "intent_score": 1.0,
            "source_citation_recall": 1.0,
            "exact_wording_preserved": True,
            "approval_privacy_unchanged": True,
            "artifact_compatible": True,
        }
        payload = harness_telemetry.export_optimizer_payload([record], label="baseline")
        self.assertEqual(payload["scenarios"][0]["id"], "codex:cold:source-heavy")
        self.assertEqual(payload["scenarios"][0]["total_processed_tokens"], 2000)
        self.assertEqual(payload["scenarios"][0]["pairing"]["repository_fixture"], "fixture-v1")


if __name__ == "__main__":
    unittest.main()
