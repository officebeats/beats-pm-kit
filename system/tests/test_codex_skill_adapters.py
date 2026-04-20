"""
Codex skill adapter generation tests
====================================
Protects the Antigravity-first / Codex-second command promotion model.
"""

import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import sync_codex_skill_adapters
from utils.command_registry import get_promoted_codex_commands


class TestCodexSkillAdapters(unittest.TestCase):
    """Regression tests for promoted Codex skill generation."""

    def test_promoted_skill_generation_matches_registry(self):
        """Every promoted command should generate one Codex skill adapter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = sync_codex_skill_adapters.sync_promoted_skills(
                output_dir=tmpdir,
                root=ROOT_DIR,
            )

            expected = {
                entry["codex_skill_name"] for entry in get_promoted_codex_commands(ROOT_DIR)
            }
            self.assertEqual(set(generated), expected)

            for skill_name in expected:
                with self.subTest(skill_name=skill_name):
                    self.assertTrue((Path(tmpdir) / skill_name / "SKILL.md").exists())

    def test_generated_day_skill_mentions_aliases_and_optional_files(self):
        """The /day adapter should carry the repo workflow, aliases, and optional files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-day" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("`/day`", content)
            self.assertIn("`/status`", content)
            self.assertIn("<repo>/.agent/workflows/day.md", content)
            self.assertIn("<repo>/STATUS.md", content)
            self.assertIn("<repo>/5. Trackers/bugs/bugs-master.md", content)

    def test_dispatch_only_commands_do_not_generate_skills(self):
        """Commands not promoted in the registry should not be emitted as Codex skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            self.assertFalse((Path(tmpdir) / "beats-discover").exists())
            self.assertFalse((Path(tmpdir) / "beats-prioritize").exists())

    def test_guarded_update_skill_mentions_safety_block(self):
        """Guarded native skills should include an explicit Codex safety section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_codex_skill_adapters.sync_promoted_skills(output_dir=tmpdir, root=ROOT_DIR)
            skill_md = Path(tmpdir) / "beats-update" / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")

            self.assertIn("## Safety", content)
            self.assertIn("state-changing", content)
            self.assertIn("If the repo is dirty or not on main", content)


if __name__ == "__main__":
    unittest.main()
