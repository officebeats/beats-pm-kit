import datetime as dt
import tempfile
import unittest
from pathlib import Path

from system.scripts import task_intake_fast


class TestTaskIntakeFast(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / ".agent" / "cache").mkdir(parents=True)
        tasks_dir = root / "5. Trackers" / "tasks"
        tasks_dir.mkdir(parents=True)
        (root / "0. Incoming" / "raw").mkdir(parents=True)
        (root / "5. Trackers" / "TASK_MASTER.md").write_text(
            "\n".join(
                [
                    "# TASK MASTER",
                    "",
                    "| ID | Task | Owner | Due | Status |",
                    "|:---|:-----|:------|:----|:-------|",
                    "| [PARU-014](tasks/PARU-014.md) | **Review DS Guideline Recommendation work** — GLR ramp | Ernesto | 2026-05-13 | 🔴 Active — GLR production target needs context |",
                ]
            ),
            encoding="utf-8",
        )
        (tasks_dir / "PARU-014.md").write_text(
            "\n".join(
                [
                    "# PARU-014 — Review DS Guideline Recommendation work",
                    "",
                    "> **Status:** 🔴 Active — GLR production target needs context",
                    "> **Owner:** Ernesto Rodriguez",
                    "> **Last Updated:** 2026-06-17",
                    "",
                    "## Context & Background",
                    "",
                    "Guideline Recommender, GLR, reasoning service, IAD, Indicia, Abbey, tenant-specific configuration, and June 30 production target.",
                    "",
                    "## 👥 Stakeholders",
                    "",
                    "| Role | Person | Context |",
                    "|:-----|:-------|:--------|",
                    "| Consult | Abbey Armstead | IAD / Indicia context |",
                    "",
                    "## 📎 References",
                    "",
                    "| Type | Source | Link |",
                    "|:-----|:-------|:-----|",
                    "",
                    "## 📈 Progress Log",
                    "",
                    "| Date | Source | Update / Outcome | Status |",
                    "|:-----|:-------|:-----------------|:-------|",
                    "| 2026-06-17 | Calendar | Tavis GLR follow-up is next checkpoint. | 🔴 |",
                    "",
                    "## ✅ Subtasks",
                    "",
                    "- [ ] Confirm GLR production path.",
                ]
            ),
            encoding="utf-8",
        )
        return root

    def test_updates_existing_task_and_preserves_raw_evidence(self):
        root = self.make_repo()
        raw = "\n".join(
            [
                "Abbey Armstead",
                "Ernesto Rodriguez 2:00 PM",
                "Paru said Ernesto will set-up some time to talk to you about guideline/tenant specific configuration.",
                "Abbey 3:30 PM",
                "I think this was all referring to the set up we are doing to provide LLM reasoning to IAD.",
                "https://hbmchat.slack.com/archives/D0BC5KGDT8T/p1782160177453819",
            ]
        )
        result = task_intake_fast.run_intake(
            root=root,
            raw_text=raw,
            source="Slack DM with Abbey",
            captured_at=dt.datetime(2026, 6, 22, 15, 35, tzinfo=dt.timezone.utc),
        )

        self.assertEqual(result.mode, "updated_existing")
        self.assertEqual(result.task_id, "PARU-014")
        self.assertEqual(result.display_label, "IAD Indicia guideline tenant configuration")
        source_note = root / result.source_note_path
        task_file = root / result.task_path
        task_master = (root / "5. Trackers" / "TASK_MASTER.md").read_text(encoding="utf-8")
        self.assertTrue(source_note.exists())
        note_text = source_note.read_text(encoding="utf-8")
        self.assertIn("## Raw Evidence", note_text)
        self.assertIn("# IAD Indicia guideline tenant configuration", note_text)
        self.assertIn("Ernesto Rodriguez 2:00 PM", note_text)
        self.assertIn("https://hbmchat.slack.com/archives/D0BC5KGDT8T/p1782160177453819", note_text)
        self.assertIn("## Summary", note_text)
        updated_task = task_file.read_text(encoding="utf-8")
        self.assertIn("Source Note", updated_task)
        self.assertIn("IAD Indicia guideline tenant configuration", updated_task)
        self.assertIn("🟡 Updated", task_master)
        self.assertTrue(result.triage_deferred)

    def test_creates_candidate_task_when_match_is_low_confidence(self):
        root = self.make_repo()
        raw = "Random stakeholder note: ask Finance about lunch budget next month."
        result = task_intake_fast.run_intake(
            root=root,
            raw_text=raw,
            source="Pasted note",
            captured_at=dt.datetime(2026, 6, 22, 16, 0, tzinfo=dt.timezone.utc),
        )

        self.assertEqual(result.mode, "created_candidate")
        self.assertEqual(result.task_id, "INBOX-001")
        task_file = root / result.task_path
        source_note = root / result.source_note_path
        self.assertTrue(task_file.exists())
        self.assertTrue(source_note.exists())
        self.assertIn("Random stakeholder note", source_note.read_text(encoding="utf-8"))
        self.assertIn("Fast Intake Triage", (root / "5. Trackers" / "TASK_MASTER.md").read_text(encoding="utf-8"))
        self.assertIn("# Random stakeholder note ask", task_file.read_text(encoding="utf-8"))
        self.assertIn("INBOX-001", task_file.read_text(encoding="utf-8"))
        self.assertTrue(result.triage_deferred)


if __name__ == "__main__":
    unittest.main()
