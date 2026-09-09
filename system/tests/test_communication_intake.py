#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from system.scripts import communication_intake, task_store


class TestCommunicationIntake(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        (self.root / "5. Trackers" / "tasks").mkdir(parents=True)
        (self.root / "5. Trackers" / "workstreams").mkdir(parents=True)
        (self.root / "4. People").mkdir(parents=True)
        (self.root / "3. Meetings" / "chat-transcripts").mkdir(parents=True)
        (self.root / "3. Meetings" / "reports").mkdir(parents=True)
        (self.root / "system" / "scripts").mkdir(parents=True)

        # Setup base PEOPLE.md
        (self.root / "4. People" / "PEOPLE.md").write_text(
            "# People\n\n## Captios Partners (Consulting Team)\n\n| Name | Role | Focus |\n|:---|:---|:---|\n| **Ernesto Rodriguez** | Lead | PM |\n\n---\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_full_communication_intake_pipeline(self):
        payload = {
            "platform": "teams",
            "scope": "captios-partners-p-hf-feedx",
            "sender": "Mark Persaud",
            "timestamp": "2026-09-09T15:49:00-05:00",
            "extracted_text": "Adding Ernesto Rodriguez - We'll spend some time getting you up to speed on our FeedX product soon!",
            "task": {
                "title": "FeedX Product Onboarding Sync with Mark Persaud",
                "prefix": "CAPT",
                "lane": "next",
                "priority": "next",
                "due": "2026-09-15",
                "owner": "Ernesto Rodriguez",
                "workstream": "captios-internal-feedx",
            },
            "stakeholder": {
                "name": "Mark Persaud",
                "role": "Product Lead",
                "org": "Captios Partners",
                "notes": "FeedX Product Lead; p-hf-feedx channel owner",
            },
            "workstream": {
                "slug": "captios-internal-feedx",
                "title": "Captios — FeedX Product Onboarding",
                "client": "Captios Partners",
            },
            "peripheral_signals": ["2 unread Activity notifications"],
        }

        result = communication_intake.process_communication_intake(payload, root=self.root)

        self.assertTrue(result.ok)
        self.assertEqual(result.platform, "teams")
        self.assertEqual(result.scope, "captios-partners-p-hf-feedx")
        self.assertEqual(result.task_id, "CAPT-001-feedx-product-onboarding-sync")

        # Verify task file created
        task_path = self.root / result.task_path
        self.assertTrue(task_path.exists())
        task_txt = task_path.read_text(encoding="utf-8")
        self.assertIn("title: 'FeedX Product Onboarding Sync with Mark Persaud'", task_txt)
        self.assertIn("task_id: CAPT-001-feedx-product-onboarding-sync", task_txt)
        self.assertIn("owner: Ernesto Rodriguez", task_txt)
        self.assertIn("due: 2026-09-15", task_txt)
        self.assertIn("## Summary", task_txt)
        self.assertIn("## Context", task_txt)
        self.assertIn("## Next actions", task_txt)

        # Verify transcript created
        transcript_path = self.root / result.transcript_path
        self.assertTrue(transcript_path.exists())
        tr_txt = transcript_path.read_text(encoding="utf-8")
        self.assertIn("# Communication Transcript — teams — captios-partners-p-hf-feedx", tr_txt)
        self.assertIn("Mark Persaud", tr_txt)
        self.assertIn("Peripheral Signal: 2 unread Activity notifications", tr_txt)

        # Verify run report created
        report_path = self.root / result.run_report_path
        self.assertTrue(report_path.exists())
        rep_txt = report_path.read_text(encoding="utf-8")
        self.assertIn("# Teams Run Report: FeedX Product Onboarding Sync with Mark Persaud", rep_txt)

        # Verify chat run report created
        chat_rep_path = self.root / result.chat_report_path
        self.assertTrue(chat_rep_path.exists())

        # Verify stakeholder profile created and PEOPLE.md updated
        stakeholder_path = self.root / result.stakeholder_path
        self.assertTrue(stakeholder_path.exists())
        s_txt = stakeholder_path.read_text(encoding="utf-8")
        self.assertIn("title: Mark Persaud", s_txt)
        self.assertIn("role: Product Lead", s_txt)

        people_index_txt = (self.root / "4. People" / "PEOPLE.md").read_text(encoding="utf-8")
        self.assertIn("Mark Persaud", people_index_txt)

        # Verify workstream created
        ws_path = self.root / result.workstream_path
        self.assertTrue(ws_path.exists())
        ws_txt = ws_path.read_text(encoding="utf-8")
        self.assertIn("title: 'Captios — FeedX Product Onboarding'", ws_txt)

        # Verify Task Master rebuild
        tm_path = self.root / "5. Trackers" / "TASK_MASTER.md"
        self.assertTrue(tm_path.exists())
        tm_txt = tm_path.read_text(encoding="utf-8")
        self.assertIn("FeedX Product Onboarding Sync with Mark Persaud", tm_txt)

        # Verify preview links present
        self.assertIn("Transcript", result.preview_links)
        self.assertIn("Task Detail", result.preview_links)
        self.assertIn("Task Master", result.preview_links)

        # Verify workstream snapshot formatted
        self.assertIn("### Captios — FeedX Product Onboarding (`captios-internal-feedx`)", result.workstream_snapshot)

    def test_auto_increments_task_number(self):
        # Pre-create CAPT-001 and CAPT-002
        (self.root / "5. Trackers" / "tasks" / "capt-001-test.md").write_text(
            "---\ntask_id: CAPT-001-test\ntitle: Test 1\n---\n", encoding="utf-8"
        )
        (self.root / "5. Trackers" / "tasks" / "capt-002-test.md").write_text(
            "---\ntask_id: CAPT-002-test\ntitle: Test 2\n---\n", encoding="utf-8"
        )

        next_num = communication_intake.find_next_task_number(self.root, "CAPT")
        self.assertEqual(next_num, 3)

        payload = {
            "platform": "teams",
            "scope": "test-channel",
            "sender": "Alice",
            "extracted_text": "Follow up with Bob",
            "task": {
                "title": "Follow up with Bob",
                "prefix": "CAPT",
            },
        }
        result = communication_intake.process_communication_intake(payload, root=self.root)
        self.assertEqual(result.task_id, "CAPT-003-follow-up-with-bob")
    def test_cli_flags_and_slack_platform(self):
        payload = {
            "platform": "slack",
            "scope": "proj-feedx",
            "sender": "Carol",
            "extracted_text": "Review PR for FeedX API",
            "task": {
                "title": "Review FeedX API PR",
                "prefix": "FEED",
                "lane": "today",
                "priority": "now",
            },
        }
        result = communication_intake.process_communication_intake(payload, root=self.root)
        self.assertTrue(result.ok)
        self.assertEqual(result.platform, "slack")
        self.assertEqual(result.task_id, "FEED-001-review-feedx-api-pr")
        self.assertTrue((self.root / result.transcript_path).exists())
        self.assertTrue((self.root / result.run_report_path).exists())
        self.assertTrue((self.root / result.chat_report_path).exists())


if __name__ == "__main__":
    unittest.main()
