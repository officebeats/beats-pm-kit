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
        """Keep lower-frequency workflows dispatch-only while sharing normalized router wiring."""
        promoted = {entry["name"] for entry in get_promoted_codex_commands(ROOT_DIR)}
        self.assertNotIn("discover", promoted)
        self.assertNotIn("prioritize", promoted)

    def test_pre_commit_restages_only_tracked_generated_files(self):
        """Ignored generated adapters should sync locally without being force-added."""
        hook = (ROOT_DIR / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('git ls-files --error-unmatch "$generated"', hook)
        self.assertNotIn("git add -f AGENTS.md CODEX_COMMANDS.md .codex/rules.md .claude/CLAUDE.md", hook)
        self.assertIn("python3 system/scripts/privacy_guard.py --tree", hook)

    def test_generated_runtime_dirs_are_guarded_from_tracking(self):
        """Generated adapter directories should remain local-only artifacts."""
        from scripts import adapter_guard

        guarded = set(adapter_guard.FORBIDDEN_TRACKED_PREFIXES)
        for prefix in [".codex/", ".gemini/", ".claude/", ".kilocode/", ".context/"]:
            self.assertIn(prefix, guarded)

    def test_adapter_guard_checks_public_docs_catalog_drift(self):
        """Registry-backed public Markdown docs must be part of the release guard."""
        from scripts import adapter_guard

        self.assertTrue(callable(adapter_guard.run_public_docs_check))

    def test_kilocode_agent_tools_are_normalized_to_record_form(self):
        """KiloCode rejects comma-delimited tools strings in generated agent frontmatter."""
        from scripts import sync_cli_adapters

        content = "---\nname: reviewer\ntools: Read, Grep, Bash\n---\nBody\n"
        normalized = sync_cli_adapters.normalize_kilocode_agent_frontmatter(content)

        self.assertIn("tools:\n  Read: true\n  Grep: true\n  Bash: true", normalized)
        self.assertNotIn("tools: Read, Grep, Bash", normalized)

    def test_privacy_guard_enforces_private_workspace_skeletons(self):
        """Only .gitkeep files should be tracked in private workspace folders."""
        from scripts import privacy_guard

        finding_paths = {
            finding.rule
            for finding in privacy_guard.path_findings("3. Meetings/example-notes.md")
        }
        self.assertIn("private-workspace-content", finding_paths)

        clean_findings = privacy_guard.path_findings("3. Meetings/transcripts/.gitkeep")
        self.assertEqual(clean_findings, [])


if __name__ == "__main__":
    unittest.main()
