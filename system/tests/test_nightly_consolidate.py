import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from system.scripts import nightly_consolidate, task_store

ROOT = Path(__file__).resolve().parents[2]


class TestNightlyConsolidate(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "0. Incoming" / "raw").mkdir(parents=True)
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        (root / "5. Trackers" / "workstreams").mkdir(parents=True)
        (root / "5. Trackers" / "archive").mkdir(parents=True)
        (root / ".beats").mkdir(parents=True)
        (root / "5. Trackers" / "tasks" / "PLAN-201.md").write_text(
            "---\n"
            "task_id: PLAN-201\n"
            "title: 'Draft pricing brief'\n"
            "status: in-progress\n"
            "lane: Today\n"
            "owner: Ernesto\n"
            "workstream: Pricing\n"
            "---\n\n# Draft pricing brief\n",
            encoding="utf-8",
        )
        (root / "5. Trackers" / "tasks" / "PLAN-202.md").write_text(
            "---\n"
            "task_id: PLAN-202\n"
            "title: 'Old finished chore'\n"
            "status: done\n"
            "lane: Today\n"
            "owner: Ernesto\n"
            "workstream: Pricing\n"
            "---\n\n# Old finished chore\n",
            encoding="utf-8",
        )
        (root / "5. Trackers" / "archive" / "PLAN-190.md").write_text(
            "---\n"
            "task_id: PLAN-190\n"
            "title: 'Misfiled archived task'\n"
            "status: in-progress\n"
            "lane: Today\n"
            "owner: Ernesto\n"
            "workstream: Pricing\n"
            "---\n\n# Misfiled archived task\n",
            encoding="utf-8",
        )
        return root

    def test_run_ok_writes_skeleton_and_last_run(self):
        root = self.make_root()

        summary = nightly_consolidate.run_nightly(root)

        self.assertTrue(summary["ok"])
        self.assertEqual(
            [step["step"] for step in summary["steps"]],
            ["context-index", "task-master", "humanizer", "archive-check", "day-skeleton"],
        )
        for step in summary["steps"]:
            self.assertTrue(step["ok"], step)
            self.assertIsInstance(step["wall_ms"], int)
            self.assertGreaterEqual(step["wall_ms"], 0)
            self.assertIsInstance(step["detail"], str)

        self.assertTrue((root / ".beats" / "day_skeleton.md").exists())
        last_run = root / ".beats" / "nightly-last-run.json"
        self.assertTrue(last_run.exists())
        persisted = json.loads(last_run.read_text(encoding="utf-8"))
        self.assertTrue(persisted["ok"])
        self.assertEqual(persisted["steps"], summary["steps"])

    def test_skip_skeleton(self):
        root = self.make_root()

        summary = nightly_consolidate.run_nightly(root, skip_skeleton=True)

        self.assertTrue(summary["ok"])
        self.assertFalse((root / ".beats" / "day_skeleton.md").exists())
        skeleton_step = summary["steps"][-1]
        self.assertEqual(skeleton_step["step"], "day-skeleton")
        self.assertIn("skipped", skeleton_step["detail"])

    def test_failing_step_degrades_without_aborting_later_steps(self):
        root = self.make_root()

        with patch.object(task_store, "rebuild_task_master", side_effect=RuntimeError("boom")):
            summary = nightly_consolidate.run_nightly(root)

        self.assertFalse(summary["ok"])
        by_name = {step["step"]: step for step in summary["steps"]}
        self.assertFalse(by_name["task-master"]["ok"])
        self.assertIn("RuntimeError: boom", by_name["task-master"]["detail"])
        # Later steps still ran.
        self.assertTrue(by_name["archive-check"]["ok"])
        self.assertTrue(by_name["day-skeleton"]["ok"])
        self.assertTrue((root / ".beats" / "day_skeleton.md").exists())
        # Persisted record carries the failure.
        persisted = json.loads((root / ".beats" / "nightly-last-run.json").read_text(encoding="utf-8"))
        self.assertFalse(persisted["ok"])

    def test_main_exit_codes_follow_summary(self):
        with patch.object(nightly_consolidate, "run_nightly", return_value={"ok": True, "ts": "", "steps": []}):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(nightly_consolidate.main(["--json"]), 0)
        with patch.object(nightly_consolidate, "run_nightly", return_value={"ok": False, "ts": "", "steps": []}):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(nightly_consolidate.main(["--json"]), 1)

    def test_archive_hygiene_counts(self):
        root = self.make_root()

        counts = nightly_consolidate.archive_hygiene_counts(root)

        self.assertEqual(counts["active_done"], 1)
        self.assertEqual(counts["archived_open"], 1)

    def test_install_launchd_renders_template_without_loading(self):
        target = Path(tempfile.mkdtemp())
        buffer = io.StringIO()

        with contextlib.redirect_stdout(buffer):
            destination = nightly_consolidate.install_launchd(ROOT, launch_agents_dir=target)

        self.assertEqual(destination.name, "com.beats.nightly-consolidate.plist")
        rendered = destination.read_text(encoding="utf-8")
        self.assertNotIn("__REPO_ROOT__", rendered)
        self.assertIn("system.scripts.nightly_consolidate", rendered)
        self.assertIn(str(ROOT), rendered)
        output = buffer.getvalue()
        self.assertIn("launchctl load", output)


if __name__ == "__main__":
    unittest.main()
