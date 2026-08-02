"""Tests for the local context router."""

from __future__ import annotations

import tempfile
import time
import sys
import unittest
from pathlib import Path


SYSTEM_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SYSTEM_DIR))

from scripts import context_router


class TestContextRouter(unittest.TestCase):
    def make_root(self) -> tempfile.TemporaryDirectory:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "5. Trackers" / "tasks").mkdir(parents=True)
        (root / "3. Meetings" / "reports" / "day").mkdir(parents=True)
        (root / "6. Resources" / "planning").mkdir(parents=True)
        (root / "5. Trackers" / "tasks" / "PARU-009.md").write_text(
            "# White-Labelled Developer Portal Research\n\n"
            "Developer portal pricing, DRI, implementor, and build-vs-buy evidence.\n",
            encoding="utf-8",
        )
        (root / "3. Meetings" / "reports" / "day" / "2026-05-26-task-triage.md").write_text(
            "# Daily Triage\n\nDeveloper portal remains open and needs pricing confirmation.\n",
            encoding="utf-8",
        )
        (root / "6. Resources" / "planning" / "calculator-scope.md").write_text(
            "# Calculator Scope\n\nCURB-65 and PSI are likely first-slice calculators.\n",
            encoding="utf-8",
        )
        return tmp

    def test_build_index_covers_supported_local_sources(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"

            index = context_router.build_index(root, force=True, index_path=index_path)

            paths = {item["path"] for item in index["files"]}
            self.assertIn("5. Trackers/tasks/PARU-009.md", paths)
            self.assertIn("3. Meetings/reports/day/2026-05-26-task-triage.md", paths)
            self.assertIn("6. Resources/planning/calculator-scope.md", paths)
            self.assertTrue(index_path.exists())
            self.assertEqual(index["schema_version"], 2)
            task = next(item for item in index["files"] if item["path"].endswith("PARU-009.md"))
            for field in ["authority", "freshness", "topic", "source_type", "stakeholder", "workflow"]:
                self.assertIn(field, task)

    def test_query_returns_context_packet_with_confidence_and_suggestions(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"

            result = context_router.query_index(
                "developer portal pricing",
                root=root,
                index_path=index_path,
            )

            self.assertEqual(result["query"], "developer portal pricing")
            self.assertGreater(result["matches"][0]["confidence"], 0)
            self.assertEqual(result["matches"][0]["path"], "5. Trackers/tasks/PARU-009.md")
            self.assertIn("/find", result["suggested_commands"])
            self.assertEqual(result["search_mode"], "fts5")
            self.assertEqual(result["retrieval_policy"]["maximum_initial_sources"], 5)
            self.assertEqual(result["retrieval_policy"]["maximum_reference_hops"], 1)
            self.assertTrue(result["retrieval_policy"]["compiled_sources_are_navigation_only"])

    def test_initial_retrieval_is_capped_at_five_sources(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"
            with self.assertRaisesRegex(ValueError, "between 1 and 5"):
                context_router.query_index("developer portal", root=root, limit=6, index_path=index_path)

    def test_find_retrieves_evidence_buried_late_in_a_transcript(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            transcript = root / "3. Meetings" / "transcripts" / "2026-07-18-product-council.md"
            transcript.parent.mkdir(parents=True, exist_ok=True)
            filler = "General roadmap discussion.\n" * 120
            transcript.write_text(
                "---\ntitle: Product Council — July 18, 2026\n---\n\n# Product Council — July 18, 2026\n\n"
                + filler
                + "The explicit decision was to delay the search beta until telemetry is ready.\n",
                encoding="utf-8",
            )
            index_path = root / "system" / "cache" / "context-router" / "index.json"

            result = context_router.query_index("delay search beta telemetry", root=root, index_path=index_path)

            self.assertEqual(result["matches"][0]["path"], "3. Meetings/transcripts/2026-07-18-product-council.md")
            self.assertIn("delay", result["matches"][0]["snippet"].lower())
            self.assertGreater(result["matches"][0]["line"], 100)

    def test_cache_invalidates_when_file_changes(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"
            first = context_router.build_index(root, force=True, index_path=index_path)
            task_path = root / "5. Trackers" / "tasks" / "PARU-009.md"
            old_hash = next(item["sha256"] for item in first["files"] if item["path"].endswith("PARU-009.md"))

            time.sleep(0.01)
            task_path.write_text(task_path.read_text(encoding="utf-8") + "\nNew pricing source added.\n", encoding="utf-8")
            second = context_router.build_index(root, index_path=index_path)
            new_hash = next(item["sha256"] for item in second["files"] if item["path"].endswith("PARU-009.md"))

            self.assertNotEqual(old_hash, new_hash)

    def test_write_wiki_uses_ignored_cache_shape(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"
            index = context_router.build_index(root, force=True, index_path=index_path)

            wiki_path = context_router.write_wiki(index, root=root, wiki_dir=index_path.parent / "wiki")

            self.assertEqual(wiki_path.relative_to(root).as_posix(), "system/cache/context-router/wiki/index.md")
            self.assertIn("PARU-009.md", wiki_path.read_text(encoding="utf-8"))

    def test_warm_lookup_is_under_one_second(self):
        with self.make_root() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "system" / "cache" / "context-router" / "index.json"
            context_router.build_index(root, force=True, index_path=index_path)

            start = time.perf_counter()
            context_router.query_index("calculator scope", root=root, index_path=index_path)
            elapsed = time.perf_counter() - start

            self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
