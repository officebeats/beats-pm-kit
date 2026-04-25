"""
Codex Adapter Regression Tests
==============================
Protects the Codex-specific adapter layer:
- explicit slash-command routing
- generated command index coverage
- workflow resolution via beats.py
"""

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import beats, sync_cli_adapters


class TestCodexAdapter(unittest.TestCase):
    """Regression tests for Codex-specific adapter behavior."""

    @classmethod
    def setUpClass(cls):
        generated_files = [
            ROOT_DIR / "AGENTS.md",
            ROOT_DIR / "CODEX_COMMANDS.md",
            ROOT_DIR / "CODEX_PROMPT.md",
            ROOT_DIR / ".codex" / "rules.md",
        ]
        if any(not path.exists() for path in generated_files):
            sync_cli_adapters.main()

        cls.workflow_meta = sync_cli_adapters.get_workflow_descriptions()
        cls.command_catalog = sync_cli_adapters.get_command_catalog()
        cls.workflow_names = [name for name, _ in cls.workflow_meta]
        cls.command_index = (ROOT_DIR / "CODEX_COMMANDS.md").read_text(encoding="utf-8")
        cls.agents_md = (ROOT_DIR / "AGENTS.md").read_text(encoding="utf-8")
        cls.codex_rules = (ROOT_DIR / ".codex" / "rules.md").read_text(encoding="utf-8")
        cls.codex_prompt = (ROOT_DIR / "CODEX_PROMPT.md").read_text(encoding="utf-8")

    def test_codex_command_index_exists(self):
        """Codex must have an explicit slash-command routing table."""
        self.assertTrue((ROOT_DIR / "CODEX_COMMANDS.md").exists(), "CODEX_COMMANDS.md missing")

    def test_codex_command_index_covers_all_workflows(self):
        """Every workflow must be represented in the generated Codex command index."""
        for workflow in self.workflow_names:
            with self.subTest(workflow=workflow):
                row_fragment = f"| `/{workflow}` | `.agent/workflows/{workflow}.md` |"
                self.assertIn(
                    row_fragment,
                    self.command_index,
                    f"Missing Codex command routing entry for /{workflow}",
                )

    def test_codex_command_index_count_matches_workflows(self):
        """The number of command rows should match the number of workflows."""
        command_rows = [
            line for line in self.command_index.splitlines()
            if line.startswith("| `/")
        ]
        self.assertEqual(
            len(command_rows),
            len(self.workflow_names),
            "CODEX_COMMANDS.md command count drifted from .agent/workflows",
        )

    def test_codex_command_index_marks_promoted_skills(self):
        """Promoted commands should advertise their native Codex skill adapters."""
        self.assertIn("Native skill `beats-day`", self.command_index)
        self.assertIn("Native skill `beats-track`", self.command_index)
        self.assertIn("Native skill `beats-boss`", self.command_index)
        self.assertIn("Native skill `beats-week`", self.command_index)

    def test_codex_command_index_keeps_update_dispatch_only(self):
        """Dangerous workflows should be available as guarded Codex skills."""
        self.assertIn("| `/update` | `.agent/workflows/update.md` | Guarded skill `beats-update` |", self.command_index)
        self.assertIn("| `/vacuum` | `.agent/workflows/vacuum.md` | Guarded skill `beats-vacuum` |", self.command_index)

    def test_agents_md_enforces_slash_command_dispatch(self):
        """AGENTS.md should tell Codex to treat leading /commands as workflow dispatch."""
        self.assertIn("## Runtime Priority", self.agents_md)
        self.assertIn("**Antigravity first**", self.agents_md)
        self.assertIn("## Slash Command Dispatch", self.agents_md)
        self.assertIn("If the user's message starts with `/command`:", self.agents_md)
        self.assertIn("Resolve it using `CODEX_COMMANDS.md`", self.agents_md)
        self.assertIn("If the command does not exist", self.agents_md)

    def test_codex_rules_enforce_slash_command_dispatch(self):
        """The Codex runtime notes must preserve explicit command routing."""
        self.assertIn("## Slash Command Dispatch", self.codex_rules)
        self.assertIn("follow the explicit dispatch rule in `CODEX_COMMANDS.md`", self.codex_rules)
        self.assertIn("If the user's first non-whitespace token is `/command`:", self.codex_rules)
        self.assertIn("If no workflow exists, report an unknown command and suggest `/help`", self.codex_rules)

    def test_codex_prompt_mentions_explicit_dispatch(self):
        """The manual bootstrap prompt should reinforce explicit command resolution."""
        self.assertIn("If my message starts with /command", self.codex_prompt)
        self.assertIn("Resolve it using CODEX_COMMANDS.md", self.codex_prompt)

    def test_beats_resolve_workflow_known_command(self):
        """beats.resolve_workflow should map /day to the workflow file."""
        resolved = beats.resolve_workflow("/day")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved, ROOT_DIR / ".agent" / "workflows" / "day.md")

    def test_beats_resolve_workflow_alias_command(self):
        """Aliases in the command registry should resolve to the canonical workflow."""
        resolved = beats.resolve_workflow("/status focus on blockers")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved, ROOT_DIR / ".agent" / "workflows" / "day.md")

    def test_beats_resolve_workflow_unknown_command(self):
        """Unknown slash commands should not resolve to an arbitrary workflow."""
        self.assertIsNone(beats.resolve_workflow("/does-not-exist"))


if __name__ == "__main__":
    unittest.main()
