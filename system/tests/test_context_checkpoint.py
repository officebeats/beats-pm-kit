"""Tests for phase-aware, loss-aware checkpoints."""

from __future__ import annotations

import hashlib
import json
import shutil
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


class TestAppendOnlyAnchors(unittest.TestCase):

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.checkpoint_dir = self.root / ".beats" / "context" / "checkpoints"

    def tearDown(self):
        shutil.rmtree(self.root)

    def create(self, workflow: str = "day", phase: str = "planning") -> Path:
        return context_checkpoint.create_checkpoint(
            complete_payload(),
            workflow=workflow,
            phase=phase,
            context_percent=70.0,
            projected_next_phase_tokens=1000,
            remaining_tokens=50000,
            root=self.root,
        )

    def test_two_checkpoints_produce_two_anchors_first_anchor_unchanged(self):
        first = self.create(workflow="day")
        anchors_path = self.checkpoint_dir / context_checkpoint.ANCHORS_FILENAME
        after_first = anchors_path.read_bytes()

        second = self.create(workflow="week", phase="creation")
        after_second = anchors_path.read_bytes()

        self.assertNotEqual(first, second)
        self.assertTrue(first.is_file())
        self.assertTrue(second.is_file())
        # Append-only: the file after the second write starts with the exact
        # bytes it had after the first write.
        self.assertTrue(after_second.startswith(after_first))
        headings = [
            line
            for line in after_second.decode("utf-8").split("\n")
            if line.startswith(context_checkpoint.ANCHOR_HEADING_PREFIX)
        ]
        self.assertEqual(len(headings), 2)
        self.assertEqual(context_checkpoint.verify_anchors(anchors_path), 2)

    def test_anchor_records_checkpoint_document_hash(self):
        output = self.create()
        anchors_text = (self.checkpoint_dir / context_checkpoint.ANCHORS_FILENAME).read_text(
            encoding="utf-8"
        )
        expected = hashlib.sha256(output.read_bytes()).hexdigest()
        self.assertIn(f"- checkpoint_file: {output.name}", anchors_text)
        self.assertIn(f"- checkpoint_sha256: {expected}", anchors_text)

    def test_mutated_anchor_blocks_next_checkpoint(self):
        self.create()
        anchors_path = self.checkpoint_dir / context_checkpoint.ANCHORS_FILENAME
        tampered = anchors_path.read_text(encoding="utf-8").replace(
            "- workflow: day", "- workflow: rewritten"
        )
        anchors_path.write_text(tampered, encoding="utf-8")

        with self.assertRaises(ValueError):
            self.create(workflow="week")
        # The guard fired before the second JSON document was written.
        json_files = list(self.checkpoint_dir.glob("*.json"))
        self.assertEqual(len(json_files), 1)


if __name__ == "__main__":
    unittest.main()
