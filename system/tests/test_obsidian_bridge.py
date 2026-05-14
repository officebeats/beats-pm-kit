import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import obsidian_bridge


class TestObsidianDetection(unittest.TestCase):
    def test_windows_detection_validates_saved_vault_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            appdata = tmp_path / "Roaming"
            local = tmp_path / "Local"
            valid_vault = tmp_path / "Vault"
            valid_vault.mkdir()
            (valid_vault / ".obsidian").mkdir()
            missing_vault = tmp_path / "Missing"
            global_config = appdata / "obsidian" / "obsidian.json"
            global_config.parent.mkdir(parents=True)
            global_config.write_text(
                json.dumps(
                    {
                        "vaults": {
                            "valid123": {"path": str(valid_vault), "ts": 2, "open": True},
                            "stale123": {"path": str(missing_vault), "ts": 3, "open": False},
                        }
                    }
                ),
                encoding="utf-8",
            )
            exe = local / "Programs" / "Obsidian" / "Obsidian.exe"
            exe.parent.mkdir(parents=True)
            exe.write_text("", encoding="utf-8")

            result = obsidian_bridge.detect_obsidian(
                platform_name="Windows",
                home=tmp_path,
                env={
                    "APPDATA": str(appdata),
                    "LOCALAPPDATA": str(local),
                    "ProgramFiles": str(tmp_path / "Program Files"),
                },
                registry_command='"C:\\Obsidian\\Obsidian.exe" "%1"',
                command_lookup=lambda _: None,
                rest_probe=lambda: {"url": "https://127.0.0.1:27124/", "reachable": False},
                spotlight_paths=[],
            )

            self.assertTrue(result["installed"])
            self.assertEqual(len(result["valid_vaults"]), 1)
            self.assertEqual(result["valid_vaults"][0]["id"], "valid123")
            self.assertEqual(len(result["stale_vaults"]), 1)
            self.assertEqual(result["stale_vaults"][0]["id"], "stale123")

    def test_macos_detection_reads_application_support_vaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            vault = tmp_path / "Notes"
            vault.mkdir()
            app = tmp_path / "Applications" / "Obsidian.app"
            app.mkdir(parents=True)
            global_config = tmp_path / "Library" / "Application Support" / "obsidian" / "obsidian.json"
            global_config.parent.mkdir(parents=True)
            global_config.write_text(
                json.dumps({"vaults": {"macvault": {"path": str(vault), "ts": 1}}}),
                encoding="utf-8",
            )

            result = obsidian_bridge.detect_obsidian(
                platform_name="Darwin",
                home=tmp_path,
                env={},
                extra_app_paths=[app],
                command_lookup=lambda _: None,
                rest_probe=lambda: {"url": "https://127.0.0.1:27124/", "reachable": False},
                spotlight_paths=[],
            )

            self.assertTrue(result["installed"])
            self.assertEqual(result["valid_vaults"][0]["id"], "macvault")
            self.assertIn(str(app), result["app_paths"])

    def test_no_install_has_no_valid_vaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = obsidian_bridge.detect_obsidian(
                platform_name="Linux",
                home=tmp_path,
                env={},
                command_lookup=lambda _: None,
                rest_probe=lambda: {"url": "https://127.0.0.1:27124/", "reachable": False},
                spotlight_paths=[],
            )

            self.assertFalse(result["installed"])
            self.assertEqual(result["valid_vaults"], [])


class TestObsidianSync(unittest.TestCase):
    def make_root(self, tmp_path: Path) -> Path:
        root = tmp_path / "kit"
        (root / "3. Meetings").mkdir(parents=True)
        (root / "5. Trackers").mkdir(parents=True)
        (root / "3. Meetings" / "notes.md").write_text(
            "# Notes\n\n- **Owner**: Pat\n- **Priority**: now\n",
            encoding="utf-8",
        )
        (root / "5. Trackers" / "custom.md").write_text(
            "---\ntitle: Human Frontmatter\n---\n\n# Keep Me\n",
            encoding="utf-8",
        )
        return root

    def test_sync_is_idempotent_and_preserves_human_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self.make_root(tmp_path)
            vault = tmp_path / "vault"
            vault.mkdir()
            config = {
                "mode": "sync",
                "vault_path": str(vault),
                "target_folder": "Work",
                "dashboard_note": "OBSIDIAN.md",
            }

            first = obsidian_bridge.run_sync(config=config, root=root, dry_run=False)
            second = obsidian_bridge.run_sync(config=config, root=root, dry_run=False)

            synced = vault / "Work" / "Meetings" / "notes.md"
            text = synced.read_text(encoding="utf-8")
            self.assertEqual(first.new, 3)
            self.assertEqual(second.updated, 0)
            self.assertGreaterEqual(second.skipped, 3)
            self.assertEqual(text.count("source: beats-pm-kit"), 1)
            self.assertIn("priority: \"now\"", text)
            self.assertIn("owner: \"Pat\"", text)

            human = vault / "Work" / "Trackers" / "custom.md"
            self.assertNotIn("source: beats-pm-kit", human.read_text(encoding="utf-8"))
            self.assertIn("title: Human Frontmatter", human.read_text(encoding="utf-8"))

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self.make_root(tmp_path)
            vault = tmp_path / "vault"
            vault.mkdir()
            config = {"mode": "sync", "vault_path": str(vault), "target_folder": "Work"}

            stats = obsidian_bridge.run_sync(config=config, root=root, dry_run=True)

            self.assertGreater(stats.new, 0)
            self.assertFalse((vault / "Work").exists())

    def test_clean_removes_only_managed_stale_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self.make_root(tmp_path)
            vault = tmp_path / "vault"
            managed = vault / "Work" / "Meetings" / "old.md"
            human = vault / "Work" / "Meetings" / "human.md"
            managed.parent.mkdir(parents=True)
            managed.write_text("---\nsource: beats-pm-kit\n---\n\n# Old\n", encoding="utf-8")
            human.write_text("# Human note\n", encoding="utf-8")
            config = {"mode": "sync", "vault_path": str(vault), "target_folder": "Work"}

            stats = obsidian_bridge.run_sync(config=config, root=root, dry_run=False, clean=True)

            self.assertEqual(stats.removed, 1)
            self.assertFalse(managed.exists())
            self.assertTrue(human.exists())

    def test_mcp_template_contains_placeholders_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "mcp.obsidian.local.json"

            obsidian_bridge.write_mcp_template(output)
            text = output.read_text(encoding="utf-8")

            self.assertIn("<your-local-rest-api-key>", text)
            self.assertNotIn("admin" + "-beats", text)
            self.assertNotIn("O:\\", text)


class TestObsidianPrivacy(unittest.TestCase):
    def test_local_obsidian_config_is_gitignored(self):
        gitignore = (ROOT_DIR / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("system/config/obsidian.local*.json", gitignore)
        self.assertIn("system/config/mcp.*.local.json", gitignore)


if __name__ == "__main__":
    unittest.main()
