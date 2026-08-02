"""Tests for phase-aware, loss-aware checkpoints."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from system.scripts import context_checkpoint


def complete_payload() -> dict:
    return {
        "goal": "Create a cited brief",
        "decisions": ["Use raw source A"],
        "exact_stakeholder_language": ["Do not change these words"],
        "source_ids": ["ctx-0123456789abcdef"],
        "artifacts": ["artifact.md"],
        "open_questions": [],
        "failed_attempts": [],
        "verification_state": "sources checked",
        "next_action": "draft",
        "recent_complete_turn": "User: proceed\nAssistant: discovery complete",
        "tool_pairs_complete": True,
    }


class TestContextCheckpoint(unittest.TestCase):
    def test_threshold_requires_boundary(self):
        self.assertFalse(
            context_checkpoint.should_checkpoint(
                context_percent=90,
                projected_next_phase_tokens=100,
                remaining_tokens=1000,
                at_phase_boundary=False,
            )
        )
        self.assertTrue(
            context_checkpoint.should_checkpoint(
                context_percent=65,
                projected_next_phase_tokens=100,
                remaining_tokens=1000,
                at_phase_boundary=True,
            )
        )
        self.assertTrue(
            context_checkpoint.should_checkpoint(
                context_percent=40,
                projected_next_phase_tokens=1200,
                remaining_tokens=1000,
                at_phase_boundary=True,
            )
        )

    def test_checkpoint_preserves_required_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = context_checkpoint.create_checkpoint(
                complete_payload(),
                workflow="create",
                phase="discovery",
                context_percent=70,
                projected_next_phase_tokens=500,
                remaining_tokens=1000,
                root=Path(tmp),
            )
            document = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(document["exact_stakeholder_language"], ["Do not change these words"])
            self.assertEqual(document["source_ids"], ["ctx-0123456789abcdef"])
            self.assertTrue(document["tool_pairs_complete"])

    def test_incomplete_tool_pair_is_rejected(self):
        payload = complete_payload()
        payload["tool_pairs_complete"] = False
        with self.assertRaisesRegex(ValueError, "tool-call/result"):
            context_checkpoint.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()
