"""Regression tests for local MarkItDown intake and skill routing."""

from __future__ import annotations

import stat
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = ROOT_DIR / "system"
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import harness_registry, markdown_intake, sync_cli_adapters


class TestMarkdownIntake(unittest.TestCase):
    def make_converter(self, root: Path) -> list[str]:
        converter = root / "fake_markitdown.py"
        converter.write_text(
            textwrap.dedent(
                r"""
                #!/usr/bin/env python3
                import argparse
                from pathlib import Path

                parser = argparse.ArgumentParser()
                parser.add_argument("input")
                parser.add_argument("-o", "--output", required=True)
                args = parser.parse_args()
                source = Path(args.input)
                Path(args.output).write_text(
                    f"# {source.stem}\n\nConverted content\n", encoding="utf-8"
                )
                """
            ).lstrip(),
            encoding="utf-8",
        )
        converter.chmod(converter.stat().st_mode | stat.S_IXUSR)
        return [str(converter)]

    def test_conversion_preserves_source_and_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "brief.docx"
            source.write_bytes(b"source bytes")

            result = markdown_intake.convert_file(
                source,
                command=self.make_converter(root),
            )

            output = root / "brief.md"
            self.assertEqual(source.read_bytes(), b"source bytes")
            self.assertEqual(Path(result["output"]), output.resolve())
            self.assertIn("Converted content", output.read_text(encoding="utf-8"))

    def test_existing_output_requires_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "brief.pdf"
            output = root / "brief.md"
            source.write_bytes(b"pdf")
            output.write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(markdown_intake.MarkdownIntakeError, "already exists"):
                markdown_intake.convert_file(
                    source,
                    command=self.make_converter(root),
                )

            self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_automatic_intake_preserves_screenshot_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "screen.png"
            source.write_bytes(b"image")

            with self.assertRaisesRegex(markdown_intake.MarkdownIntakeError, "automatic intake"):
                markdown_intake.validate_source(source, automatic=True)

            self.assertEqual(markdown_intake.validate_source(source), source.resolve())

    def test_unavailable_converter_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "brief.docx"
            source.write_bytes(b"source")

            with mock.patch.object(markdown_intake, "converter_command", return_value=None):
                with self.assertRaisesRegex(
                    markdown_intake.MarkdownIntakeError,
                    "MarkItDown is unavailable",
                ):
                    markdown_intake.convert_file(source)

    def test_skill_harness_and_runtime_adapters_route_conversion(self):
        skill_path = ROOT_DIR / ".agent" / "skills" / "markitdown" / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        gemini = (ROOT_DIR / ".agent" / "rules" / "GEMINI.md").read_text(encoding="utf-8")
        paste = (ROOT_DIR / ".agent" / "workflows" / "paste.md").read_text(encoding="utf-8")

        self.assertIn("PDF, Word, PowerPoint, Excel", skill)
        self.assertIn("system/scripts/markdown_intake.py", skill)
        self.assertIn(".agent/skills/markitdown/SKILL.md", gemini)
        self.assertIn("markdown_intake.py", paste)
        self.assertIn(".agent/skills/markitdown/SKILL.md", sync_cli_adapters.render_agents_md())
        self.assertIn(".agent/skills/markitdown/SKILL.md", sync_cli_adapters.render_claude_md())
        self.assertIn(".agent/skills/markitdown/SKILL.md", sync_cli_adapters.render_gemini_md())
        manifest = harness_registry.resolve_harness_skill("markitdown", ROOT_DIR)
        self.assertEqual(manifest["entrypoint"], ".agent/skills/markitdown/SKILL.md")
        self.assertEqual(manifest["response"]["final"], "artifact")


if __name__ == "__main__":
    unittest.main()
