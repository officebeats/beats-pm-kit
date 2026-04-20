"""
Adapter guard regression tests.
"""

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from utils.command_registry import get_promoted_codex_commands


class TestAdapterGuardConfig(unittest.TestCase):
    """Validate the promoted command set and automation guard assumptions."""

    def test_pm_promoted_commands_include_boss_and_week(self):
        """High-frequency PM workflows should be promoted for Codex."""
        promoted = {entry["name"] for entry in get_promoted_codex_commands(ROOT_DIR)}
        self.assertIn("boss", promoted)
        self.assertIn("week", promoted)
        self.assertIn("update", promoted)
        self.assertIn("vacuum", promoted)

    def test_discover_and_prioritize_remain_dispatch_only_for_now(self):
        """Hold back lower-confidence workflows until their skill wiring is normalized."""
        promoted = {entry["name"] for entry in get_promoted_codex_commands(ROOT_DIR)}
        self.assertNotIn("discover", promoted)
        self.assertNotIn("prioritize", promoted)

    def test_pre_commit_restages_only_tracked_generated_files(self):
        """Ignored generated adapters should sync locally without being force-added."""
        hook = (ROOT_DIR / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('git ls-files --error-unmatch "$generated"', hook)
        self.assertNotIn("git add -f AGENTS.md CODEX_COMMANDS.md .codex/rules.md .claude/CLAUDE.md", hook)


if __name__ == "__main__":
    unittest.main()
