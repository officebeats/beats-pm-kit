"""Capability-driven runtime detection tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import detect_runtime


class TestRuntimeDetection(unittest.TestCase):
    def test_single_active_runtime_is_primary_and_versioned(self):
        root = Path(tempfile.mkdtemp())

        result = detect_runtime.detect_runtime(
            root=root,
            env={"CODEX_THREAD_ID": "thread"},
            which=lambda name: f"C:/bin/{name}.exe" if name == "codex" else None,
            version_probe=lambda _command: "codex 9.9.0",
        )

        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["primary"], "codex")
        self.assertEqual(result["primary_version"], "codex 9.9.0")
        self.assertIn("deep", result["supported_profiles"])
        self.assertTrue(detect_runtime.capability_supported(result, "filesystem_read"))

    def test_available_adapters_do_not_create_brand_priority(self):
        root = Path(tempfile.mkdtemp())
        (root / ".agent").mkdir()
        (root / ".claude").mkdir()

        result = detect_runtime.detect_runtime(
            root=root,
            env={},
            which=lambda _name: None,
            version_probe=lambda _command: None,
        )

        self.assertEqual(result["primary"], "unknown")
        self.assertEqual(result["active_count"], 0)
        self.assertEqual(set(result["all_runtimes"]), {"antigravity", "claude"})
        self.assertEqual(result["available_runtimes"], [])
        self.assertEqual(result["capabilities"], [])
        self.assertTrue(all(not item["available"] for item in result["details"]))
        self.assertTrue(all(item["capabilities"] == [] for item in result["details"]))

    def test_multiple_active_runtime_markers_fail_closed(self):
        root = Path(tempfile.mkdtemp())

        result = detect_runtime.detect_runtime(
            root=root,
            env={"CODEX_THREAD_ID": "thread", "CLAUDECODE": "1"},
            which=lambda _name: None,
            version_probe=lambda _command: None,
        )

        self.assertEqual(result["primary"], "unknown")
        self.assertEqual(result["selection_status"], "ambiguous")
        self.assertEqual(result["capabilities"], [])

    def test_unknown_capability_is_denied(self):
        result = {"capabilities": ["filesystem_read"]}

        self.assertFalse(detect_runtime.capability_supported(result, "telepathy"))


if __name__ == "__main__":
    unittest.main()
