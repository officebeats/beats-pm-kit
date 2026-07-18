import tempfile
import unittest
import json
from pathlib import Path

from system.scripts import upgrade_compat


class TestUpgradeCompatibility(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        return root

    def test_safe_migration_adds_titles_without_renaming_or_breaking_links(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "PLAN-014.md"
        original = "# PLAN-014 — Review recommendation work\n\n> **Status:** Active\n"
        task.write_text(original, encoding="utf-8")
        task_master = root / "5. Trackers" / "TASK_MASTER.md"
        task_master.write_text(
            "# Task Master\n\n| ID | Task | Owner | Due | Status |\n|:---|:---|:---|:---|:---|\n"
            "| [PLAN-014](tasks/PLAN-014.md) | Review recommendation work | Owner | TBD | Active |\n",
            encoding="utf-8",
        )

        report = upgrade_compat.inspect(root)
        self.assertFalse(report.blockers)
        self.assertEqual({item.path for item in report.changes}, {"5. Trackers/TASK_MASTER.md", "5. Trackers/tasks/PLAN-014.md"})

        result = upgrade_compat.apply_safe_changes(root, report)

        self.assertTrue(task.exists())
        self.assertIn("title: 'Review recommendation work'", task.read_text(encoding="utf-8"))
        self.assertIn("# Review recommendation work", task.read_text(encoding="utf-8"))
        self.assertIn("tasks/PLAN-014.md", task_master.read_text(encoding="utf-8"))
        self.assertTrue((root / result["backup"] / "manifest.json").exists())

        rolled_back = upgrade_compat.rollback(root, Path(result["backup"]))
        self.assertEqual(rolled_back["restored"], 2)
        self.assertEqual(task.read_text(encoding="utf-8"), original)

    def test_ambiguous_id_only_title_blocks_apply(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "PLAN-014.md"
        task.write_text("# PLAN-014\n", encoding="utf-8")

        report = upgrade_compat.inspect(root)

        self.assertEqual(len(report.blockers), 1)
        self.assertEqual(report.blockers[0].code, "ambiguous-title")
        with self.assertRaises(ValueError):
            upgrade_compat.apply_safe_changes(root, report)

    def test_id_only_task_uses_existing_task_master_label_without_renaming(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "PLAN-014.md"
        task.write_text("# PLAN-014\n", encoding="utf-8")
        task_master = root / "5. Trackers" / "TASK_MASTER.md"
        task_master.write_text(
            "# Task Master\n\n| ID | Task | Owner | Due | Status |\n|:---|:---|:---|:---|:---|\n"
            "| [PLAN-014](tasks/PLAN-014.md) | **Review recommendation work** — Follow up | Owner | TBD | Active |\n",
            encoding="utf-8",
        )

        report = upgrade_compat.inspect(root)

        self.assertFalse(report.blockers)
        task_change = next(change for change in report.changes if change.path.endswith("PLAN-014.md"))
        self.assertEqual(task_change.title, "Review recommendation work")
        upgrade_compat.apply_safe_changes(root, report)
        self.assertTrue(task.exists())
        self.assertIn("# Review recommendation work", task.read_text(encoding="utf-8"))

    def test_local_meeting_exports_satisfy_upgrade_source_check(self):
        root = self.make_root()
        for source in ("quill", "granola"):
            export = root / "3. Meetings" / "transcripts" / source
            export.mkdir(parents=True)
            (export / "meeting.md").write_text("# Meeting\n", encoding="utf-8")

        self.assertEqual(upgrade_compat.source_status(root, "quill"), "available")
        self.assertEqual(upgrade_compat.source_status(root, "granola"), "available")

    def test_crlf_frontmatter_is_migrated_without_duplication(self):
        root = self.make_root()
        note = root / "5. Trackers" / "tasks" / "launch-brief.md"
        note.write_bytes(b"---\r\ntask_id: BPM-001\r\n---\r\n\r\n# Launch brief\r\n")

        report = upgrade_compat.inspect(root)
        upgrade_compat.apply_safe_changes(root, report)
        migrated = note.read_text(encoding="utf-8")

        self.assertEqual(migrated.count("task_id: BPM-001"), 1)
        self.assertEqual(migrated.count("title: 'Launch brief'"), 1)
        self.assertEqual(migrated.count("# Launch brief"), 1)

    def test_legacy_model_pin_migrates_locally_and_rollback_removes_new_policy(self):
        root = self.make_root()
        config = root / "system" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(
            json.dumps({"ai": {"default_model": "gemini-preview-candidate"}}),
            encoding="utf-8",
        )

        report = upgrade_compat.inspect(root)

        self.assertEqual(len(report.model_pins), 1)
        self.assertEqual(report.model_pins[0].runtime, "gemini")
        self.assertTrue(any(item.code == "legacy-model-pin" for item in report.warnings))
        self.assertTrue(any(item.code == "preview-model-pin" for item in report.warnings))

        result = upgrade_compat.apply_safe_changes(root, report)
        policy_path = root / ".beats" / "model-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["overrides"]["gemini"]["balanced"], "gemini-preview-candidate"
        )

        upgraded = upgrade_compat.inspect(root)
        self.assertEqual(upgraded.model_pins, [])

        rolled_back = upgrade_compat.rollback(root, Path(result["backup"]))
        self.assertFalse(policy_path.exists())
        self.assertGreaterEqual(rolled_back["restored"], 1)

    def test_existing_local_promotion_wins_over_legacy_pin(self):
        root = self.make_root()
        config = root / "system" / "config.json"
        config.parent.mkdir(parents=True)
        config.write_text(
            json.dumps({"ai": {"default_model": "gpt-legacy-candidate"}}),
            encoding="utf-8",
        )
        policy_path = root / ".beats" / "model-policy.json"
        policy_path.parent.mkdir(parents=True)
        policy_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "overrides": {"codex": {"balanced": "evaluated-candidate"}},
                }
            ),
            encoding="utf-8",
        )

        report = upgrade_compat.inspect(root)
        upgrade_compat.apply_safe_changes(root, report)

        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["overrides"]["codex"]["balanced"], "evaluated-candidate"
        )
        self.assertTrue(
            any(item["status"] == "preserved-newer-choice" for item in policy["legacy_migrations"])
        )

    def test_conflicting_legacy_model_pins_block_upgrade(self):
        root = self.make_root()
        system_config = root / "system" / "config.json"
        system_config.parent.mkdir(parents=True)
        system_config.write_text(
            json.dumps({"ai": {"default_model": "gemini-candidate-one"}}),
            encoding="utf-8",
        )
        profile = root / "config" / "profile.yml"
        profile.parent.mkdir(parents=True)
        profile.write_text("model: gemini-candidate-two\n", encoding="utf-8")

        report = upgrade_compat.inspect(root)

        self.assertTrue(any(item.code == "conflicting-model-pins" for item in report.blockers))
        with self.assertRaises(ValueError):
            upgrade_compat.apply_safe_changes(root, report)


if __name__ == "__main__":
    unittest.main()
