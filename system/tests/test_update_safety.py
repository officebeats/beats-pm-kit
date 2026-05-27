import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import update


class TestUpdateMigrationSafety(unittest.TestCase):
    def test_migration_scan_preserves_active_root_adapters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            active_adapters = [
                "AGENTS.md",
                "CLAUDE.md",
                "CODEX_COMMANDS.md",
                "GEMINI.md",
                "README.md",
                "VERSION",
                "install.sh",
            ]
            for name in active_adapters:
                (root / name).write_text(f"{name}\n", encoding="utf-8")
            (root / "SETTINGS.md").write_text("# Settings\n", encoding="utf-8")
            (root / "STATUS.md").write_text("# Status\n", encoding="utf-8")
            (root / "KERNEL.md").write_text("# Deprecated\n", encoding="utf-8")
            (root / "scratch-notes.md").write_text("# Notes\n", encoding="utf-8")
            (root / "Beats-PM-System").mkdir()
            (root / "0. Incoming").mkdir()

            original_root = update.BRAIN_ROOT
            try:
                update.BRAIN_ROOT = root
                update.migration_scan()
            finally:
                update.BRAIN_ROOT = original_root

            for name in active_adapters:
                with self.subTest(name=name):
                    self.assertTrue((root / name).exists())
                    self.assertFalse((root / "0. Incoming" / name).exists())

            self.assertFalse((root / "KERNEL.md").exists())
            cleanup_root = root / "0. Incoming" / "root-cleanup"
            moved_files = {path.name for path in cleanup_root.rglob("*") if path.is_file()}
            moved_dirs = {path.name for path in cleanup_root.rglob("*") if path.is_dir()}
            self.assertIn("scratch-notes.md", moved_files)
            self.assertIn("KERNEL.md", moved_files)
            self.assertIn("Beats-PM-System", moved_dirs)


if __name__ == "__main__":
    unittest.main()
