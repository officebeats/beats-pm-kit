from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from system.scripts import agent_memory_health


class TestAgentMemoryHealth(unittest.TestCase):
    def test_missing_config_falls_back_to_obsidian_then_rg(self):
        status = agent_memory_health.health_status(env={})
        self.assertEqual(status.provider, "tenscentdb")
        self.assertFalse(status.configured)
        self.assertEqual(status.fallback, "obsidian_mcp_then_rg")
        self.assertIn("AGENT_MEMORY_URL or TENCENTDB_URL", status.missing_env)

    def test_tencentdb_alias_is_supported(self):
        status = agent_memory_health.health_status(
            env={
                "AGENT_MEMORY_PROVIDER": "tencentdb",
                "TENCENTDB_URL": "https://example.invalid/memory",
                "TENCENTDB_API_KEY": "test-key",
                "TENCENTDB_NAMESPACE": "kit",
            }
        )
        self.assertTrue(status.configured)
        self.assertTrue(status.available)
        self.assertEqual(status.provider, "tencentdb")
        self.assertEqual(status.namespace, "kit")
        self.assertIn("semantic_search", status.allowed_operations)
        self.assertIn("external_memory_write", status.disallowed_operations)

    def test_unsupported_provider_is_not_configured(self):
        status = agent_memory_health.health_status(
            env={
                "AGENT_MEMORY_PROVIDER": "otherdb",
                "AGENT_MEMORY_URL": "https://example.invalid/memory",
                "AGENT_MEMORY_API_KEY": "test-key",
            }
        )
        self.assertFalse(status.configured)
        self.assertIn("Unsupported agent memory provider", status.issues[0])


if __name__ == "__main__":
    unittest.main()
