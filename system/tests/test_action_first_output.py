"""Regression coverage for the default action-first response policy."""

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import sync_cli_adapters


class TestActionFirstOutputPolicy(unittest.TestCase):
    """Keep one canonical response policy aligned across runtime adapters."""

    def test_canonical_policy_defines_behavior_and_compatibility_boundary(self):
        policy_path = ROOT_DIR / ".agent" / "rules" / "ACTION_FIRST_OUTPUT.md"
        content = policy_path.read_text(encoding="utf-8")

        self.assertIn(
            "Lead with the answer, completed outcome, or smallest useful next action",
            content,
        )
        self.assertIn("five items or fewer", content)
        self.assertIn("State failures matter-of-factly", content)
        self.assertIn("If work remains, end with one concrete next action", content)
        self.assertIn("## Precedence and Exceptions", content)
        self.assertIn("response profiles", content)
        self.assertIn("structured-output formats", content)
        self.assertIn("does not change the PM Decision Router", content)
        self.assertIn("plugin, hooks, and executable code are not vendored", content)

    def test_canonical_runtime_rule_loads_action_first_policy(self):
        content = (ROOT_DIR / ".agent" / "rules" / "GEMINI.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(".agent/rules/ACTION_FIRST_OUTPUT.md", content)
        self.assertIn("response profiles", content)

    def test_runtime_adapter_renderers_reference_canonical_policy(self):
        rendered = {
            "agents": sync_cli_adapters.render_agents_md(),
            "codex_rules": sync_cli_adapters.render_codex_rules(),
            "gemini": sync_cli_adapters.render_gemini_md(),
            "claude": sync_cli_adapters.render_claude_md(),
            "claude_runtime": sync_cli_adapters.render_claude_runtime(),
            "kilocode": sync_cli_adapters.render_kilocode_rules(),
        }

        for adapter, content in rendered.items():
            with self.subTest(adapter=adapter):
                self.assertIn("ACTION_FIRST_OUTPUT.md", content)

        self.assertIn("## Action-First Responses", rendered["agents"])
        self.assertIn("response profiles", rendered["agents"])


if __name__ == "__main__":
    unittest.main()
