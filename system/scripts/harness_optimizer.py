#!/usr/bin/env python3
"""Evaluate one bounded harness change against held-out paired scenarios."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEDGER_REL = Path(".beats/harness/optimizer-ledger.jsonl")
ALLOWED_SURFACES = {
    "routing_description",
    "context_selection",
    "top_k",
    "response_profile",
    "deterministic_output_filter",
    "checkpoint_threshold",
    "prompt_wording",
    "prompt_ordering",
}
PROTECTED_SURFACES = {
    "quality_rubric",
    "permissions",
    "source_requirements",
    "workflow_intent",
    "evaluation_fixtures",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def scenario_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Evaluation payload requires scenarios")
    mapped = {str(item["id"]): item for item in scenarios}
    if len(mapped) != len(scenarios):
        raise ValueError("Scenario IDs must be unique")
    return mapped


def quality_regressions(baseline: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for score in ["functionality_score", "intent_score"]:
        if float(candidate.get(score, -1)) < float(baseline.get(score, -1)):
            failures.append(f"{score} regressed")
    if float(candidate.get("source_citation_recall", 0)) < 1.0:
        failures.append("source and citation recall is below 100%")
    for field in ["exact_wording_preserved", "approval_privacy_unchanged", "artifact_compatible"]:
        if candidate.get(field) is not True:
            failures.append(field + " failed")
    return failures


def evaluate_experiment(
    experiment: dict[str, Any],
    baseline_payload: dict[str, Any],
    candidate_payload: dict[str, Any],
) -> dict[str, Any]:
    change = experiment.get("change")
    if not isinstance(change, dict) or set(change) != {"surface", "before", "after"}:
        raise ValueError("Experiment must contain exactly one before/after change and surface")
    surface = str(change["surface"])
    if surface in PROTECTED_SURFACES or surface not in ALLOWED_SURFACES:
        raise ValueError(f"Optimizer may not change {surface}")
    if experiment.get("held_out") is not True:
        raise ValueError("Held-out evaluation is required")
    baseline = scenario_map(baseline_payload)
    candidate = scenario_map(candidate_payload)
    if set(baseline) != set(candidate):
        raise ValueError("Baseline and candidate scenario sets must match")

    scenario_results = []
    all_quality_ok = True
    max_token_regression_ok = True
    for scenario_id in sorted(baseline):
        base = baseline[scenario_id]
        cand = candidate[scenario_id]
        if base.get("pairing") != cand.get("pairing"):
            raise ValueError(f"Scenario pairing metadata differs: {scenario_id}")
        failures = quality_regressions(base, cand)
        if failures:
            all_quality_ok = False
        token_change = (float(cand["total_processed_tokens"]) - float(base["total_processed_tokens"])) / max(
            float(base["total_processed_tokens"]), 1
        )
        if token_change > 0.05:
            max_token_regression_ok = False
            failures.append(f"token regression {token_change:.1%} exceeds 5%")
        scenario_results.append(
            {
                "id": scenario_id,
                "passed": not failures,
                "failures": failures,
                "token_change_percent": round(token_change * 100, 3),
            }
        )

    baseline_tokens = [float(item["total_processed_tokens"]) for item in baseline.values()]
    candidate_tokens = [float(item["total_processed_tokens"]) for item in candidate.values()]
    median_reduction = 1 - statistics.median(candidate_tokens) / max(statistics.median(baseline_tokens), 1)
    baseline_turns = statistics.median(float(item["turns"]) for item in baseline.values())
    candidate_turns = statistics.median(float(item["turns"]) for item in candidate.values())
    required_reduction = 0.10 if experiment.get("optional_compression_component") else 0.25
    gates = {
        "per_scenario_quality": all_quality_ok,
        "median_token_reduction": median_reduction >= required_reduction,
        "per_scenario_token_regression": max_token_regression_ok,
        "median_turn_increase": candidate_turns <= baseline_turns + 1,
    }
    passed = all(gates.values())
    return {
        "schema_version": 1,
        "experiment_id": experiment.get("id"),
        "evaluated_at": utc_now(),
        "change": change,
        "held_out": True,
        "human_approval_required": True,
        "automatic_promotion": False,
        "passed": passed,
        "gates": gates,
        "median_token_reduction_percent": round(median_reduction * 100, 3),
        "median_turn_change": candidate_turns - baseline_turns,
        "scenarios": scenario_results,
    }


def append_ledger(result: dict[str, Any], *, root: Path = ROOT, ledger: Path | None = None) -> Path:
    destination = ledger or root / LEDGER_REL
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, separators=(",", ":"), sort_keys=True) + "\n")
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = evaluate_experiment(
            json.loads(args.experiment.read_text(encoding="utf-8")),
            json.loads(args.baseline.read_text(encoding="utf-8")),
            json.loads(args.candidate.read_text(encoding="utf-8")),
        )
        append_ledger(result, root=args.root.resolve(), ledger=args.ledger)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"harness-optimizer: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
