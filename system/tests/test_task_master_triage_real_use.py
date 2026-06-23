import tempfile
import unittest
from pathlib import Path


from system.scripts import task_master_triage


class TestTaskMasterTriageRealUse(unittest.TestCase):
    def test_realistic_overdue_task_updates_managed_blocks_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tasks_dir = root / "5. Trackers" / "tasks"
            reports_dir = root / "3. Meetings" / "reports" / "day"
            tasks_dir.mkdir(parents=True)
            reports_dir.mkdir(parents=True)
            task_master = root / "5. Trackers" / "TASK_MASTER.md"
            task_master.write_text(
                "\n".join(
                    [
                        "# TASK MASTER",
                        "",
                        "| ID | Task | Owner | Due | Status |",
                        "|:---|:-----|:------|:----|:-------|",
                        "| PARU-001 | Partner launch scope | PM | 2024-01-15 | Active |",
                        "",
                        "## Manual Notes",
                        "",
                        "Do not overwrite this section.",
                    ]
                ),
                encoding="utf-8",
            )
            task_file = tasks_dir / "PARU-001.md"
            task_file.write_text(
                "\n".join(
                    [
                        "# PARU-001: Partner Launch Scope",
                        "",
                        "> **Status:** Active",
                        "> **Due:** 2024-01-15",
                        "> **Last Updated:** 2024-01-10",
                        "",
                        "## Context & Background",
                        "",
                        "Define the first release slice from partner evidence.",
                        "",
                        "## Progress Log",
                        "",
                        "| Date | Source | Update | Status |",
                        "|:---|:---|:---|:---|",
                        "| 2024-01-10 | Planning Artifact | Drafted initial scope boundary. | Active |",
                    ]
                ),
                encoding="utf-8",
            )

            original = (
                task_master_triage.BASE_DIR,
                task_master_triage.TASK_MASTER_PATH,
                task_master_triage.TASKS_DIR,
                task_master_triage.REPORTS_DIR,
            )
            try:
                task_master_triage.BASE_DIR = root
                task_master_triage.TASK_MASTER_PATH = task_master
                task_master_triage.TASKS_DIR = tasks_dir
                task_master_triage.REPORTS_DIR = reports_dir
                items, by_task = task_master_triage.collect_triage()
                report_path = reports_dir / "fixture-task-triage.md"
                task_master_triage.write_text(report_path, task_master_triage.build_report(items))
                task_master_triage.apply_updates(items, by_task, report_path)
            finally:
                (
                    task_master_triage.BASE_DIR,
                    task_master_triage.TASK_MASTER_PATH,
                    task_master_triage.TASKS_DIR,
                    task_master_triage.REPORTS_DIR,
                ) = original

            updated_master = task_master.read_text(encoding="utf-8")
            updated_task = task_file.read_text(encoding="utf-8")

            self.assertIn("TASK_TRIAGE_SUMMARY:BEGIN", updated_master)
            self.assertIn("Manual Notes", updated_master)
            self.assertIn("Do not overwrite this section.", updated_master)
            self.assertIn("Overdue", updated_task)
            self.assertIn("Confirmation needed", updated_task)
            self.assertTrue(report_path.exists())


if __name__ == "__main__":
    unittest.main()
