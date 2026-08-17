"""Tests for the SKILL.md Quick Path advisory linter."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from system.scripts import skill_lint


def make_skill(root: Path, name: str, body: str, description: str = "Test skill.") -> Path:
    skill_dir = root / ".agent" / "skills" / name
    skill_dir.mkdir(parents=True)
    text = f"---\nname: {name}\ndescription: {description}\n---\n\n{body}"
    path = skill_dir / "SKILL.md"
    path.write_text(text, encoding="utf-8")
    return path


COMPLIANT_BODY = (
    "# Big Skill\n\n"
    "## Quick Path\n\n"
    "1. Do the first thing.\n"
    "2. Do the second thing.\n"
    "3. Do the third thing.\n\n"
    "Go deeper for edge cases.\n\n"
    "## Details\n\n" + ("x" * 6000) + "\n"
)


class TestAnalyzeText(unittest.TestCase):
    def test_detects_present_quick_path(self):
        record = skill_lint.analyze_text("---\nname: a\ndescription: d\n---\n" + COMPLIANT_BODY)
        self.assertTrue(record["has_quick_path"])
        self.assertTrue(record["quick_path_first"])
        self.assertTrue(record["required"])
        self.assertTrue(record["compliant"])
        self.assertGreater(record["quick_path_chars"], 0)
        self.assertLessEqual(record["quick_path_chars"], skill_lint.QUICK_PATH_MAX_CHARS)
        self.assertEqual(record["description_chars"], 1)

    def test_detects_absent_quick_path(self):
        record = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Big Skill\n\n## Details\n" + "x" * 6000
        )
        self.assertFalse(record["has_quick_path"])
        self.assertEqual(record["quick_path_chars"], 0)
        self.assertTrue(record["required"])
        self.assertFalse(record["compliant"])

    def test_small_skill_not_required(self):
        record = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Small Skill\n\n## Details\nshort body\n"
        )
        self.assertFalse(record["required"])
        self.assertFalse(record["compliant"])

    def test_quick_path_not_first_h2_is_noncompliant(self):
        record = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Big Skill\n\n## Details\n"
            + "x" * 6000
            + "\n\n## Quick Path\n\n1. Late step.\n"
        )
        self.assertTrue(record["has_quick_path"])
        self.assertFalse(record["quick_path_first"])
        self.assertFalse(record["compliant"])

    def test_oversized_quick_path_is_noncompliant(self):
        record = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Big Skill\n\n## Quick Path\n\n"
            + "y" * (skill_lint.QUICK_PATH_MAX_CHARS + 1)
            + "\n\n## Details\n"
            + "x" * 6000
        )
        self.assertTrue(record["has_quick_path"])
        self.assertFalse(record["compliant"])

    def test_body_bytes_excludes_quick_path_section(self):
        without = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Skill\n\n## Details\nbody\n"
        )
        with_qp = skill_lint.analyze_text(
            "---\nname: a\ndescription: d\n---\n# Skill\n\n"
            "## Quick Path\n\n1. Step.\n\n## Details\nbody\n"
        )
        self.assertEqual(without["body_bytes"], with_qp["body_bytes"])


class TestStrictMode(unittest.TestCase):
    def test_strict_fails_on_required_skill_without_quick_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "big-bare", "# Big\n\n## Details\n" + "x" * 6000)
            self.assertEqual(skill_lint.main(["--root", tmp, "--strict"]), 1)
            self.assertEqual(skill_lint.main(["--root", tmp, "--report"]), 0)

    def test_strict_passes_when_required_skills_compliant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "big-ok", COMPLIANT_BODY)
            make_skill(root, "small-bare", "# Small\n\n## Details\nshort\n")
            self.assertEqual(skill_lint.main(["--root", tmp, "--strict"]), 0)

    def test_missing_skills_dir_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(skill_lint.main(["--root", tmp, "--strict"]), 2)


class TestRealRepo(unittest.TestCase):
    def test_module_cli_strict_passes_against_repo(self):
        result = subprocess.run(
            [sys.executable, "-m", "system.scripts.skill_lint", "--strict", "--json"],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"violations": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
