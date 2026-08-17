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
                    "| [PLAN-014](tasks/PLAN-014.md) | **Review guideline recommendation work** — GLR ramp | Owner | 2026-05-13 | 🔴 Active — GLR production target needs context |",
                ]
            ),
            encoding="utf-8",
        )
        (tasks_dir / "PLAN-014.md").write_text(
            "\n".join(
                [
                    "# PLAN-014 — Review guideline recommendation work",
                    "",
                    "> **Status:** 🔴 Active — GLR production target needs context",
                    "> **Owner:** Owner",
                    "> **Last Updated:** 2026-06-17",
                    "",
                    "## Context & Background",
                    "",
                    "Guideline Recommender, GLR, reasoning service, IAD, Indicia, stakeholder-specific configuration, and June 30 production target.",
                    "",
                    "## 👥 Stakeholders",
                    "",
                    "| Role | Person | Context |",
                    "|:-----|:-------|:--------|",
                    "| Consult | Stakeholder One | IAD / Indicia context |",
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
                    "| 2026-06-17 | Calendar | Stakeholder follow-up is next checkpoint. | 🔴 |",
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
                "Stakeholder One",
                "Task Owner 2:00 PM",
                "IAD Indicia guideline tenant configuration needs task owner follow-up with the stakeholder.",
                "Stakeholder One 3:30 PM",
                "I think this was all referring to the set up we are doing to provide LLM reasoning to IAD.",
                "https://example.slack.com/archives/D0000000000/p1782160177453819",
            ]
        )
        result = task_intake_fast.run_intake(
            root=root,
            raw_text=raw,
            source="Slack DM with stakeholder",
            captured_at=dt.datetime(2026, 6, 22, 15, 35, tzinfo=dt.timezone.utc),
        )

        self.assertEqual(result.mode, "updated_existing")
        self.assertEqual(result.task_id, "PLAN-014")
        self.assertEqual(result.display_label, "IAD Indicia guideline tenant configuration")
        source_note = root / result.source_note_path
        task_file = root / result.task_path
        task_master = (root / "5. Trackers" / "TASK_MASTER.md").read_text(encoding="utf-8")
        self.assertTrue(source_note.exists())
        note_text = source_note.read_text(encoding="utf-8")
        self.assertIn("## Raw Evidence", note_text)
        self.assertIn("# IAD Indicia guideline tenant configuration", note_text)
        self.assertIn("Task Owner 2:00 PM", note_text)
        self.assertIn("https://example.slack.com/archives/D0000000000/p1782160177453819", note_text)
        self.assertIn("## Summary", note_text)
        updated_task = task_file.read_text(encoding="utf-8")
        self.assertIn("Source Note", updated_task)
        self.assertIn("IAD Indicia guideline tenant configuration", updated_task)
        self.assertIn("title: 'Review guideline recommendation work'", updated_task)
        self.assertIn("[[PLAN-014\\|Review guideline recommendation work]]", task_master)
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
        self.assertNotIn("INBOX-001", task_file.name)
        self.assertIn("[[random-stakeholder-note-ask-finance\\|Random stakeholder note ask Finance]]", (root / "5. Trackers" / "TASK_MASTER.md").read_text(encoding="utf-8"))
        self.assertIn("# Random stakeholder note ask", task_file.read_text(encoding="utf-8"))
        self.assertIn("task_id: INBOX-001", task_file.read_text(encoding="utf-8"))
        self.assertIn("workstream: Unassigned", task_file.read_text(encoding="utf-8"))
        self.assertIn("  - workstream", task_file.read_text(encoding="utf-8"))
        self.assertTrue(result.triage_deferred)

    def test_repeated_updates_append_frontmatter_sources_without_corrupting_yaml(self):
        root = self.make_repo()
        first = task_intake_fast.run_intake(
            root=root,
            raw_text="IAD Indicia guideline setup needs owner follow-up.",
            source="Teams",
            explicit_task_id="PLAN-014",
            captured_at=dt.datetime(2026, 6, 22, 16, 0, tzinfo=dt.timezone.utc),
        )
        second = task_intake_fast.run_intake(
            root=root,
            raw_text="The same IAD Indicia task was confirmed in Outlook.",
            source="Outlook",
            explicit_task_id="PLAN-014",
            captured_at=dt.datetime(2026, 6, 23, 9, 0, tzinfo=dt.timezone.utc),
        )

        text = (root / second.task_path).read_text(encoding="utf-8")
        frontmatter = text.split("\n---\n", 1)[0]

        self.assertEqual(first.task_path, second.task_path)
        self.assertIn("updated: 2026-06-23", frontmatter)
        self.assertEqual(frontmatter.count("0. Incoming/raw/"), 2)
        self.assertNotIn("> **Last Updated:**", text)

    def test_write_task_index_writes_only_canonical_cache(self):
        root = self.make_repo()
        index = task_intake_fast.build_task_index(root)

        written = task_intake_fast.write_task_index(root, index)

        self.assertEqual(written, root / task_intake_fast.CACHE_REL)
        self.assertTrue(written.exists())
        self.assertFalse((root / "system" / "cache" / "task_index.json").exists())
        self.assertEqual(task_intake_fast.load_or_build_index(root)["tasks"], index["tasks"])


if __name__ == "__main__":
    unittest.main()
