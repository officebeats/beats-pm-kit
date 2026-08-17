"""Tests for harness trajectory telemetry."""

from __future__ import annotations

import json
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

    def test_usage_append_writes_contract_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry = harness_telemetry.append_usage(
                "day", sources_loaded=3, source_bytes=2048, wall_ms=12.3456, root=root
            )
            ledger = root / harness_telemetry.USAGE_LEDGER_REL
            lines = ledger.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            stored = json.loads(lines[0])
            self.assertEqual(stored, entry)
            self.assertEqual(
                sorted(stored), ["command", "source_bytes", "sources_loaded", "ts", "wall_ms"]
            )
            self.assertEqual(stored["command"], "day")
            self.assertEqual(stored["sources_loaded"], 3)
            self.assertEqual(stored["source_bytes"], 2048)
            self.assertAlmostEqual(stored["wall_ms"], 12.346)
            self.assertTrue(stored["ts"].endswith("Z"))

    def test_usage_ledger_rotates_keeping_newest(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            for index in range(21):
                harness_telemetry.append_usage(
                    f"cmd-{index}",
                    sources_loaded=1,
                    source_bytes=index,
                    wall_ms=1.0,
                    ledger=ledger,
                    max_lines=20,
                    keep_lines=10,
                )
            entries = harness_telemetry.load_usage(ledger)
            self.assertEqual(len(entries), 10)
            self.assertEqual(entries[0]["command"], "cmd-11")
            self.assertEqual(entries[-1]["command"], "cmd-20")

    def test_load_usage_skips_malformed_lines_and_hotspots_rank_by_mean(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "usage.jsonl"
            harness_telemetry.append_usage("day", sources_loaded=1, source_bytes=100, wall_ms=1, ledger=ledger)
            harness_telemetry.append_usage("day", sources_loaded=1, source_bytes=300, wall_ms=1, ledger=ledger)
            harness_telemetry.append_usage("create", sources_loaded=2, source_bytes=900, wall_ms=1, ledger=ledger)
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write("{not json\n")
            entries = harness_telemetry.load_usage(ledger)
            self.assertEqual(len(entries), 3)
            hotspots = harness_telemetry.usage_hotspots(entries, top=5)
            self.assertEqual(
                hotspots,
                [
                    {"command": "create", "runs": 1, "mean_source_bytes": 900},
                    {"command": "day", "runs": 2, "mean_source_bytes": 200},
                ],
            )

    def test_missing_usage_ledger_loads_empty(self):
        self.assertEqual(harness_telemetry.load_usage(Path("/nonexistent/usage.jsonl")), [])


if __name__ == "__main__":
    unittest.main()
