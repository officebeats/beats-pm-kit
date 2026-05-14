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
from utils.command_registry import get_runtime_priority


class TestAdapterGuardConfig(unittest.TestCase):
    """Validate the promoted command set and automation guard assumptions."""

    def test_pm_promoted_commands_include_boss_and_week(self):
        """High-frequency PM workflows should be promoted for Codex."""
        promoted = {entry["name"] for entry in get_promoted_codex_commands(ROOT_DIR)}
        expected = {
            "beats-comms",
            "beats-slack",
            "beats-teams",
            "boss",
            "create",
            "day",
            "deck",
            "discover",
            "meet",
            "obsidian",
            "office-cli",
            "paste",
            "plan",
            "prioritize",
            "review",
            "sop",
            "track",
            "transcript",
            "update",
            "vacuum",
            "vibe",
            "week",
        }
        self.assertEqual(promoted, expected)

    def test_codex_is_primary_runtime(self):
        """Codex should be the optimized default runtime."""
        priority = get_runtime_priority(ROOT_DIR)
        self.assertEqual(priority["primary"], "codex")
        self.assertEqual(priority["secondary"], "antigravity")

    def test_pre_commit_restages_only_tracked_generated_files(self):
        """Ignored generated adapters should sync locally without being force-added."""
        hook = (ROOT_DIR / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('git ls-files --error-unmatch "$generated"', hook)
        self.assertNotIn("git add -f AGENTS.md CODEX_COMMANDS.md .codex/rules.md .claude/CLAUDE.md", hook)

    def test_project_codex_custom_agents_exist(self):
        """Codex custom agents should be project-scoped TOML files."""
        agents_dir = ROOT_DIR / ".codex" / "agents"
        self.assertTrue(agents_dir.is_dir())
        expected = {
            "pm-explorer.toml",
            "pm-writer.toml",
            "verifier.toml",
            "docs-researcher.toml",
            "comms-intake-reviewer.toml",
        }
        actual = {path.name for path in agents_dir.glob("*.toml")}
        self.assertTrue(expected.issubset(actual))
        for path in agents_dir.glob("*.toml"):
            content = path.read_text(encoding="utf-8")
            self.assertIn("name =", content)
            self.assertIn("description =", content)
            self.assertIn("developer_instructions", content)


if __name__ == "__main__":
    unittest.main()
