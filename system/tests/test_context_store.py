"""Tests for deterministic loss-aware context storage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from system.scripts import context_store


class TestContextStore(unittest.TestCase):
    def test_archive_is_content_addressed_and_retrievable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = b"alpha\nWARNING: keep this\n3 tests passed\nomega\n"
            first = context_store.archive_bytes(
                payload,
                root=root,
                source="test-output",
                producing_command="python -m unittest",
            )
            second = context_store.archive_bytes(
                payload,
                root=root,
                source="same-content",
                producing_command="rerun",
            )

            self.assertEqual(first["id"], second["id"])
            self.assertEqual(context_store.retrieve_bytes(first["id"], root=root), payload)
            self.assertEqual(len(list((root / ".beats/context/raw").glob("*.blob"))), 1)
            record = context_store.load_record(first["id"], root=root)
            self.assertEqual(len(record["captures"]), 2)

    def test_compact_view_preserves_signals_and_retrieval_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lines = [f"routine line {number}" for number in range(80)]
            lines[40] = "ERROR system/scripts/example.py:42 failed"
            record = context_store.archive_bytes(
                "\n".join(lines).encode(),
                root=root,
                source="tool",
                producing_command="example",
            )

            view = context_store.compact_view(record["id"], root=root, max_chars=700)

            self.assertTrue(view["truncated"])
            self.assertIn("ERROR system/scripts/example.py:42 failed", [item["text"] for item in view["signals"]])
            self.assertIn(record["id"], view["retrieval"])
            self.assertEqual(view["sha256"], record["sha256"])

    def test_retrieve_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = context_store.archive_bytes(
                b"authoritative",
                root=root,
                source="quote",
                producing_command="capture",
            )
            raw_path = root / record["raw_path"]
            raw_path.write_bytes(b"changed")

            with self.assertRaisesRegex(ValueError, "Hash mismatch"):
                context_store.retrieve_bytes(record["id"], root=root)


if __name__ == "__main__":
    unittest.main()
