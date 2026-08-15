from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import pm_decision_router


class TestPMDecisionRouter(unittest.TestCase):
    def assert_intent(self, text: str, intent: str, target: str) -> None:
        routed = pm_decision_router.route_text(text)
        self.assertEqual(routed.intent, intent)
        self.assertEqual(routed.routing_target, target)
        self.assertIn(routed.intent, pm_decision_router.INTENTS)

    def test_existing_task_signal_routes_to_task_update(self):
        self.assert_intent(
            "PLAN-009 is blocked until the platform lead confirms the engineering DRI.",
            "task_update",
            ".agent/workflows/track.md",
        )

    def test_raw_action_note_routes_to_new_task_with_blocking_questions(self):
        routed = pm_decision_router.route_text("Need to follow up with Design by Friday on the prototype.")
        self.assertEqual(routed.intent, "new_task")
        self.assertEqual(routed.routing_target, ".agent/workflows/track.md")
        self.assertTrue(routed.blocking_questions)

    def test_discovery_signal_routes_to_discover(self):
        self.assert_intent(
            "Run discovery on the prior auth problem space and map assumptions for an experiment.",
            "discovery",
            ".agent/workflows/discover.md",
        )

    def test_scope_creep_routes_to_scope_challenge(self):
        routed = pm_decision_router.route_text(
            "Kari wants me to become the Jira requirements writer for a legacy UI launch."
        )
        self.assertEqual(routed.intent, "scope_challenge")
        self.assertEqual(routed.routing_target, ".agent/workflows/track.md")
        self.assertTrue(any("Priority Gate" in item for item in routed.candidate_updates))

    def test_vague_input_asks_user(self):
        routed = pm_decision_router.route_text("Help with the product thing.")
        self.assertEqual(routed.intent, "ask_user")
        self.assertEqual(routed.routing_target, ".agent/workflows/chat.md")
        self.assertTrue(routed.blocking_questions)

    def test_prioritization_signal_routes_to_prioritize(self):
        self.assert_intent(
            "Prioritize this backlog with RICE and draw a cut line based on capacity.",
            "prioritize",
            ".agent/workflows/prioritize.md",
        )

    def test_create_doc_signal_routes_to_create(self):
        self.assert_intent(
            "Write a PRD for the checkout flow.",
            "create_doc",
            ".agent/workflows/create.md",
        )

    def test_decision_signal_routes_to_decision_log(self):
        self.assert_intent(
            "We decided to go with option B for the launch path.",
            "decision_log",
            ".agent/workflows/track.md",
        )

    def test_archive_only_signal_routes_to_archive(self):
        self.assert_intent(
            "FYI this is for reference only, no action needed.",
            "archive_only",
            ".agent/workflows/archive.md",
        )


if __name__ == "__main__":
    unittest.main()
