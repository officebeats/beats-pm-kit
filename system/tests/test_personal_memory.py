"""Regression tests for the optional local personal-memory companion."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "system" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import agent_memory_health
import personal_memory
import upgrade_compat


class TestPersonalMemory(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "system" / "scripts").mkdir(parents=True)
        (root / "system" / "scripts" / "agentic_memory.py").write_text(
            "# local memory engine\n", encoding="utf-8"
        )
        return root

    def enable(
        self,
        root: Path,
        *,
        capture_enabled: bool = False,
        store: str | None = None,
    ) -> dict:
        return personal_memory.configure(
            root=root,
            enabled=True,
            capture_enabled=capture_enabled,
            binary="iai-test",
            store=store,
        )

    def test_default_is_disabled_and_never_probes_an_external_binary(self):
        root = self.make_root()
        runner = mock.Mock()

        result = personal_memory.status(root=root, runner=runner)

        self.assertEqual(result["status"], "disabled")
        self.assertFalse(result["enabled"])
        self.assertFalse(result["capture_enabled"])
        self.assertEqual(result["fallback"], "rg")
        runner.assert_not_called()

    def test_configure_is_local_opt_in_and_backs_up_existing_choices(self):
        root = self.make_root()

        first = self.enable(root, store=str(root / "private-memory"))
        second = personal_memory.configure(
            root=root,
            enabled=True,
            capture_enabled=True,
            binary="iai-test",
            store=str(root / "private-memory"),
        )

        config_path = root / ".beats" / "personal-memory.json"
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(first["status"], "configured")
        self.assertIsNone(first["backup"])
        self.assertTrue(second["capture_enabled"])
        self.assertIsNotNone(second["backup"])
        self.assertTrue((root / second["backup"]).is_file())
        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["enabled"])
        self.assertTrue(payload["capture_enabled"])

    def test_cli_capture_opt_in_preserves_existing_store_and_binary(self):
        root = self.make_root()
        store = str(root / "private-memory")
        self.enable(root, store=store)

        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = personal_memory.main(
                [
                    "--root",
                    str(root),
                    "configure",
                    "--enable",
                    "--enable-capture",
                    "--json",
                ]
            )

        payload = personal_memory.load_config(root)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["store"], store)
        self.assertEqual(payload["binary"], "iai-test")
        self.assertTrue(payload["capture_enabled"])

    def test_recall_is_fail_open_when_disabled(self):
        root = self.make_root()
        runner = mock.Mock()

        result = personal_memory.recall(
            "what did we decide about launch?",
            root=root,
            runner=runner,
        )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["fallback"], "rg")
        runner.assert_not_called()

    def test_recall_uses_json_argv_and_marks_results_untrusted(self):
        root = self.make_root()
        store = root / "private-memory"
        self.enable(root, store=str(store))
        runner = mock.Mock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(
                    {
                        "hits": [
                            {
                                "id": "memory-1",
                                "literal_surface": "Launch moved to Friday.",
                                "score": 0.91,
                                "captured_at": "2026-07-20T14:00:00Z",
                            }
                        ],
                        "_source": "direct-store",
                        "count": 1,
                    }
                ),
                stderr="",
            )
        )

        with (
            mock.patch.object(personal_memory.shutil, "which", return_value="iai-test"),
            mock.patch.dict(
                personal_memory.os.environ,
                {"OPENAI_API_KEY": "must-not-reach-companion"},
            ),
        ):
            result = personal_memory.recall(
                "launch decision",
                root=root,
                limit=3,
                runner=runner,
            )

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["treat_as_untrusted"])
        self.assertEqual(result["hits"][0]["content"], "Launch moved to Friday.")
        self.assertEqual(result["hits"][0]["record_id"], "memory-1")
        command = runner.call_args.args[0]
        self.assertEqual(
            command,
            ["iai-test", "recall", "--json", "--limit", "3", "launch decision"],
        )
        call_kwargs = runner.call_args.kwargs
        self.assertEqual(call_kwargs["env"]["IAI_MCP_STORE"], str(store.resolve()))
        self.assertFalse(
            any(key.endswith("API_KEY") for key in call_kwargs["env"])
        )
        self.assertLessEqual(call_kwargs["timeout"], 15.0)

    def test_recall_timeout_degrades_without_exposing_private_input(self):
        root = self.make_root()
        self.enable(root)
        runner = mock.Mock(side_effect=subprocess.TimeoutExpired(["iai-test"], 8))

        with mock.patch.object(personal_memory.shutil, "which", return_value="iai-test"):
            result = personal_memory.recall(
                "sensitive customer decision",
                root=root,
                runner=runner,
            )

        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["fallback"], "rg")
        self.assertEqual(result["error"], "timeout")
        self.assertNotIn("sensitive customer decision", json.dumps(result))

    def test_recall_rejects_bulk_cues_before_running_the_companion(self):
        root = self.make_root()
        self.enable(root)
        runner = mock.Mock()

        result = personal_memory.recall(
            "x" * (personal_memory.MAX_CUE_CHARS + 1),
            root=root,
            runner=runner,
        )

        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["error"], "cue_too_large")
        runner.assert_not_called()

    def test_capture_requires_separate_explicit_opt_in(self):
        root = self.make_root()
        self.enable(root, capture_enabled=False)
        runner = mock.Mock()

        result = personal_memory.capture(
            "Decision: ship Friday.",
            root=root,
            runner=runner,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "capture_not_enabled")
        runner.assert_not_called()

    def test_capture_rejects_bulk_content_before_running_the_companion(self):
        root = self.make_root()
        self.enable(root, capture_enabled=True)
        runner = mock.Mock()

        result = personal_memory.capture(
            "x" * (personal_memory.MAX_CAPTURE_CHARS + 1),
            root=root,
            runner=runner,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "memory_too_large")
        runner.assert_not_called()

    def test_capture_uses_only_the_local_cli_when_enabled(self):
        root = self.make_root()
        self.enable(root, capture_enabled=True)
        runner = mock.Mock(
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout='{"id":"memory-2","status":"inserted","_source":"daemon"}',
                stderr="",
            )
        )

        with mock.patch.object(personal_memory.shutil, "which", return_value="iai-test"):
            result = personal_memory.capture(
                "Decision: ship Friday.",
                root=root,
                session_id="beats-project-alpha",
                runner=runner,
            )

        self.assertEqual(result["status"], "inserted")
        self.assertEqual(result["record_id"], "memory-2")
        self.assertEqual(
            runner.call_args.args[0],
            [
                "iai-test",
                "capture",
                "--json",
                "--session-id",
                "beats-project-alpha",
                "Decision: ship Friday.",
            ],
        )

    def test_health_reads_the_actual_local_graph_path_and_companion_state(self):
        root = self.make_root()
        graph = root / ".beats" / "memory" / "symbolic_graph.mermaid"
        graph.parent.mkdir(parents=True)
        graph.write_text("graph TD\n", encoding="utf-8")

        result = agent_memory_health.health_status(root)

        self.assertTrue(result.available)
        self.assertEqual(Path(result.graph_path), graph)
        self.assertEqual(result.companion["status"], "disabled")

    def test_upgrade_blocks_an_invalid_local_companion_config(self):
        root = self.make_root()
        config = root / ".beats" / "personal-memory.json"
        config.parent.mkdir(parents=True)
        config.write_text('{"schema_version": 99}', encoding="utf-8")

        report = upgrade_compat.inspect(root)

        self.assertTrue(
            any(
                finding.code == "invalid-personal-memory-config"
                for finding in report.blockers
            )
        )


if __name__ == "__main__":
    unittest.main()
