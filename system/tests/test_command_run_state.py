from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import command_run_state


class TestCommandRunState(unittest.TestCase):
    def test_successful_source_scope_checkpoint_is_reusable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            command_run_state.record_run(
                root,
                command="week",
                mode="week",
                run_id="run-1",
                completed_at="2026-06-27T12:00:00Z",
                sources=[
                    {
                        "source": "slack",
                        "platform": "slack",
                        "scope": "people: requester",
                        "status": "completed",
                        "processed_through_at": "2026-06-27T11:59:00Z",
                    }
                ],
            )

            checkpoint = command_run_state.latest_successful_checkpoint(root, "slack", "people: requester")

            self.assertEqual(command_run_state.isoformat_utc(checkpoint), "2026-06-27T11:59:00Z")

    def test_failed_or_skipped_source_does_not_create_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            command_run_state.record_run(
                root,
                command="week",
                mode="week",
                run_id="run-1",
                completed_at="2026-06-27T12:00:00Z",
                sources=[
                    {
                        "source": "teams",
                        "platform": "teams",
                        "scope": "DM: requester",
                        "status": "failed",
                    },
                    {
                        "source": "granola",
                        "platform": "granola",
                        "scope": "local app",
                        "status": "skipped",
                    },
                ],
            )

            self.assertIsNone(command_run_state.latest_successful_checkpoint(root, "teams", "DM: requester"))
            self.assertIsNone(command_run_state.latest_successful_checkpoint(root, "granola", "local app"))


if __name__ == "__main__":
    unittest.main()
