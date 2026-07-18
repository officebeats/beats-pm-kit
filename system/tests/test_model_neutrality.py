"""Guards against provider-pinned tracked runtime behavior."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HARDCODED_MODEL_RE = re.compile(
    r"(?:claude-(?:(?:opus|sonnet|haiku)-)?[0-9][A-Za-z0-9.-]*|gemini(?:/gemini)?-[0-9][A-Za-z0-9.-]*|gpt-[0-9][A-Za-z0-9.-]*)",
    re.IGNORECASE,
)


class TestModelNeutrality(unittest.TestCase):
    def test_all_canonical_agents_inherit_the_runtime_model(self):
        for path in sorted((ROOT / ".agent" / "agents").glob("*.md")):
            with self.subTest(path=path.name):
                model_lines = [
                    line.strip()
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line.startswith("model:")
                ]
                self.assertTrue(all(line == "model: inherit" for line in model_lines))

    def test_tracked_runtime_code_has_no_hardcoded_model_identifiers(self):
        result = subprocess.run(
            ["git", "ls-files", ".agent", "system"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        violations: list[str] = []
        for relative in result.stdout.splitlines():
            path = ROOT / relative
            if not path.is_file() or relative.startswith("system/tests/") or relative.startswith("system/evals/"):
                continue
            if path.suffix.lower() not in {".py", ".md", ".json", ".yml", ".yaml"}:
                continue
            for match in HARDCODED_MODEL_RE.finditer(path.read_text(encoding="utf-8", errors="replace")):
                violations.append(f"{relative}: {match.group(0)}")
        self.assertEqual(violations, [])

    def test_legacy_cli_is_dependency_free_compatibility_only(self):
        cli_dir = ROOT / "system" / "cli"
        self.assertTrue((cli_dir / "beats_cli.py").is_file())
        self.assertFalse((cli_dir / "router.py").exists())
        self.assertFalse((cli_dir / "config.py").exists())
        self.assertFalse((cli_dir / "requirements.txt").exists())
        content = (cli_dir / "beats_cli.py").read_text(encoding="utf-8")
        for dependency in ("litellm", "typer", "rich", "yaml", "dotenv"):
            self.assertNotIn(dependency, content)


if __name__ == "__main__":
    unittest.main()
