from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from system.scripts import vault_query

# All fixture content is synthetic: fake people, fake workstreams, fake files.

TASK_ONE = """---
title: 'Draft widget onboarding checklist'
task_id: WID-001
---

# WID-001 — Draft widget onboarding checklist

> **Status:** 🟡 In Progress
> **Lane:** Today
> **Owner:** Alex Example
> **Due:** 2026-01-15
> **Eisenhower:** 🔴 Do First
> **Labels:** P0 / Urgent

Body mentions the gizmo rollout plan.
"""

TASK_TWO = """---
title: 'Archive sprocket survey results'
task_id: SPR-002
---

# SPR-002 — Archive sprocket survey results

> **Status:** ✅ Done
> **Lane:** Later
> **Owner:** Sam Sample
> **Due:** 2026-02-01
> **Eisenhower:** ⬜ Monitor
> **Workstream:** Sprocket research
"""

QUOTE_INDEX = """# Quote Index

| Date | Speaker | Quote | Source |
|:---|:---|:---|:---|
| 2026-01-10 | Alex Example | We should ship the widget onboarding flow first. | `archive/2026-01-10_widget-sync.txt` |
| 2026-02-05 | 2026-02-05_Sprocket Survey Review.txt | `archive/2026-02-05_sprocket-survey-review.txt` |
| 2026-02-20 | Sam Sample | The survey results favor the gizmo variant. | `archive/2026-02-20_survey-readout.txt` |
"""

LABELS = {
    "schema_version": 1,
    "notes": [
        {"agent_ref": "", "label": "Widget Weekly Sync — Notes", "needs_review": False, "path": "notes/widget-weekly.md", "preserved": True},
        {"agent_ref": "WID-001", "label": "Widget Onboarding Checklist", "needs_review": False, "path": "notes/widget-onboarding.md", "preserved": False},
        {"agent_ref": "", "label": "Sprocket Survey Raw Export", "needs_review": True, "path": "notes/sprocket-survey.md", "preserved": True},
    ],
}


def make_vault(root: Path) -> None:
    tasks = root / "5. Trackers" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "WID-001.md").write_text(TASK_ONE, encoding="utf-8")
    (tasks / "archive").mkdir()
    (tasks / "archive" / "SPR-002.md").write_text(TASK_TWO, encoding="utf-8")
    (tasks / "_TEMPLATE.md").write_text("# {{TASK_ID}}\n\n> **Status:** template\n", encoding="utf-8")
    (tasks / "scratch-draft.md").write_text("just a draft note, no headers\n", encoding="utf-8")
    meetings = root / "3. Meetings"
    meetings.mkdir()
    (meetings / "quote-index.md").write_text(QUOTE_INDEX, encoding="utf-8")
    beats = root / ".beats"
    beats.mkdir()
    (beats / "markdown-labels.json").write_text(json.dumps(LABELS), encoding="utf-8")


def run_cli(root: Path, *argv: str) -> tuple[int, list[str]]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = vault_query.main(["--root", str(root), *argv])
    lines = out.getvalue().splitlines()
    return code, lines


class TestVaultQuery(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        make_vault(self.root)

    # --- tasks ---

    def test_tasks_lists_all_with_summary_header(self):
        code, lines = run_cli(self.root, "tasks")
        self.assertEqual(code, 0)
        self.assertEqual(lines[0], "# tasks: showing 2 of 2 matches (2 scanned)")
        self.assertEqual(len(lines), 3)  # template and draft are skipped
        self.assertIn("WID-001", lines[1])
        self.assertIn("5. Trackers/tasks/WID-001.md", lines[1])  # source path shown
        self.assertIn("SPR-002", lines[2])

    def test_tasks_filters(self):
        code, lines = run_cli(self.root, "tasks", "--status", "in progress")
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 2)
        self.assertIn("WID-001", lines[1])

        _, lines = run_cli(self.root, "tasks", "--lane", "later")
        self.assertIn("SPR-002", lines[1])

        _, lines = run_cli(self.root, "tasks", "--priority", "P0")
        self.assertEqual(len(lines), 2)
        self.assertIn("WID-001", lines[1])

        _, lines = run_cli(self.root, "tasks", "--workstream", "sprocket")
        self.assertEqual(len(lines), 2)
        self.assertIn("SPR-002", lines[1])

        _, lines = run_cli(self.root, "tasks", "--text", "gizmo rollout")
        self.assertEqual(len(lines), 2)
        self.assertIn("WID-001", lines[1])

        _, lines = run_cli(self.root, "tasks", "--text", "no such thing")
        self.assertEqual(lines, ["# tasks: showing 0 of 0 matches (2 scanned)"])

    def test_tasks_limit_bounds_output_and_flags_hidden_matches(self):
        code, lines = run_cli(self.root, "tasks", "--limit", "1")
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 2)
        self.assertIn("showing 1 of 2 matches", lines[0])
        self.assertIn("narrow filters or raise --limit", lines[0])

    # --- labels ---

    def test_labels_glob_substring_and_needs_review(self):
        code, lines = run_cli(self.root, "labels", "--name", "*Weekly*")
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 2)
        self.assertIn("Widget Weekly Sync", lines[1])

        _, lines = run_cli(self.root, "labels", "--name", "onboarding")
        self.assertEqual(len(lines), 2)
        self.assertIn("ref=WID-001", lines[1])

        _, lines = run_cli(self.root, "labels", "--needs-review")
        self.assertEqual(len(lines), 2)
        self.assertIn("Sprocket Survey Raw Export", lines[1])
        self.assertIn("needs_review", lines[1])

        _, lines = run_cli(self.root, "labels", "--path", "notes/*.md", "--limit", "2")
        self.assertEqual(lines[0], "# labels: showing 2 of 3 matches (3 scanned) — narrow filters or raise --limit")

    # --- quotes ---

    def test_quotes_person_topic_and_date_filters(self):
        code, lines = run_cli(self.root, "quotes")
        self.assertEqual(code, 0)
        self.assertEqual(lines[0], "# quotes: showing 3 of 3 matches (3 scanned)")

        _, lines = run_cli(self.root, "quotes", "--person", "alex")
        self.assertEqual(len(lines), 2)
        self.assertIn("Alex Example", lines[1])

        _, lines = run_cli(self.root, "quotes", "--topic", "survey")
        self.assertEqual(len(lines), 3)  # 3-cell legacy row + Sam's quote

        _, lines = run_cli(self.root, "quotes", "--date", "2026-02")
        self.assertEqual(len(lines), 3)

    def test_quotes_parses_legacy_three_cell_rows(self):
        _, lines = run_cli(self.root, "quotes", "--topic", "Sprocket Survey Review")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].startswith("2026-02-05 | - |"))

    # --- error handling ---

    def test_missing_files_exit_1_with_stderr_message(self):
        empty = self.root / "empty"
        empty.mkdir()
        for command, needle in (("tasks", "tasks directory"), ("labels", "labels sidecar"), ("quotes", "quote index")):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code, lines = run_cli(empty, command)
            self.assertEqual(code, 1, command)
            self.assertEqual(lines, [], command)
            self.assertIn(needle, err.getvalue())

    def test_corrupt_labels_sidecar_exits_1(self):
        (self.root / ".beats" / "markdown-labels.json").write_text("{not json", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code, _ = run_cli(self.root, "labels")
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", err.getvalue())


if __name__ == "__main__":
    unittest.main()
