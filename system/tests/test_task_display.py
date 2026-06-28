from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import task_display


class TestTaskDisplay(unittest.TestCase):
    def test_task_file_provenance_uses_titles_and_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "PLAN-030.md"
            task_path.write_text(
                "\n".join(
                    [
                        "# PLAN-030 — Stand up the product API intake",
                        "",
                        "> **Created:** 2026-04-23",
                        "> **Last Updated:** 2026-06-26",
                        "",
                        "## Progress Log",
                        "",
                        "| Date | Source | Update | Status |",
                        "|:---|:---|:---|:---|",
                        "| 2026-04-23 | Operational strategy sync | Created after requester clarified traceability. | Active |",
                        "| 2026-06-26 | Partner Slack delta | Proceed on 9 guideline-set mappings. | Active |",
                    ]
                ),
                encoding="utf-8",
            )

            provenance = task_display.build_provenance(task_path)

            self.assertEqual(provenance.display_title, "Stand up the product API intake")
            self.assertEqual(provenance.started_at, "2026-04-23")
            self.assertEqual(task_display.format_source_pointer(provenance.initial_source), "Operational strategy sync on 2026-04-23")
            self.assertEqual(task_display.format_source_pointer(provenance.latest_source), "Partner Slack delta on 2026-06-26")
            self.assertEqual(
                task_display.format_evidence(provenance),
                "Stand up the product API intake; started from Operational strategy sync on 2026-04-23; latest progress from Partner Slack delta on 2026-06-26.",
            )

    def test_scrubber_replaces_known_and_unknown_hard_ids(self):
        text = "PLAN-030 depends on INIT-292 and DUI2-75."

        scrubbed = task_display.scrub_visible_refs(text, {"PLAN-030": "Stand up the product API intake"})

        self.assertIn("Stand up the product API intake", scrubbed)
        self.assertNotIn("PLAN-030", scrubbed)
        self.assertNotIn("INIT-292", scrubbed)
        self.assertNotIn("DUI2-75", scrubbed)
        self.assertIn("linked Jira item", scrubbed)


if __name__ == "__main__":
    unittest.main()
