import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import transcript_pipeline


class TestTranscriptPipeline(unittest.TestCase):
    def meeting_date(self, offset_days: int = 0) -> str:
        return (dt.date.today() - dt.timedelta(days=offset_days)).isoformat()

    def make_repo(self, tmpdir):
        root = Path(tmpdir)
        for folder in (
            "0. Incoming",
            "1. Company",
            "2. Products/partners",
            "3. Meetings/transcripts",
            "3. Meetings/summaries",
            "3. Meetings/reports",
            "4. People",
            "5. Trackers",
        ):
            (root / folder).mkdir(parents=True, exist_ok=True)
        (root / "5. Trackers" / "TASK_MASTER.md").write_text(
            "| ID | Task |\n| DEMO-034 | Prepare starter stories |\n",
            encoding="utf-8",
        )
        (root / "4. People" / "manager-profile.md").write_text("# Manager Profile\n", encoding="utf-8")
        return root

    def test_business_days_ago_skips_weekends(self):
        monday = dt.date(2026, 4, 27)
        self.assertEqual(transcript_pipeline.business_days_ago(1, today=monday), dt.date(2026, 4, 24))
        self.assertEqual(transcript_pipeline.business_days_ago(10, today=monday), dt.date(2026, 4, 13))

    def test_sanitize_filename_and_summary_path(self):
        self.assertEqual(transcript_pipeline.sanitize_filename("A/B: C?  D"), "AB C D")
        path = Path("2026-04-24_My Meeting Name.txt")
        self.assertEqual(
            transcript_pipeline.slugify_summary_name(path),
            "2026-04-24_My-Meeting-Name.md",
        )

    def test_prepare_creates_manifest_and_packet_once(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            transcript = root / f"3. Meetings/transcripts/{self.meeting_date()}_Manager Partner Sync.txt"
            transcript.write_text(
                "Direct manager and user discussed DEMO-034 and partner access request.",
                encoding="utf-8",
            )

            first = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)
            second = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)

            self.assertEqual(len(first["packets"]), 1)
            self.assertEqual(len(second["packets"]), 0)
            self.assertEqual(second["skipped"][0]["reason"], "packet_already_ready")

            manifest = json.loads((root / "3. Meetings/transcripts/_manifest.json").read_text(encoding="utf-8"))
            entries = list(manifest["transcripts"].values())
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["status"], "packet_ready")
            self.assertTrue((root / entries[0]["packet_path"]).exists())

    def test_existing_summary_prevents_packet_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            transcript = root / f"3. Meetings/transcripts/{self.meeting_date()}_Existing Summary.txt"
            transcript.write_text("Already handled.", encoding="utf-8")
            (root / f"3. Meetings/summaries/{self.meeting_date()}_Existing-Summary.md").write_text("# Summary\n", encoding="utf-8")

            result = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)

            self.assertEqual(result["packets"], [])
            self.assertEqual(result["skipped"][0]["reason"], "summary_exists_or_already_processed")

    def test_teams_bridge_failure_is_recorded_as_unavailable(self):
        def fake_run(cmd, root, timeout=45):
            if any(part.endswith("beats.py") for part in cmd):
                return {"command": cmd, "returncode": 1, "stdout": "", "stderr": "denied"}
            return {"command": cmd, "returncode": 0, "stdout": "ok", "stderr": ""}

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            with patch.object(transcript_pipeline, "run_command", side_effect=fake_run):
                sources = transcript_pipeline.collect_sources(root, skip_import=False)

            self.assertEqual(sources["teams"]["status"], "unavailable")
            self.assertIn("remediation", sources["teams"])

    def test_native_mcp_quill_mode_does_not_launch_sandboxed_bridge(self):
        commands = []

        def fake_run(cmd, root, timeout=45):
            commands.append(cmd)
            return {"command": cmd, "returncode": 0, "stdout": "ok", "stderr": ""}

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            with patch.object(transcript_pipeline, "run_command", side_effect=fake_run):
                sources = transcript_pipeline.collect_sources(root, quill_mode="native-mcp")

        flattened = [part for command in commands for part in command]
        self.assertEqual(sources["quill"]["status"], "ok")
        self.assertEqual(sources["quill"]["transport"], "native_mcp")
        self.assertNotIn("system/scripts/quill_mcp_client.py", flattened)
        self.assertNotIn("system/scripts/transcript_fetcher.py", flattened)

    def test_validate_rejects_missing_required_summary_markers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            transcript = root / f"3. Meetings/transcripts/{self.meeting_date()}_Manager Partner Sync.txt"
            transcript.write_text(
                "Direct manager discussed partner access request and commercial risk.",
                encoding="utf-8",
            )
            prepared = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)
            run_id = prepared["run_id"]

            packet = json.loads((root / prepared["packets"][0]["path"]).read_text(encoding="utf-8"))
            summary_path = root / packet["transcript"]["expected_summary_path"]
            summary_path.write_text("# Meeting Summary\n\nNo required contract markers.\n", encoding="utf-8")

            result = transcript_pipeline.validate(root, run_id, json_output=False)

            self.assertFalse(result["ok"])
            self.assertIn("missing_source_hash", result["results"][0]["errors"])
            self.assertTrue(any(error.startswith("missing_marker:") for error in result["results"][0]["errors"]))

    def test_validate_accepts_hybrid_summary_contract(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            transcript = root / f"3. Meetings/transcripts/{self.meeting_date()}_Standalone Sync.txt"
            transcript.write_text("General peer sync with no external access terms.", encoding="utf-8")
            prepared = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)
            run_id = prepared["run_id"]
            packet = json.loads((root / prepared["packets"][0]["path"]).read_text(encoding="utf-8"))
            source_hash = packet["transcript"]["content_sha256"]
            summary_path = root / packet["transcript"]["expected_summary_path"]
            summary_path.write_text(
                "\n".join(
                    [
                        "# Meeting Summary",
                        "**Source Transcript**: x",
                        f"**Transcript SHA256**: {source_hash}",
                        f"**Pipeline Run ID**: {run_id}",
                        "## Summary",
                        "- Point",
                        "## Routed Updates",
                        "- No durable update required",
                        "## Key Evidence",
                        "- Evidence",
                    ]
                ),
                encoding="utf-8",
            )

            result = transcript_pipeline.validate(root, run_id, json_output=False)

            self.assertTrue(result["ok"])
            manifest = json.loads((root / "3. Meetings/transcripts/_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(list(manifest["transcripts"].values())[0]["status"], "validated")

    def test_recent_uses_only_validated_manifest_summaries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self.make_repo(tmpdir)
            transcript = root / f"3. Meetings/transcripts/{self.meeting_date()}_Validated Sync.txt"
            transcript.write_text("General peer sync.", encoding="utf-8")
            prepared = transcript_pipeline.prepare(root, 10, json_output=False, skip_import=True)
            run_id = prepared["run_id"]
            packet = json.loads((root / prepared["packets"][0]["path"]).read_text(encoding="utf-8"))
            source_hash = packet["transcript"]["content_sha256"]
            summary_path = root / packet["transcript"]["expected_summary_path"]
            summary_path.write_text(
                "\n".join(
                    [
                        "# Meeting Summary",
                        f"**Date**: {self.meeting_date()}",
                        "**Participants**: Sample User",
                        "**Source Transcript**: x",
                        f"**Transcript SHA256**: {source_hash}",
                        f"**Pipeline Run ID**: {run_id}",
                        "## Summary",
                        "- Validated point",
                        "## Action Items",
                        "| Owner | Action | Due Date |",
                        "| --- | --- | --- |",
                        f"| Sample User | Follow up | {(dt.date.today() + dt.timedelta(days=3)).isoformat()} |",
                        "## Routed Updates",
                        "- No durable update required",
                        "## Key Evidence",
                        "- Evidence",
                    ]
                ),
                encoding="utf-8",
            )
            (root / f"3. Meetings/summaries/{self.meeting_date()}_Draft-Sync.md").write_text(
                "# Draft Sync\n\n## Summary\n- Should not appear\n",
                encoding="utf-8",
            )
            transcript_pipeline.validate(root, run_id, json_output=False)

            output = transcript_pipeline.recent(root, 5, markdown=True)

            self.assertIn("Validated-Sync", output)
            self.assertIn("Validated point", output)
            self.assertNotIn("Draft-Sync", output)


if __name__ == "__main__":
    unittest.main()
