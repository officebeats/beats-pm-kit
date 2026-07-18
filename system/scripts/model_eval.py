#!/usr/bin/env python3
"""Run sanitized deterministic or explicit local model evaluations."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = ROOT / "system" / "evals" / "scenarios.json"
EVAL_ROOT = Path(".beats/evals")
PRIVATE_PATH_RE = re.compile(
    r"(?:[A-Za-z]:\\(?:Users|Documents|OneDrive)\\|/(?:Users|home|private)/|\\\\[^\\]+\\)",
    re.IGNORECASE,
)
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+@-]{0,199}$")
RUNTIME_BINARIES = {
    "antigravity": "antigravity",
    "claude": "claude",
    "codex": "codex",
    "gemini": "gemini",
}

RUNTIME_AUTH_ENV = {
    "antigravity": ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"),
    "claude": (
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_BASE_URL",
    ),
    "codex": ("OPENAI_API_KEY", "OPENAI_BASE_URL"),
    "gemini": (
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
    ),
}


def load_scenarios(path: Path = SCENARIOS_PATH) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot load sanitized evaluation scenarios: {path}") from exc
    if payload.get("schema_version") != 1 or not isinstance(payload.get("scenarios"), list):
        raise ValueError("Unsupported evaluation scenario schema")
    scenarios = payload["scenarios"]
    validate_scenarios(scenarios)
    return scenarios


def validate_scenarios(scenarios: list[dict[str, Any]]) -> None:
    """Reject malformed fixtures and prompts that point at private workspaces."""
    required = {
        "id",
        "title",
        "profile",
        "prompt",
        "baseline_output",
        "expected_terms",
        "forbidden_terms",
    }
    identifiers: set[str] = set()
    for scenario in scenarios:
        missing = sorted(required - set(scenario))
        if missing:
            raise ValueError(f"Evaluation scenario is missing fields: {', '.join(missing)}")
        identifier = scenario["id"]
        if not isinstance(identifier, str) or identifier in identifiers:
            raise ValueError(f"Duplicate or invalid evaluation scenario ID: {identifier!r}")
        identifiers.add(identifier)
        for field in ("prompt", "baseline_output"):
            value = scenario[field]
            if not isinstance(value, str) or PRIVATE_PATH_RE.search(value):
                raise ValueError(
                    f"Scenario {identifier} contains a private or absolute path in {field}"
                )
        for field in ("expected_terms", "forbidden_terms"):
            values = scenario[field]
            if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                raise ValueError(f"Scenario {identifier} has invalid {field}")


def evaluate_output(scenario: dict[str, Any], output: str) -> dict[str, Any]:
    normalized = output.casefold()
    expected = scenario["expected_terms"]
    forbidden = scenario["forbidden_terms"]
    hits = [term for term in expected if term.casefold() in normalized]
    violations = [term for term in forbidden if term.casefold() in normalized]
    score = round(100.0 * len(hits) / len(expected), 2) if expected else 100.0
    return {
        "score": score,
        "hard_gates_passed": not violations,
        "expected_hits": hits,
        "missing_terms": [term for term in expected if term not in hits],
        "forbidden_hits": violations,
    }


def _aggregate(
    candidate: dict[str, str],
    scenarios: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    *,
    mode: str,
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        grouped[run["id"]].append(run)
    aggregated: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_runs = grouped[scenario["id"]]
        aggregated.append(
            {
                "id": scenario["id"],
                "title": scenario["title"],
                "profile": scenario["profile"],
                "score": round(
                    sum(item["score"] for item in scenario_runs) / len(scenario_runs), 2
                ),
                "latency_ms": round(
                    sum(item["latency_ms"] for item in scenario_runs) / len(scenario_runs), 2
                ),
                "hard_gates_passed": all(
                    item["hard_gates_passed"] for item in scenario_runs
                ),
                "runs": scenario_runs,
            }
        )
    quality = round(
        sum(item["score"] for item in aggregated) / len(aggregated), 2
    ) if aggregated else 0.0
    latency = round(
        sum(item["latency_ms"] for item in aggregated) / len(aggregated), 2
    ) if aggregated else 0.0
    return {
        "schema_version": 1,
        "mode": mode,
        "candidate": candidate,
        "scenario_schema": 1,
        "scenarios": aggregated,
        "summary": {
            "quality": quality,
            "mean_latency_ms": latency,
            "safety_gates_passed": all(
                item["hard_gates_passed"] for item in aggregated
            ),
            "scenario_count": len(aggregated),
            "repeat_count": max((len(item["runs"]) for item in aggregated), default=0),
        },
    }


def run_offline(*, scenarios: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = scenarios or load_scenarios()
    validate_scenarios(selected)
    runs: list[dict[str, Any]] = []
    for scenario in selected:
        evaluation = evaluate_output(scenario, scenario["baseline_output"])
        runs.append(
            {
                "id": scenario["id"],
                "iteration": 1,
                "latency_ms": 0.0,
                "output": scenario["baseline_output"],
                **evaluation,
            }
        )
    return _aggregate(
        {"runtime": "offline", "profile": "all", "model": "fixture-baseline"},
        selected,
        runs,
        mode="offline",
    )


def _validate_candidate(runtime: str, profile: str, model: str) -> None:
    if runtime not in RUNTIME_BINARIES:
        raise ValueError(f"Unsupported live evaluation runtime: {runtime}")
    if profile not in {"fast", "balanced", "deep", "all"}:
        raise ValueError(f"Unsupported evaluation profile: {profile}")
    if model != "inherit" and not SAFE_ID_RE.fullmatch(model):
        raise ValueError(f"Invalid model ID: {model!r}")


def runtime_runner(
    runtime: str, model: str, prompt: str, cwd: Path
) -> tuple[str, float]:
    """Run a provider CLI without a shell from an isolated sanitized directory."""
    binary = RUNTIME_BINARIES[runtime]
    executable = shutil.which(binary)
    if not executable:
        raise ValueError(f"{runtime} CLI is not available on PATH")
    guarded_prompt = (
        "This is a sanitized evaluation. Do not inspect files, environment variables, "
        "credentials, tools, or external services. Answer only from the prompt.\n\n" + prompt
    )
    if runtime == "codex":
        command = [
            executable,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "-c",
            "shell_environment_policy.inherit=none",
            "--color",
            "never",
        ]
        if model != "inherit":
            command.extend(["--model", model])
        command.append(guarded_prompt)
    elif runtime == "claude":
        command = [
            executable,
            "-p",
            guarded_prompt,
            "--output-format",
            "text",
            "--tools",
            "",
            "--safe-mode",
            "--no-session-persistence",
            "--strict-mcp-config",
        ]
        if model != "inherit":
            command.extend(["--model", model])
    elif runtime == "gemini":
        policy = cwd / "deny-all-tools.toml"
        policy.write_text(
            '[[rule]]\ntoolName = "*"\ndecision = "deny"\npriority = 1000000\n',
            encoding="utf-8",
        )
        command = [
            executable,
            "-p",
            guarded_prompt,
            "--output-format",
            "text",
            "--policy",
            str(policy),
        ]
        if model != "inherit":
            command.extend(["--model", model])
    else:
        command = [executable, "prompt", guarded_prompt]
        if model != "inherit":
            command.extend(["--model", model])
    environment = {
        key: value
        for key, value in os.environ.items()
        if key
        in {
            "PATH",
            "PATHEXT",
            "SYSTEMROOT",
            "WINDIR",
            "COMSPEC",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "HOME",
            "APPDATA",
            "LOCALAPPDATA",
            *RUNTIME_AUTH_ENV[runtime],
        }
    }
    environment["BEATS_EVAL_SANITIZED"] = "1"
    started = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Live {runtime} evaluation failed: {exc}") from exc
    latency_ms = (time.perf_counter() - started) * 1000
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise ValueError(
            f"Live {runtime} evaluation exited {result.returncode}: "
            f"{detail[0][:300] if detail else 'no diagnostic'}"
        )
    return result.stdout.strip(), latency_ms


def _eval_destination(root: Path, runtime: str, profile: str, model: str) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "-", model)[:80]
    destination = root / EVAL_ROOT / f"{stamp}-{runtime}-{profile}-{safe_model}.json"
    resolved_root = (root / EVAL_ROOT).resolve()
    if resolved_root != destination.resolve().parent:
        raise ValueError("Evaluation destination escaped .beats/evals")
    return destination


def _write_result(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_live(
    *,
    runtime: str,
    profile: str,
    model: str,
    allow_live: bool,
    repeats: int = 3,
    root: Path = ROOT,
    scenarios: list[dict[str, Any]] | None = None,
    runner: Callable[[str, str, str, Path], tuple[str, float]] = runtime_runner,
) -> dict[str, Any]:
    if not allow_live:
        raise ValueError("Live evaluation requires explicit --allow-live opt-in")
    if repeats != 3:
        raise ValueError("Live evaluations must run exactly three times per scenario")
    _validate_candidate(runtime, profile, model)
    all_scenarios = scenarios or load_scenarios()
    selected = [
        scenario
        for scenario in all_scenarios
        if profile == "all" or scenario["profile"] == profile
    ]
    if not selected:
        raise ValueError(f"No sanitized scenarios match profile: {profile}")
    validate_scenarios(selected)

    runs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="beats-model-eval-") as temporary:
        cwd = Path(temporary)
        for scenario in selected:
            for iteration in range(1, repeats + 1):
                output, latency_ms = runner(runtime, model, scenario["prompt"], cwd)
                evaluation = evaluate_output(scenario, output)
                runs.append(
                    {
                        "id": scenario["id"],
                        "iteration": iteration,
                        "latency_ms": round(latency_ms, 2),
                        "output": output,
                        **evaluation,
                    }
                )
    result = _aggregate(
        {"runtime": runtime, "profile": profile, "model": model},
        selected,
        runs,
        mode="live",
    )
    destination = _eval_destination(root, runtime, profile, model)
    result["created_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    result["privacy"] = {
        "fixtures_only": True,
        "private_workspace_inputs_included": False,
        "isolated_working_directory": True,
        "runtime_tools_disabled_or_denied": runtime in {"codex", "claude", "gemini"},
        "output_scope": EVAL_ROOT.as_posix(),
    }
    result["result_path"] = destination.relative_to(root).as_posix()
    _write_result(destination, result)
    return result


def _scenario_scores(run: dict[str, Any]) -> dict[str, float]:
    return {item["id"]: float(item["score"]) for item in run.get("scenarios", [])}


def _privacy_gates_passed(run: dict[str, Any]) -> bool:
    if run.get("mode") != "live":
        return True
    privacy = run.get("privacy", {})
    return bool(
        privacy.get("fixtures_only")
        and privacy.get("private_workspace_inputs_included") is False
        and privacy.get("isolated_working_directory")
        and privacy.get("runtime_tools_disabled_or_denied")
    )


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_scores = _scenario_scores(baseline)
    candidate_scores = _scenario_scores(candidate)
    if not baseline_scores or set(baseline_scores) != set(candidate_scores):
        raise ValueError("Baseline and candidate must contain the same scenarios")
    baseline_summary = baseline.get("summary", {})
    candidate_summary = candidate.get("summary", {})
    baseline_quality = float(baseline_summary.get("quality", 0.0))
    candidate_quality = float(candidate_summary.get("quality", 0.0))
    baseline_latency = float(baseline_summary.get("mean_latency_ms", 0.0))
    candidate_latency = float(candidate_summary.get("mean_latency_ms", 0.0))
    regressions = sorted(
        identifier
        for identifier, score in candidate_scores.items()
        if score + 1e-9 < baseline_scores[identifier]
    )
    candidate_repeats_passed = (
        candidate.get("mode") != "live"
        or candidate_summary.get("repeat_count") == 3
    )
    baseline_repeats_passed = (
        baseline.get("mode") != "live"
        or baseline_summary.get("repeat_count") == 3
    )
    repeated_runs_passed = candidate_repeats_passed and baseline_repeats_passed
    privacy_gates_passed = _privacy_gates_passed(baseline) and _privacy_gates_passed(
        candidate
    )
    safety = (
        repeated_runs_passed
        and privacy_gates_passed
        and bool(candidate_summary.get("safety_gates_passed"))
        and all(item.get("hard_gates_passed") for item in candidate.get("scenarios", []))
    )
    quality_gain = round(candidate_quality - baseline_quality, 2)
    latency_gain = (
        round(100.0 * (baseline_latency - candidate_latency) / baseline_latency, 2)
        if baseline_latency > 0
        else 0.0
    )
    quality_path = safety and quality_gain >= 2.0 and not regressions
    latency_path = (
        safety
        and latency_gain >= 20.0
        and candidate_quality >= baseline_quality - 1.0
        and not regressions
    )
    recommended = quality_path or latency_path
    reason = "quality" if quality_path else "latency" if latency_path else "rejected"
    return {
        "schema_version": 1,
        "candidate": candidate.get("candidate", {}),
        "baseline": baseline.get("candidate", {}),
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
        "comparison": {
            "recommended": recommended,
            "reason": reason,
            "safety_gates_passed": safety,
            "repeated_runs_passed": repeated_runs_passed,
            "privacy_gates_passed": privacy_gates_passed,
            "quality_gain_points": quality_gain,
            "latency_improvement_percent": latency_gain,
            "scenario_regressions": regressions,
            "thresholds": {
                "quality_gain_points": 2.0,
                "latency_improvement_percent": 20.0,
                "latency_path_quality_tolerance_points": 1.0,
            },
        },
    }


def _load_run(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read evaluation result: {path}") from exc


def _public_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": result.get("mode"),
        "candidate": result.get("candidate"),
        "summary": result.get("summary"),
        "result_path": result.get("result_path"),
        "privacy": result.get("privacy"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="action", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--mode", choices=["offline", "live"], required=True)
    run_parser.add_argument("--runtime", choices=sorted(RUNTIME_BINARIES))
    run_parser.add_argument("--profile", choices=["fast", "balanced", "deep", "all"], default="all")
    run_parser.add_argument("--model", default="inherit")
    run_parser.add_argument("--allow-live", action="store_true")
    run_parser.add_argument("--repeats", type=int, default=3)
    run_parser.add_argument("--json", action="store_true")

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--baseline", type=Path, required=True)
    compare_parser.add_argument("--candidate", type=Path, required=True)
    compare_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.action == "run":
            if args.mode == "offline":
                result = run_offline()
                public = result
            else:
                if not args.runtime:
                    raise ValueError("--runtime is required for live evaluation")
                result = run_live(
                    runtime=args.runtime,
                    profile=args.profile,
                    model=args.model,
                    allow_live=args.allow_live,
                    repeats=args.repeats,
                    root=args.root.resolve(),
                )
                public = _public_summary(result)
        else:
            result = compare_runs(_load_run(args.baseline), _load_run(args.candidate))
            public = result
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(public, indent=2, sort_keys=True))
    else:
        summary = public.get("summary") or public.get("comparison")
        print(json.dumps(summary, indent=2, sort_keys=True))
        if public.get("result_path"):
            print(f"Stored private evaluation output: {public['result_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
