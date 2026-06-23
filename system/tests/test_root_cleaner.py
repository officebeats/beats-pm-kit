import tempfile
import unittest
from pathlib import Path


from system.scripts.root_cleaner import clean_root


class TestRootCleanerRealUse(unittest.TestCase):
    def test_moves_unknown_root_content_without_touching_public_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for name in ["AGENTS.md", "README.md", "VERSION", "install.sh"]:
                (root / name).write_text(f"{name}\n", encoding="utf-8")
            (root / ".agent").mkdir()
            (root / "system").mkdir()
            (root / "0. Incoming").mkdir()
            (root / "scratch-notes.md").write_text("local planning notes\n", encoding="utf-8")
            (root / "outputs").mkdir()
            (root / "outputs" / "draft.md").write_text("draft\n", encoding="utf-8")
            (root / ".kilocode" / "skills 2").mkdir(parents=True)
            (root / "system" / "context_cache.json").write_text("{}", encoding="utf-8")

            dry_run = clean_root(root, apply=False, stamp="20260101-000000")
            self.assertGreaterEqual(len(dry_run), 3)
            self.assertTrue((root / "scratch-notes.md").exists())

            actions = clean_root(root, apply=True, stamp="20260101-000000")
            action_paths = {action.path for action in actions}

            self.assertIn("scratch-notes.md", action_paths)
            self.assertIn("outputs", action_paths)
            self.assertIn("system/context_cache.json", action_paths)
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertFalse((root / "scratch-notes.md").exists())
            self.assertTrue(
                (root / "0. Incoming" / "root-cleanup" / "20260101-000000" / "scratch-notes.md").exists()
            )
            self.assertTrue(
                (root / "0. Incoming" / "root-cleanup" / "20260101-000000" / "outputs" / "draft.md").exists()
            )
            self.assertFalse((root / ".kilocode" / "skills 2").exists())


if __name__ == "__main__":
    unittest.main()
