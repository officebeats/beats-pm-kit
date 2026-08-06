import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from system.scripts import markdown_humanizer, task_store
from system.utils import filesystem


ROOT = Path(__file__).resolve().parents[2]


class TestMarkdownHumanizer(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "0. Incoming" / "raw").mkdir(parents=True)
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        (root / "5. Trackers" / "workstreams").mkdir(parents=True)
        (root / "5. Trackers" / "archive").mkdir(parents=True)
        (root / ".beats").mkdir(parents=True)
        task = root / "5. Trackers" / "tasks" / "TASK-012.md"
        task.write_text(
            "# TASK-012 — Partner\n\n## Context\n\nPartner integration walkthrough.\n",
            encoding="utf-8",
        )
        (root / "5. Trackers" / "workstreams" / "partner-integration.md").write_text(
            "# Partner integration\n\n[TASK-012](../tasks/TASK-012.md)\n\n"
            "[[../tasks/TASK-012|TASK-012]]\n",
            encoding="utf-8",
        )
        (root / "0. Incoming" / "raw" / "source.md").write_text(
            "# Raw source\n\n[TASK-012](../../5.%20Trackers/tasks/TASK-012.md)\n",
            encoding="utf-8",
        )
        return root

    def test_preview_does_not_mutate(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "TASK-012.md"
        before = task.read_text(encoding="utf-8")

        result = markdown_humanizer.run_humanizer(root, apply=False)

        self.assertEqual(result.scanned, 3)
        self.assertGreaterEqual(result.files_updated, 1)
        self.assertEqual(task.read_text(encoding="utf-8"), before)
        self.assertFalse((root / markdown_humanizer.LABEL_MAP).exists())

    def test_apply_humanizes_legacy_task_and_links_with_backup(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "TASK-012.md"
        workstream = root / "5. Trackers" / "workstreams" / "partner-integration.md"
        raw = root / "0. Incoming" / "raw" / "source.md"
        raw_before = raw.read_text(encoding="utf-8")

        result = markdown_humanizer.run_humanizer(root, apply=True)

        task_text = task.read_text(encoding="utf-8")
        self.assertIn("title: 'Partner integration walkthrough'", task_text)
        self.assertIn("task_id: TASK-012", task_text)
        self.assertIn("# Partner integration walkthrough", task_text)
        self.assertIn(
            "[Partner integration walkthrough](../tasks/TASK-012.md)",
            workstream.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "[[../tasks/TASK-012|Partner integration walkthrough]]",
            workstream.read_text(encoding="utf-8"),
        )
        self.assertEqual(raw.read_text(encoding="utf-8"), raw_before)
        self.assertIsNotNone(result.backup)
        self.assertTrue((root / str(result.backup) / "5. Trackers" / "tasks" / "TASK-012.md").exists())
        self.assertIn("# Human-Readable Markdown Map", (root / markdown_humanizer.LABEL_MAP).read_text(encoding="utf-8"))
        manifest = json.loads((root / markdown_humanizer.MANIFEST).read_text(encoding="utf-8"))
        self.assertTrue(all(len(item["label"].split()) <= 10 for item in manifest["notes"]))
        map_before = (root / markdown_humanizer.LABEL_MAP).read_bytes()
        manifest_before = (root / markdown_humanizer.MANIFEST).read_bytes()

        second = markdown_humanizer.run_humanizer(root, apply=True)
        self.assertEqual(second.files_updated, 0)
        self.assertIsNone(second.backup)
        self.assertEqual((root / markdown_humanizer.LABEL_MAP).read_bytes(), map_before)
        self.assertEqual((root / markdown_humanizer.MANIFEST).read_bytes(), manifest_before)

    def test_frontmatter_fields_are_not_used_as_fallback_titles(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "TASK-099.markdown"
        task.write_text(
            "---\ntitle: TASK-099\ntask_id: TASK-099\nstatus: active\n---\n\n"
            "# TASK-099\n\nPrepare the customer readiness review.\n",
            encoding="utf-8",
        )

        result = markdown_humanizer.run_humanizer(root, apply=True)

        self.assertIn("# Prepare the customer readiness review", task.read_text(encoding="utf-8"))
        self.assertIn("5. Trackers/tasks/TASK-099.markdown", result.updated_paths)

    def test_write_time_formatter_is_bounded_and_caps_task_title(self):
        root = self.make_root()
        task = root / "5. Trackers" / "tasks" / "long-title.md"
        content = (
            "---\ntitle: Review the complete partner launch readiness plan before final executive approval meeting\n"
            "task_id: BPM-0900\n---\n\n"
            "# Review the complete partner launch readiness plan before final executive approval meeting\n"
        )

        with patch.object(markdown_humanizer, "markdown_files") as full_scan:
            markdown_humanizer.write_generated_markdown(task, content)

        full_scan.assert_not_called()
        rendered = task.read_text(encoding="utf-8")
        self.assertIn("task_id: BPM-0900", rendered)
        self.assertEqual(
            markdown_humanizer.document_title(rendered),
            "Review the complete partner launch readiness plan before final executive",
        )
        self.assertLessEqual(len(markdown_humanizer.document_title(rendered).split()), 10)

    def test_task_store_output_stays_human_readable(self):
        root = self.make_root()
        path = task_store.unique_task_path(root, "Confirm beta customer list")
        record = task_store.TaskRecord(
            task_id="BPM-0123",
            title="Confirm beta customer list",
            path=path,
        )

        task_store._write(
            path,
            task_store.render_task(
                record,
                summary="Confirm the cohort.",
                context="Launch planning.",
                next_action="Confirm owner",
                source="Local evidence",
            ),
        )

        self.assertEqual(path.name, "confirm-beta-customer-list.md")
        self.assertIn("# Confirm beta customer list", path.read_text(encoding="utf-8"))

    def test_catalog_skips_dependencies(self):
        root = self.make_root()
        dependency = root / "3. Meetings" / "work" / "node_modules" / "pkg" / "README.md"
        dependency.parent.mkdir(parents=True)
        dependency.write_text("# Dependency\n", encoding="utf-8")

        paths = {path.relative_to(root).as_posix() for path in markdown_humanizer.markdown_files(root)}

        self.assertNotIn(dependency.relative_to(root).as_posix(), paths)

    def test_generic_writer_preserves_non_workspace_markdown_exactly(self):
        root = self.make_root()
        path = root / "system" / "docs" / "contract.md"
        content = "# Exact contract\n\nNo trailing newline"

        self.assertTrue(filesystem.write_file(path, content))

        self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_primary_generators_use_shared_formatter(self):
        paths = (
            "system/scripts/task_store.py",
            "system/scripts/task_intake_fast.py",
            "system/scripts/task_master_triage.py",
            "system/scripts/trello_bridge.py",
            "system/scripts/atlassian_context_state.py",
            "system/utils/filesystem.py",
        )
        for relative in paths:
            source = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("markdown_humanizer", source, relative)


if __name__ == "__main__":
    unittest.main()
