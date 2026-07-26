"""Registry-derived manifest, routing, architecture, and compatibility tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from system.scripts import generate_registry_docs
from system.scripts import upgrade_compat
from system.utils import config
from system.utils.command_registry import build_command_catalog, load_command_registry


ROOT = Path(__file__).resolve().parents[2]


class TestRegistryDocs(unittest.TestCase):
    def test_release_version_surfaces_match(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        manifest = json.loads((ROOT / ".agent" / "MANIFEST.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["version"], version)
        self.assertEqual(upgrade_compat.TARGET_VERSION, version)
        self.assertEqual(config.DEFAULT_CONFIG["system"]["version"], version)
        self.assertEqual(config.DEFAULT_CONFIG["system"]["name"], "Beats PM Kit")
        self.assertEqual(config.DEFAULT_CONFIG["paths"]["scripts"], "system/scripts")
        self.assertEqual(config.DEFAULT_CONFIG["paths"]["utils"], "system/utils")

    def test_every_derived_surface_matches_the_registry_generator(self):
        generated = generate_registry_docs.generated_files(ROOT)
        for path, expected in generated.items():
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertTrue(path.is_file())
                self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_manifest_counts_match_canonical_files(self):
        manifest = json.loads((ROOT / ".agent" / "MANIFEST.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(manifest["agents"]["count"], len(list((ROOT / ".agent" / "agents").glob("*.md"))))
        self.assertEqual(manifest["workflows"]["count"], len(build_command_catalog(ROOT)))
        self.assertEqual(
            manifest["skills"]["count"],
            len(list((ROOT / ".agent" / "skills").glob("*/SKILL.md"))),
        )

    def test_compatibility_table_covers_registry_runtimes(self):
        registry = load_command_registry(ROOT)
        compatibility = (ROOT / "system" / "docs" / "runtime-compatibility.md").read_text(encoding="utf-8")

        for runtime in registry["runtime_policy"]["supported"]:
            self.assertIn(f"| {runtime.title()} |", compatibility)

    def test_stale_duplicate_routing_source_is_absent(self):
        self.assertFalse((ROOT / ".agent" / "rules" / "antigravity-rules-ROUTING.md").exists())


if __name__ == "__main__":
    unittest.main()
