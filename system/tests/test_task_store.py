import tempfile
import unittest
from pathlib import Path

from system.scripts import task_store


class TestTaskStore(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        return root

    def test_rebuilds_readable_task_master_from_task_notes(self):
        root = self.make_root()
        path = root / "5. Trackers" / "tasks" / "confirm-beta-customer-list.md"
        path.write_text(
            """---
title: Confirm beta customer list
task_id: BPM-0123
status: next
owner: Product
due: 2026-07-24
---

# Confirm beta customer list

## Summary

Confirm the launch cohort.
""",
            encoding="utf-8",
        )

        output = task_store.rebuild_task_master(root)
        text = output.read_text(encoding="utf-8")

        self.assertIn("title: Task Master", text)
        self.assertIn("# Task Master", text)
        self.assertIn("[[confirm-beta-customer-list\\|Confirm beta customer list]]", text)
        self.assertNotIn("BPM-0123", text)

    def test_parses_legacy_id_heading_without_renaming_file(self):
        root = self.make_root()
        path = root / "5. Trackers" / "tasks" / "PLAN-014.md"
        path.write_text(
            "# PLAN-014 — Review recommendation work\n\n> **Status:** Active\n> **Owner:** Owner\n",
            encoding="utf-8",
        )

        task = task_store.parse_task(path)

        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, "PLAN-014")
        self.assertEqual(task.title, "Review recommendation work")
        self.assertEqual(task.path.name, "PLAN-014.md")

    def test_human_filename_collision_gets_stable_suffix(self):
        root = self.make_root()
        tasks = root / "5. Trackers" / "tasks"
        (tasks / "confirm-beta-customer-list.md").write_text("existing", encoding="utf-8")

        path = task_store.unique_task_path(root, "Confirm beta customer list")

        self.assertEqual(path.name, "confirm-beta-customer-list-2.md")

    def test_round_trips_workstream_and_inferred_fields(self):
        root = self.make_root()
        path = root / "5. Trackers" / "tasks" / "confirm-beta-customer-list.md"
        record = task_store.TaskRecord(
            task_id="BPM-0123",
            title="Confirm beta customer list",
            path=path,
            workstream="Search beta",
            source_refs=["3. Meetings/transcripts/granola/launch.md"],
            inferred_fields=["owner", "due"],
        )
        path.write_text(
            task_store.render_task(
                record,
                summary="Confirm the cohort.",
                context="Granola and Teams both mention the launch cohort.",
                next_action="Confirm owner",
                source="Triangulated evidence",
            ),
            encoding="utf-8",
        )

        parsed = task_store.parse_task(path)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.workstream, "Search beta")
        self.assertEqual(parsed.inferred_fields, ["owner", "due"])

    def test_apostrophe_title_round_trips_without_compounding_escapes(self):
        root = self.make_root()
        path = root / "5. Trackers" / "tasks" / "review-peters-weekly-report.md"
        record = task_store.TaskRecord(
            task_id="P1-008",
            title="Review Peter's Weekly Report",
            path=path,
        )
        render_kwargs = dict(
            summary="Review the report.",
            context="Weekly report review with Peter.",
            next_action="Review report",
            source="Test fixture",
        )
        path.write_text(task_store.render_task(record, **render_kwargs), encoding="utf-8")

        for _ in range(3):
            parsed = task_store.parse_task(path)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.title, "Review Peter's Weekly Report")
            path.write_text(task_store.render_task(parsed, **render_kwargs), encoding="utf-8")

        text = path.read_text(encoding="utf-8")
        self.assertIn("Review Peter''s Weekly Report", text)
        self.assertNotIn("''''", text)


if __name__ == "__main__":
    unittest.main()
