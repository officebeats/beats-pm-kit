"""
Codex browser-first policy tests.

Keeps the Codex runtime adapter aligned with the kit preference that browser
work should stay inside the Codex in-app Browser unless an external browser is
needed for a specific reason.
"""

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import sync_cli_adapters


class TestCodexBrowserFirstPolicy(unittest.TestCase):
    """Regression coverage for Codex Browser-first instructions."""

    def test_canonical_rule_exists(self):
        rule = ROOT_DIR / ".agent" / "rules" / "codex-browser-first.md"
        content = rule.read_text(encoding="utf-8")

        self.assertIn("Use the Codex in-app Browser first", content)
        self.assertIn("External Browser Fallback", content)
        self.assertIn("state the reason briefly", content)

    def test_generated_agents_md_includes_browser_first_policy(self):
        content = sync_cli_adapters.render_agents_md()

        self.assertIn("## Codex Browser First", content)
        self.assertIn("Use the Codex in-app Browser first", content)
        self.assertIn("Do not default to macOS `open`, Chrome, Edge, Safari, Computer Use, or standalone Playwright", content)
        self.assertIn("State the reason briefly before using the external browser", content)


if __name__ == "__main__":
    unittest.main()
