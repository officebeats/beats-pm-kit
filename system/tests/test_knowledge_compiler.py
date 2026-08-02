"""Tests for the local PM knowledge compiler."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import knowledge_compiler


class TestKnowledgeCompiler(unittest.TestCase):
    def make_root(self) -> tempfile.TemporaryDirectory:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        source = root / "0. Incoming/source.md"
        source.parent.mkdir(parents=True)
        source.write_text("# Raw decision\n\nExact customer wording.\n", encoding="utf-8")
        return tmp

    def test_compiled_artifact_cites_raw_path_and_hash(self):
        with self.make_root() as tmp:
            root = Path(tmp)
            output = knowledge_compiler.compile_artifact(
                topic="Decision",
                body="# Current view\n\nThe decision remains open.",
                sources=[root / "0. Incoming/source.md"],
                root=root,
            )
            content = output.read_text(encoding="utf-8")
            self.assertIn("layer: compiled", content)
            self.assertIn("writer: knowledge-compiler", content)
            self.assertIn("`0. Incoming/source.md` — `sha256:", content)
            self.assertEqual(knowledge_compiler.verify_layers(root)["errors"], [])

    def test_stale_raw_hash_fails_verification(self):
        with self.make_root() as tmp:
            root = Path(tmp)
            knowledge_compiler.compile_artifact(
                topic="Decision",
                body="Current view.",
                sources=[root / "0. Incoming/source.md"],
                root=root,
            )
            (root / "0. Incoming/source.md").write_text("changed", encoding="utf-8")
            result = knowledge_compiler.verify_layers(root)
            self.assertFalse(result["ok"])
            self.assertIn("stale source hash", result["errors"][0])

    def test_compiler_rejects_compiled_source_as_evidence(self):
        with self.make_root() as tmp:
            root = Path(tmp)
            first = knowledge_compiler.compile_artifact(
                topic="First",
                body="Current view.",
                sources=[root / "0. Incoming/source.md"],
                root=root,
            )
            with self.assertRaisesRegex(ValueError, "Evidence must be raw"):
                knowledge_compiler.compile_artifact(
                    topic="Second",
                    body="Another view.",
                    sources=[first],
                    root=root,
                )

    def test_manifest_records_layer_writer_and_hash(self):
        with self.make_root() as tmp:
            root = Path(tmp)
            manifest = knowledge_compiler.build_manifest(root)
            source = manifest["files"][0]
            self.assertEqual(source["layer"], "raw")
            self.assertEqual(source["authorized_writer"], "source-capture")
            self.assertEqual(len(source["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
