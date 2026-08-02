"""Deterministic and opt-in live model evaluation tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from system.scripts import model_eval


class TestModelEval(unittest.TestCase):
    def test_offline_suite_covers_all_safety_scenarios(self):
        result = model_eval.run_offline()

        self.assertTrue(
            {
                "evidence-retrieval",
                "cross-source-conflict",
                "duplicate-task-prevention",
                "meeting-synthesis",
                "task-fidelity",
                "prompt-injection",
                "missing-source-handling",
                "legacy-migration",
            }.issubset({item["id"] for item in result["scenarios"]})
        )
        self.assertGreaterEqual(result["summary"]["scenario_count"], 15)
        self.assertTrue(result["summary"]["safety_gates_passed"])
        self.assertEqual(result["summary"]["quality"], 100.0)

    def test_live_mode_requires_explicit_opt_in(self):
        with self.assertRaisesRegex(ValueError, "--allow-live"):
            model_eval.run_live(
                runtime="codex", profile="fast", model="inherit", allow_live=False
            )

    def test_live_runs_three_times_and_writes_only_under_ignored_eval_root(self):
        root = Path(tempfile.mkdtemp())
        calls: list[tuple[str, Path]] = []

        def runner(runtime: str, model: str, prompt: str, cwd: Path) -> tuple[str, float]:
            calls.append((prompt, cwd))
            return "Decision: the launch is postponed. [meeting-1] [slack-2]", 10.0

        result = model_eval.run_live(
            runtime="codex",
            profile="fast",
            model="candidate",
            allow_live=True,
            repeats=3,
            root=root,
            scenarios=[model_eval.load_scenarios()[0]],
            runner=runner,
        )

        self.assertEqual(len(calls), 3)
        self.assertTrue(all(root not in cwd.parents and cwd != root for _, cwd in calls))
        output = root / result["result_path"]
        self.assertTrue(output.is_file())
        self.assertEqual(output.relative_to(root).parts[:2], (".beats", "evals"))

    def test_private_workspace_path_in_scenario_is_rejected(self):
        scenario = dict(model_eval.load_scenarios()[0])
        scenario["prompt"] = "Read C:\\Users\\person\\Private\\meeting.md"

        with self.assertRaisesRegex(ValueError, "private or absolute path"):
            model_eval.validate_scenarios([scenario])

    def test_codex_live_runner_disables_rules_sessions_and_shell_environment(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            model_eval.shutil, "which", return_value="C:/bin/codex.exe"
        ), mock.patch.object(model_eval.subprocess, "run") as run, mock.patch.dict(
            model_eval.os.environ,
            {"PATH": "C:/bin", "UNRELATED_PRIVATE_TOKEN": "must-not-pass"},
            clear=True,
        ):
            run.return_value = SimpleNamespace(returncode=0, stdout="answer", stderr="")

            model_eval.runtime_runner("codex", "inherit", "fixture", Path(temporary))

        command = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("shell_environment_policy.inherit=none", command)
        self.assertNotIn("UNRELATED_PRIVATE_TOKEN", environment)

    def test_gemini_live_runner_supplies_a_deny_all_tools_policy(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            model_eval.shutil, "which", return_value="C:/bin/gemini.exe"
        ), mock.patch.object(model_eval.subprocess, "run") as run:
            run.return_value = SimpleNamespace(returncode=0, stdout="answer", stderr="")

            model_eval.runtime_runner("gemini", "inherit", "fixture", Path(temporary))

            command = run.call_args.args[0]
            policy = Path(command[command.index("--policy") + 1])
            self.assertIn('toolName = "*"', policy.read_text(encoding="utf-8"))
            self.assertIn('decision = "deny"', policy.read_text(encoding="utf-8"))

    def test_quality_gain_requires_no_scenario_regression(self):
        baseline = self.make_run({"one": 80.0, "two": 80.0}, latency=100.0)
        candidate = self.make_run({"one": 82.0, "two": 82.0}, latency=100.0)

        comparison = model_eval.compare_runs(baseline, candidate)

        self.assertTrue(comparison["comparison"]["recommended"])
        self.assertEqual(comparison["comparison"]["reason"], "quality")

        candidate = self.make_run({"one": 90.0, "two": 79.0}, latency=100.0)
        comparison = model_eval.compare_runs(baseline, candidate)
        self.assertFalse(comparison["comparison"]["recommended"])
        self.assertIn("two", comparison["comparison"]["scenario_regressions"])

    def test_latency_gain_can_recommend_without_quality_regression(self):
        baseline = self.make_run({"one": 90.0, "two": 90.0}, latency=100.0)
        candidate = self.make_run({"one": 90.0, "two": 90.0}, latency=79.0)

        comparison = model_eval.compare_runs(baseline, candidate)

        self.assertTrue(comparison["comparison"]["recommended"])
        self.assertEqual(comparison["comparison"]["reason"], "latency")

    def test_latency_gain_rejects_any_scenario_regression(self):
        baseline = self.make_run({"one": 90.0, "two": 90.0}, latency=100.0)
        candidate = self.make_run({"one": 89.0, "two": 90.0}, latency=70.0)

        comparison = model_eval.compare_runs(baseline, candidate)

        self.assertFalse(comparison["comparison"]["recommended"])
        self.assertEqual(comparison["comparison"]["scenario_regressions"], ["one"])

    def test_live_candidate_without_three_repeats_fails_safety_gate(self):
        baseline = self.make_run({"one": 80.0}, latency=100.0)
        candidate = self.make_run({"one": 90.0}, latency=70.0)
        candidate["mode"] = "live"
        candidate["summary"]["repeat_count"] = 2

        comparison = model_eval.compare_runs(baseline, candidate)

        self.assertFalse(comparison["comparison"]["recommended"])
        self.assertFalse(comparison["comparison"]["repeated_runs_passed"])

    def test_live_candidate_without_proven_privacy_controls_fails_safety_gate(self):
        baseline = self.make_run({"one": 80.0}, latency=100.0)
        candidate = self.make_run({"one": 90.0}, latency=70.0)
        for run in (baseline, candidate):
            run["mode"] = "live"
            run["summary"]["repeat_count"] = 3
            run["privacy"] = {
                "fixtures_only": True,
                "private_workspace_inputs_included": False,
                "isolated_working_directory": True,
                "runtime_tools_disabled_or_denied": False,
            }

        comparison = model_eval.compare_runs(baseline, candidate)

        self.assertFalse(comparison["comparison"]["recommended"])
        self.assertFalse(comparison["comparison"]["privacy_gates_passed"])

    @staticmethod
    def make_run(scores: dict[str, float], *, latency: float) -> dict:
        return {
            "candidate": {"runtime": "codex", "profile": "fast", "model": "candidate"},
            "scenarios": [
                {
                    "id": scenario_id,
                    "score": score,
                    "latency_ms": latency,
                    "hard_gates_passed": True,
                }
                for scenario_id, score in scores.items()
            ],
            "summary": {
                "quality": sum(scores.values()) / len(scores),
                "mean_latency_ms": latency,
                "safety_gates_passed": True,
            },
        }


if __name__ == "__main__":
    unittest.main()
