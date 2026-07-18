import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from system.scripts import pack_manager


class TestPackManager(unittest.TestCase):
    def make_root(self) -> Path:
        root = Path(tempfile.mkdtemp())
        pack = root / "packs" / "trello"
        pack.mkdir(parents=True)
        (pack / "PACK.md").write_text("# Trello Task Board Pack\n", encoding="utf-8")
        (pack / "pack.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "id": "trello",
                    "title": "Trello Task Board",
                    "description": "Optional board sync.",
                    "version": "1.0.0",
                    "entrypoint": "PACK.md",
                    "runner": "system/scripts/trello_bridge.py",
                }
            ),
            encoding="utf-8",
        )
        script = root / "system" / "scripts" / "trello_bridge.py"
        script.parent.mkdir(parents=True)
        script.write_text("print('ok')\n", encoding="utf-8")
        return root

    def test_packs_are_disabled_by_default_and_enable_locally(self):
        root = self.make_root()

        self.assertFalse(pack_manager.pack_rows(root)[0]["enabled"])
        result = pack_manager.set_enabled(root, "trello", True)

        self.assertTrue(pack_manager.pack_rows(root)[0]["enabled"])
        self.assertEqual(result["config"], ".beats/packs.json")
        self.assertEqual(json.loads((root / ".beats" / "packs.json").read_text(encoding="utf-8"))["enabled"], ["trello"])

    def test_disabled_pack_cannot_run(self):
        root = self.make_root()

        with self.assertRaisesRegex(ValueError, "disabled"):
            pack_manager.run_pack(root, "trello", ["status"])

    @mock.patch("system.scripts.pack_manager.subprocess.run")
    def test_enabled_pack_runs_repo_contained_script(self, run):
        root = self.make_root()
        run.return_value.returncode = 0
        pack_manager.set_enabled(root, "trello", True)

        code = pack_manager.run_pack(root, "trello", ["status"])

        self.assertEqual(code, 0)
        command = run.call_args.args[0]
        self.assertEqual(command[-1], "status")
        self.assertEqual(run.call_args.kwargs["cwd"], root)


if __name__ == "__main__":
    unittest.main()
