#!/usr/bin/env python3
"""Create loss-aware workflow checkpoints only at completed phase boundaries."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASES = {"discovery", "planning", "creation", "verification"}
REQUIRED_FIELDS = {
    "goal",
    "decisions",
    "exact_stakeholder_language",
    "source_ids",
    "artifacts",
    "open_questions",
    "failed_attempts",
    "verification_state",
    "next_action",
    "recent_complete_turn",
    "tool_pairs_complete",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def should_checkpoint(
    *,
    context_percent: float,
    projected_next_phase_tokens: int,
    remaining_tokens: int,
    at_phase_boundary: bool,
) -> bool:
    if not at_phase_boundary:
        return False
    return context_percent >= 65 or projected_next_phase_tokens > remaining_tokens


def validate_payload(payload: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_FIELDS - payload.keys())
    if missing:
        raise ValueError("Missing checkpoint fields: " + ", ".join(missing))
    if payload["tool_pairs_complete"] is not True:
        raise ValueError("Checkpoint cannot split a tool-call/result pair")
    if not isinstance(payload["recent_complete_turn"], str) or not payload["recent_complete_turn"].strip():
        raise ValueError("The most recent complete turn must be preserved verbatim")


def create_checkpoint(
    payload: dict[str, Any],
    *,
    workflow: str,
    phase: str,
    context_percent: float,
    projected_next_phase_tokens: int,
    remaining_tokens: int,
    root: Path = ROOT,
) -> Path:
    if phase not in PHASES:
        raise ValueError(f"Unknown phase boundary: {phase}")
    validate_payload(payload)
    if not should_checkpoint(
        context_percent=context_percent,
        projected_next_phase_tokens=projected_next_phase_tokens,
        remaining_tokens=remaining_tokens,
        at_phase_boundary=True,
    ):
        raise ValueError("Checkpoint threshold not reached and the next phase fits")
    timestamp = utc_now()
    safe_workflow = re.sub(r"[^a-z0-9-]+", "-", workflow.lower()).strip("-") or "workflow"
    filename = timestamp.replace(":", "").replace("-", "") + f"-{safe_workflow}-{phase}.json"
    output = root / ".beats/context/checkpoints" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 1,
        "workflow": workflow,
        "completed_phase": phase,
        "created_at": timestamp,
        "trigger": {
            "context_percent": context_percent,
            "projected_next_phase_tokens": projected_next_phase_tokens,
            "remaining_tokens": remaining_tokens,
        },
        **payload,
    }
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--phase", choices=sorted(PHASES), required=True)
    parser.add_argument("--context-percent", type=float, required=True)
    parser.add_argument("--projected-next-phase-tokens", type=int, required=True)
    parser.add_argument("--remaining-tokens", type=int, required=True)
    parser.add_argument("--input", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        output = create_checkpoint(
            payload,
            workflow=args.workflow,
            phase=args.phase,
            context_percent=args.context_percent,
            projected_next_phase_tokens=args.projected_next_phase_tokens,
            remaining_tokens=args.remaining_tokens,
            root=args.root.resolve(),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"context-checkpoint: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
