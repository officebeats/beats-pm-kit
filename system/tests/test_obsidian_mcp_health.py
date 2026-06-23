from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import obsidian_mcp_health


class TestObsidianMCPHealth(unittest.TestCase):
    def test_missing_api_key_falls_back_to_rg(self):
        status = obsidian_mcp_health.health_status(
            url="https://127.0.0.1:27124/mcp/",
            api_key="",
            probe=False,
        )
        self.assertFalse(status.configured)
        self.assertFalse(status.available)
        self.assertEqual(status.fallback, "rg")
        self.assertIn("Missing OBSIDIAN_API_KEY", status.issues[0])

    def test_read_only_policy_excludes_write_tools(self):
        status = obsidian_mcp_health.health_status(
            url="https://127.0.0.1:27124/mcp/",
            api_key="test-key",
            probe=False,
        )
        self.assertIn("vault_read", status.read_only_tools)
        self.assertIn("search_simple", status.read_only_tools)
        self.assertIn("open_file", status.read_only_tools)
        self.assertIn("vault_write", status.disallowed_tools)
        self.assertIn("vault_patch", status.disallowed_tools)
        self.assertNotIn("vault_write", status.read_only_tools)
        self.assertEqual(status.fallback, "rg_if_unavailable")


if __name__ == "__main__":
    unittest.main()
