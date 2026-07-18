from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from system.scripts import critical_commitment_refresh as ccr


class TestCriticalCommitmentRefresh(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "system" / "config").mkdir(parents=True)
        (root / "3. Meetings" / "chat-transcripts").mkdir(parents=True)
        (root / "5. Trackers" / "critical").mkdir(parents=True)
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        template = Path("system/config/critical_intake.template.json")
        (root / template).write_text(Path(template).read_text(encoding="utf-8"), encoding="utf-8")
        return root

    def test_manifest_scopes_are_selected_automatically(self):
        root = self.make_root()
        manifest = {
            "schema_version": 1,
            "scopes": {
                "slack:people-requester": {
                    "platform": "slack",
                    "scope": "people: requester",
                    "last_successful_processed_at": "2026-06-27T04:12:00Z",
                }
            },
        }
        (root / "3. Meetings" / "chat-transcripts" / "_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        health = {item.source: item for item in ccr.build_health(root)}

        self.assertEqual(health["slack"].status, "healthy")
        self.assertEqual(health["slack"].configured_scope, "people: requester")
        self.assertFalse(health["slack"].requires_user_decision)

    def test_missing_expected_integration_prompts_user(self):
        root = self.make_root()

        plan = ccr.build_plan(root, "day")

        self.assertTrue(plan["should_pause_for_user"])
        self.assertTrue(any(item["source"] == "teams" and item["what_failed"] == "missing_scope" for item in plan["user_prompts"]))

    def test_local_quill_export_satisfies_core_source_health(self):
        root = self.make_root()
        export = root / "3. Meetings" / "transcripts" / "quill"
        export.mkdir(parents=True)
        (export / "product-review.md").write_text("# Product review\n", encoding="utf-8")

        health = ccr.source_health(root, "quill", {"enabled": True}, {})

        self.assertEqual(health.status, "healthy")
        self.assertFalse(health.requires_user_decision)

    def test_boss_callout_ranks_above_ordinary_stale_work(self):
        root = self.make_root()
        (root / "5. Trackers" / "TASK_MASTER.md").write_text(
            "\n".join(
                [
                    "| ID | Task | Owner | Due | Status |",
                    "|:---|:-----|:------|:----|:-------|",
                    "| [PLAN-001](tasks/PLAN-001.md) | Ordinary stale internal cleanup | Owner | 2026-01-01 | Active |",
                    "| [PLAN-002](tasks/PLAN-002.md) | Manager requested readiness by 2026-07-10 | Owner | 2026-07-10 | Active |",
                ]
            ),
            encoding="utf-8",
        )

        ranked = ccr.build_ranked_items(root, "day")

        self.assertEqual(ranked[0].task_id, "PLAN-002")
        self.assertEqual(ranked[0].authority_tier, "direct_manager")

    def test_external_commitment_ranks_above_internal_undated_work(self):
        root = self.make_root()
        (root / "5. Trackers" / "TASK_MASTER.md").write_text(
            "\n".join(
                [
                    "| ID | Task | Owner | Due | Status |",
                    "|:---|:-----|:------|:----|:-------|",
                    "| [TASK-001](tasks/TASK-001.md) | Internal backlog cleanup | Owner | TBD | Active |",
                    "| [TASK-002](tasks/TASK-002.md) | Customer testing commitment by 2026-07-03 | Owner | 2026-07-03 | Active |",
                ]
            ),
            encoding="utf-8",
        )

        ranked = ccr.build_ranked_items(root, "week")

        self.assertEqual(ranked[0].task_id, "TASK-002")
        self.assertEqual(ranked[0].commitment_type, "external_customer")

    def test_completion_states_distinguish_explicit_from_implied(self):
        self.assertEqual(ccr.completion_state("ML-2288 completed and closed"), "explicit_complete")
        self.assertEqual(ccr.completion_state("draft v1 complete and ready for review"), "implied_complete")
        self.assertEqual(ccr.completion_state("still active"), "open")

    def test_third_party_mutation_policy_is_visible(self):
        root = self.make_root()

        plan = ccr.build_plan(root, "boss")

        self.assertIn("send", plan["third_party_mutations_require_current_turn_confirmation"])
        self.assertIn("slack", plan["read_only_sources"])


if __name__ == "__main__":
    unittest.main()
