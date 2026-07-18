"""Legacy CLI entrypoint compatibility tests."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_cli():
    path = ROOT / "system" / "cli" / "beats_cli.py"
    spec = importlib.util.spec_from_file_location("legacy_beats_cli", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class TestLegacyCli(unittest.TestCase):
    def test_discover_routes_to_canonical_workflow_without_calling_provider(self):
        cli = load_cli()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            code = cli.main(["discover"])

        self.assertEqual(code, 0)
        self.assertIn(".agent/workflows/discover.md", output.getvalue())
        self.assertIn("deprecated compatibility shim", output.getvalue())

    def test_dashboard_points_to_markdown_task_tracking(self):
        cli = load_cli()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            code = cli.main(["dashboard"])

        self.assertEqual(code, 0)
        self.assertIn("5. Trackers/TASK_MASTER.md", output.getvalue())


if __name__ == "__main__":
    unittest.main()
