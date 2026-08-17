"""Tests for the per-workflow lessons FIFO ledger."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from system.scripts import workflow_lessons


class TestWorkflowLessons(unittest.TestCase):
    def test_append_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = workflow_lessons.append_lesson(
                root, "beats-slack", "Pre-chunk long windows.", date="2026-08-17"
            )
            self.assertEqual(
                path, root / ".beats" / "lessons" / "beats-slack.md"
            )
            self.assertEqual(
                workflow_lessons.load_lessons(root, "beats-slack"),
                [{"date": "2026-08-17", "text": "Pre-chunk long windows."}],
            )
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "- 2026-08-17: Pre-chunk long windows.\n",
            )

    def test_cap_drops_oldest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(12):
                workflow_lessons.append_lesson(
                    root, "day", f"lesson {n}", date=f"2026-08-{n + 1:02d}"
                )
            lessons = workflow_lessons.load_lessons(root, "day")
            self.assertEqual(len(lessons), workflow_lessons.MAX_LESSONS)
            self.assertEqual(lessons[0]["text"], "lesson 2")
            self.assertEqual(lessons[-1]["text"], "lesson 11")

    def test_missing_file_loads_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(workflow_lessons.load_lessons(Path(tmp), "never-ran"), [])

    def test_workflow_name_is_slugged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = workflow_lessons.append_lesson(root, "Beats Comms!", "note", date="2026-08-17")
            self.assertEqual(path.name, "beats-comms.md")
            self.assertEqual(len(workflow_lessons.load_lessons(root, "beats comms")), 1)

    def test_traversal_and_empty_names_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                workflow_lessons.append_lesson(root, "..", "note")
            with self.assertRaises(ValueError):
                workflow_lessons.append_lesson(root, "!!!", "note")
            with self.assertRaises(ValueError):
                workflow_lessons.append_lesson(root, "day", "   ")

    def test_multiline_text_is_flattened_to_one_bullet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow_lessons.append_lesson(root, "meet", "line one\nline two", date="2026-08-17")
            lessons = workflow_lessons.load_lessons(root, "meet")
            self.assertEqual(lessons, [{"date": "2026-08-17", "text": "line one line two"}])

    def test_module_cli_append_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(__file__).resolve().parents[2]
            append = subprocess.run(
                [
                    sys.executable, "-m", "system.scripts.workflow_lessons",
                    "--root", tmp, "append", "week", "--text", "cli lesson",
                ],
                cwd=repo, capture_output=True, text=True,
            )
            self.assertEqual(append.returncode, 0, append.stderr)
            self.assertTrue(append.stdout.strip().endswith("week.md"))
            listed = subprocess.run(
                [
                    sys.executable, "-m", "system.scripts.workflow_lessons",
                    "--root", tmp, "list", "week",
                ],
                cwd=repo, capture_output=True, text=True,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn(": cli lesson", listed.stdout)


if __name__ == "__main__":
    unittest.main()
