from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import chat_intake_state, command_run_state


class TestChatIntakeState(unittest.TestCase):
    def run_window(self, root: Path, platform: str, scope: str = "demo scope", days: int | None = None):
        args = SimpleNamespace(
            repo=str(root),
            manifest=None,
            platform=platform,
            scope=scope,
            business_days=None,
            days=days,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            return_code = chat_intake_state.command_window(args)
        return return_code, json.loads(output.getvalue())

    def run_chunks(
        self,
        root: Path,
        platform: str = "slack",
        scope: str = "to:me",
        start: str | None = None,
        end: str | None = None,
        chunk_hours: int | None = None,
    ):
        args = SimpleNamespace(
            repo=str(root),
            manifest=None,
            platform=platform,
            scope=scope,
            start=start,
            end=end,
            business_days=None,
            days=None,
            chunk_hours=chunk_hours,
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            return_code = chat_intake_state.command_chunks(args)
        return return_code, json.loads(output.getvalue())

    def test_supported_platforms_include_mcp_communication_sources(self):
        self.assertEqual(
            chat_intake_state.VALID_PLATFORMS,
            {"slack", "teams", "outlook", "calendar"},
        )

    def test_backward_windows_apply_to_slack_teams_and_outlook(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for platform in ("slack", "teams", "outlook"):
                with self.subTest(platform=platform):
                    return_code, result = self.run_window(root, platform)

                    self.assertEqual(return_code, 0)
                    self.assertTrue(result["ok"])
                    self.assertEqual(result["window_direction"], "backward")
                    self.assertEqual(result["window_source"], "default_5_business_days")
                    self.assertEqual(result["platform"], platform)

    def test_calendar_window_is_forward_looking(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            return_code, result = self.run_window(root, "calendar", days=7)

            self.assertEqual(return_code, 0)
            self.assertTrue(result["ok"])
            self.assertEqual(result["window_direction"], "backward_plus_forward")
            self.assertEqual(result["window_source"], "default_5_business_days_plus_7_calendar_days_forward")
            self.assertGreater(result["effective_end_at"], result["effective_start_at"])
            self.assertIsNotNone(result["lookahead_start_at"])
            self.assertIsNotNone(result["lookahead_end_at"])

    def test_command_run_checkpoint_shortens_backward_window(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            completed_at = dt.datetime.now(dt.timezone.utc)
            processed_at = completed_at - dt.timedelta(minutes=5)
            completed_at_text = chat_intake_state.isoformat_utc(completed_at)
            processed_at_text = chat_intake_state.isoformat_utc(processed_at)
            command_run_state.record_run(
                root,
                command="week",
                mode="week",
                run_id="run-1",
                completed_at=completed_at_text,
                sources=[
                    {
                        "source": "slack",
                        "platform": "slack",
                        "scope": "demo scope",
                        "status": "completed",
                        "processed_through_at": processed_at_text,
                    }
                ],
            )

            return_code, result = self.run_window(root, "slack")

            self.assertEqual(return_code, 0)
            self.assertTrue(result["ok"])
            self.assertEqual(result["window_source"], "command_run_last_successful_processed_at")
            self.assertEqual(result["effective_start_at"], processed_at_text)

    def test_failed_command_run_checkpoint_does_not_shorten_window(self):
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
                        "scope": "demo scope",
                        "status": "failed",
                    }
                ],
            )

            return_code, result = self.run_window(root, "teams")

            self.assertEqual(return_code, 0)
            self.assertTrue(result["ok"])
            self.assertEqual(result["window_source"], "default_5_business_days")
            self.assertIsNone(result["command_run_last_successful_processed_at"])

    def test_manifest_record_is_platform_specific_for_new_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for platform in ("outlook", "calendar"):
                with self.subTest(platform=platform):
                    args = SimpleNamespace(
                        repo=str(root),
                        manifest=None,
                        platform=platform,
                        scope="demo scope",
                        run_id=f"run-{platform}",
                        latest_source_timestamp="2026-05-06T12:00:00Z",
                        transcript_path=[f"3. Meetings/chat-transcripts/{platform}/demo.md"],
                        run_report_path=[f"3. Meetings/reports/{platform}-runs/demo.md"],
                    )
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        return_code = chat_intake_state.command_record(args)

                    self.assertEqual(return_code, 0)
                    result = json.loads(output.getvalue())
                    self.assertEqual(result["scope_key"], f"{platform}:demo-scope")

    def test_slack_chunks_default_to_daily_windows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            return_code, result = self.run_chunks(
                root,
                start="2026-04-16T05:00:00Z",
                end="2026-04-19T05:00:00Z",
            )

            self.assertEqual(return_code, 0)
            self.assertTrue(result["ok"])
            self.assertEqual(result["chunk_hours"], 24)
            self.assertEqual(result["chunk_count"], 3)
            self.assertEqual(result["read_order"], "oldest_to_newest")
            self.assertEqual(result["chunks"][0]["slack_query_date_hint"], "after:2026-04-16 before:2026-04-17")

    def test_slack_chunks_can_split_dense_windows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            return_code, result = self.run_chunks(
                root,
                start="2026-04-16T05:00:00Z",
                end="2026-04-17T05:00:00Z",
                chunk_hours=12,
            )

            self.assertEqual(return_code, 0)
            self.assertTrue(result["ok"])
            self.assertEqual(result["chunk_count"], 2)
            self.assertEqual(result["chunks"][0]["end_epoch"], result["chunks"][1]["start_epoch"])

    def test_chunks_reject_non_positive_chunk_hours(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            return_code, result = self.run_chunks(
                root,
                start="2026-04-16T05:00:00Z",
                end="2026-04-17T05:00:00Z",
                chunk_hours=0,
            )

            self.assertEqual(return_code, 2)
            self.assertFalse(result["ok"])
            self.assertIn("invalid_chunk_hours", result["issues"])


if __name__ == "__main__":
    unittest.main()
