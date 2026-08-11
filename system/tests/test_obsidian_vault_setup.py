from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import obsidian_vault_setup


class TestObsidianVaultSetup(unittest.TestCase):
    def test_dry_run_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            changes = obsidian_vault_setup.configure_vault(root, dry_run=True)

            self.assertIn(".obsidian/graph.json", changes)
            self.assertFalse((root / ".obsidian").exists())
            self.assertFalse((root / "6. Resources" / "obsidian" / "Obsidian Graph Index.md").exists())

    def test_apply_creates_local_vault_settings_and_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            changes = obsidian_vault_setup.configure_vault(root, dry_run=False)

            self.assertIn(".obsidian/core-plugins.json", changes)
            self.assertIn(".obsidian/app.json", changes)
            self.assertIn(".obsidian/graph.json", changes)
            self.assertIn("6. Resources/obsidian/Obsidian Graph Index.md", changes)

            graph = json.loads((root / ".obsidian" / "graph.json").read_text(encoding="utf-8"))
            self.assertTrue(graph["showTags"])
            self.assertTrue(graph["showAttachments"])
            self.assertTrue(graph["showArrow"])
            self.assertIn(
                {"query": 'path:"5. Trackers"', "color": {"a": 1, "rgb": 0xD64545}},
                graph["colorGroups"],
            )

            index = (root / "6. Resources" / "obsidian" / "Obsidian Graph Index.md").read_text(encoding="utf-8")
            self.assertIn("[[5. Trackers/TASK_MASTER|Task Master]]", index)
            self.assertIn("[[5. Trackers/graph-hubs/Human-readable Hubs|Human-readable Hubs]]", index)
            self.assertNotIn("Ernest0/Work", index)

    def test_existing_app_config_is_preserved_and_ignore_filters_are_deduped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            obsidian_dir = root / ".obsidian"
            obsidian_dir.mkdir()
            (obsidian_dir / "app.json").write_text(
                json.dumps(
                    {
                        "alwaysUpdateLinks": False,
                        "spellcheck": True,
                        "userIgnoreFilters": [".git/"],
                    }
                ),
                encoding="utf-8",
            )

            obsidian_vault_setup.configure_vault(root, dry_run=False)

            app_config = json.loads((obsidian_dir / "app.json").read_text(encoding="utf-8"))
            self.assertTrue(app_config["alwaysUpdateLinks"])
            self.assertTrue(app_config["spellcheck"])
            self.assertEqual(app_config["userIgnoreFilters"].count(".git/"), 1)
            self.assertIn("outputs/", app_config["userIgnoreFilters"])
            self.assertIn("5. Trackers/MARKDOWN_LABELS.md", app_config["userIgnoreFilters"])
            self.assertIn("Trackers/MARKDOWN_LABELS.md", app_config["userIgnoreFilters"])

    def test_existing_graph_groups_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            obsidian_dir = root / ".obsidian"
            obsidian_dir.mkdir()
            custom_group = {"query": "tag:#custom", "color": {"a": 1, "rgb": 123}}
            (obsidian_dir / "graph.json").write_text(
                json.dumps({"colorGroups": [custom_group]}),
                encoding="utf-8",
            )

            obsidian_vault_setup.configure_vault(root, dry_run=False)

            graph = json.loads((obsidian_dir / "graph.json").read_text(encoding="utf-8"))
            self.assertIn(custom_group, graph["colorGroups"])
            queries = [item["query"] for item in graph["colorGroups"]]
            self.assertEqual(queries.count('path:"5. Trackers"'), 1)


if __name__ == "__main__":
    unittest.main()
