"""Tests for vibe_check MCP config drift and token hotspot reporting."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from system.scripts import vibe_check


ROOT = Path(__file__).resolve().parents[2]


class TestCollectMcpServers(unittest.TestCase):
    def test_reads_both_client_config_shapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"dotcontext": {"command": "npx", "args": ["-y", "@dotcontext/mcp@latest"]}}}),
                encoding="utf-8",
            )
            (root / ".vscode").mkdir()
            (root / ".vscode" / "mcp.json").write_text(
                json.dumps({"servers": {"dotcontext": {"type": "stdio", "command": "npx"}}}),
                encoding="utf-8",
            )
            observed = vibe_check.collect_mcp_servers(root, [".mcp.json", ".vscode/mcp.json", ".cursor/mcp.json"])
            self.assertEqual(
                observed,
                [
                    {"name": "dotcontext", "source_file": ".mcp.json", "command": "npx"},
                    {"name": "dotcontext", "source_file": ".vscode/mcp.json", "command": "npx"},
                ],
            )

    def test_url_fallback_and_malformed_config_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.json").write_text(
                json.dumps({"servers": {"slack": {"transport": "http", "url": "https://mcp.example"}}}),
                encoding="utf-8",
            )
            (root / "b.json").write_text("{broken", encoding="utf-8")
            observed = vibe_check.collect_mcp_servers(root, ["a.json", "b.json"])
            self.assertEqual(observed, [{"name": "slack", "source_file": "a.json", "command": "https://mcp.example"}])


class TestMcpConfigDrift(unittest.TestCase):
    def test_flags_unknown_and_missing_servers(self):
        observed = [
            {"name": "dotcontext", "source_file": ".mcp.json", "command": "npx"},
            {"name": "rogue", "source_file": ".mcp.json", "command": "npx"},
        ]
        allowlisted = [
            {"name": "dotcontext", "source_file": ".mcp.json", "command": "npx", "note": ""},
            {"name": "ms365", "source_file": "system/config/mcp.template.json", "command": "npx", "note": ""},
        ]
        drift = vibe_check.mcp_config_drift(observed, allowlisted)
        self.assertEqual([item["name"] for item in drift["unknown"]], ["rogue"])
        self.assertEqual([item["name"] for item in drift["missing"]], ["ms365"])

    def test_seeded_baseline_has_no_unknown_servers_in_real_repo(self):
        allowlist = json.loads((ROOT / vibe_check.MCP_ALLOWLIST_REL).read_text(encoding="utf-8"))
        observed = vibe_check.collect_mcp_servers(ROOT, allowlist["config_files"])
        drift = vibe_check.mcp_config_drift(observed, allowlist["servers"])
        self.assertEqual(drift["unknown"], [], "every configured MCP server must be allowlisted")
        # The tracked template must always be present, so its servers can never be missing.
        template_missing = [
            item for item in drift["missing"] if item["source_file"] == "system/config/mcp.template.json"
        ]
        self.assertEqual(template_missing, [])


if __name__ == "__main__":
    unittest.main()
