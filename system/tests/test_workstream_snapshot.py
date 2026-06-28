"""Workstream snapshot regression coverage."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import workstream_snapshot  # noqa: E402


class TestWorkstreamSnapshot(unittest.TestCase):
    def test_real_workstream_rows_render_first(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tracker = root / "5. Trackers"
            tracker.mkdir(parents=True)
            (tracker / "WORKSTREAMS.md").write_text(
                "| Workstream | Latest Outcome | Completed Outcome | Open Items | Recommended Next 3 | Status |\n"
                "|:-----------|:---------------|:------------------|:-----------|:-------------------|:-------|\n"
                "| the product API partner routing | 2026-06-28: decision rule drafted | None newly confirmed | 1 Slack ask | Confirm owner; draft outcome; update tracker | Active |\n",
                encoding="utf-8",
            )

            items, note = workstream_snapshot.build_snapshot(root, "day", 5)
            rendered = workstream_snapshot.render_markdown(items, source_note=note)

            self.assertIn("### the product API partner routing", rendered)
            self.assertIn("- Latest outcome: 2026-06-28: decision rule drafted", rendered)
            self.assertIn("  - Confirm owner", rendered)

    def test_task_master_fallback_strips_internal_ids_from_titles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tracker = root / "5. Trackers"
            critical = tracker / "critical"
            tracker.mkdir(parents=True)
            critical.mkdir(parents=True)
            (tracker / "WORKSTREAMS.md").write_text(
                "| Workstream | Latest Outcome | Completed Outcome | Open Items | Recommended Next 3 | Status |\n"
                "|:-----------|:---------------|:------------------|:-----------|:-------------------|:-------|\n"
                "| [Example Workstream](workstreams/_TEMPLATE.md) | [Date]: [outcome] | [Date]: [completed item] | [count/source] | [top action] | Active |\n",
                encoding="utf-8",
            )
            (tracker / "TASK_MASTER.md").write_text(
                "| ID | Task | Owner | Due | Status |\n"
                "|:---|:-----|:------|:----|:-------|\n"
                "| [PLAN-048](tasks/PLAN-048.md) | **Define exception intake checklist** — Build checklist | Owner | 2026-06-29 | Partner wants checklist |\n",
                encoding="utf-8",
            )
            (critical / "boss-requests.md").write_text(
                "| ID | Date | Task | Source |\n"
                "|:---|:-----|:-----|:-------|\n"
                "| BOSS-001 | 2026-05-07 | Define user stories for the product API sandbox tracking \"Re: old subject\" | boss |\n",
                encoding="utf-8",
            )

            items, note = workstream_snapshot.build_snapshot(root, "day", 5)
            rendered = workstream_snapshot.render_markdown(items, source_note=note)

            self.assertIn("falls back to ranked local task commitments", note)
            self.assertIn("### Define exception intake checklist", rendered)
            self.assertIn("### Define user stories for the product API sandbox tracking", rendered)
            self.assertNotIn("### PLAN-048", rendered)
            self.assertNotIn("### BOSS-001", rendered)
            self.assertNotIn("Re: old subject", rendered)
            self.assertNotIn("Evidence: PLAN-048", rendered)
            self.assertIn("Agent refs:", rendered)


if __name__ == "__main__":
    unittest.main()
