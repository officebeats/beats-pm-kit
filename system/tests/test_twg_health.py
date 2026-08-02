"""Tests for the privacy-safe optional TWG health probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from system.scripts import twg_health


class TestTWGHealth(unittest.TestCase):
    def test_missing_binary_uses_existing_atlassian_fallbacks(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(twg_health.shutil, "which", return_value=None):
            status = twg_health.health_status(home=Path(tmp), probe=False)
        self.assertFalse(status.installed)
        self.assertEqual(status.fallback, "rovo_or_local_atlassian_artifacts")

    def test_doctor_output_is_sanitized(self):
        payload = {
            "data": {
                "build": {"version": "1.1.1"},
                "auth": {"config": {"loaded": True, "fields": {"authMethod": "oauth"}}, "resolved": {"site": "private.example", "tokenPresent": True}},
                "connectivity": {"ok": True},
                "skills": {"freshness": [{"status": "current"}]},
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "twg"
            binary.touch()
            binary.chmod(0o755)
            completed = twg_health.subprocess.CompletedProcess([str(binary)], 0, json.dumps(payload), "secret stderr")
            with patch.object(twg_health.subprocess, "run", return_value=completed):
                status = twg_health.health_status(binary_path=str(binary))
        serialized = json.dumps(twg_health.asdict(status))
        self.assertEqual(status.status, "healthy")
        self.assertNotIn("private.example", serialized)
        self.assertNotIn("tokenPresent", serialized)
        self.assertNotIn("secret stderr", serialized)

    def test_policy_rejects_mutation_categories(self):
        status = twg_health.unavailable()
        self.assertIn("work query", status.read_only_families)
        self.assertIn("transition", status.disallowed_actions)
        self.assertEqual(status.policy_mode, "read_only")


if __name__ == "__main__":
    unittest.main()
