#!/usr/bin/env python3
"""Create loss-aware workflow checkpoints only at completed phase boundaries.

Checkpoints are append-only and anchored: each one writes a new JSON file and
appends a `## Checkpoint <ISO8601>` section to `ANCHORS.md` in the checkpoint
directory. Earlier anchors are never rewritten or reordered; every section
carries a content hash and any mutation raises before a new checkpoint writes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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
CHECKPOINT_DIRNAME = ".beats/context/checkpoints"
ANCHORS_FILENAME = "ANCHORS.md"
ANCHORS_HEADER = (
    "# Checkpoint Anchors\n"
    "\n"
    "> Append-only ledger. Each checkpoint appends one `## Checkpoint <ISO8601>` section.\n"
    "> Existing sections are never rewritten or reordered; every section carries a content\n"
    "> hash and any mutation fails the next checkpoint.\n"
)
ANCHOR_HASH_RE = re.compile(r"^<!-- anchor-hash: ([0-9a-f]{64}) -->$")
ANCHOR_HEADING_PREFIX = "## Checkpoint "


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _anchor_digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def parse_anchors(text: str) -> list[dict[str, str]]:
    """Parse anchor sections into {heading, body, recorded_hash} dicts.

    Raises ValueError when a section has no hash line or carries content
    after its hash line (both indicate a hand edit).
    """
    sections: list[list[str]] = []
    current: list[str] | None = None
    for line in text.split("\n"):
        if line.startswith(ANCHOR_HEADING_PREFIX):
            if current is not None:
                sections.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        sections.append(current)

    anchors: list[dict[str, str]] = []
    for lines in sections:
        hash_index = None
        recorded = None
        for index, line in enumerate(lines):
            match = ANCHOR_HASH_RE.match(line)
            if match:
                hash_index = index
                recorded = match.group(1)
                break
        if hash_index is None or recorded is None:
            raise ValueError(f"Anchor section without a hash line: {lines[0]!r}")
        if any(line.strip() for line in lines[hash_index + 1 :]):
            raise ValueError(f"Content added after the hash line of {lines[0]!r}")
        anchors.append(
            {
                "heading": lines[0],
                "body": "\n".join(lines[:hash_index]),
                "recorded_hash": recorded,
            }
        )
    return anchors


def verify_anchors(anchors_path: Path) -> int:
    """Guard: raise ValueError if any existing anchor's content hash changed.

    Returns the number of verified anchors (0 when the ledger does not exist).
    """
    if not anchors_path.exists():
        return 0
    anchors = parse_anchors(anchors_path.read_text(encoding="utf-8"))
    for anchor in anchors:
        actual = _anchor_digest(anchor["body"])
        if actual != anchor["recorded_hash"]:
            raise ValueError(
                "Append-only violation: content hash changed for "
                f"{anchor['heading']!r} (checkpoint anchors are never rewritten)"
            )
    return len(anchors)


def append_anchor(
    checkpoint_dir: Path,
    *,
    timestamp: str,
    workflow: str,
    phase: str,
    checkpoint_file: str,
    document_sha256: str,
) -> Path:
    """Append one anchored `## Checkpoint <ISO8601>` section to the ledger.

    Verifies all existing anchors first and appends in 'a' mode, so earlier
    sections are never rewritten or reordered.
    """
    anchors_path = checkpoint_dir / ANCHORS_FILENAME
    verify_anchors(anchors_path)
    body = "\n".join(
        [
            f"{ANCHOR_HEADING_PREFIX}{timestamp}",
            "",
            f"- workflow: {workflow}",
            f"- completed_phase: {phase}",
            f"- checkpoint_file: {checkpoint_file}",
            f"- checkpoint_sha256: {document_sha256}",
        ]
    )
    section = f"{body}\n<!-- anchor-hash: {_anchor_digest(body)} -->\n\n"
    is_new = not anchors_path.exists()
    with anchors_path.open("a", encoding="utf-8") as handle:
        if is_new:
            handle.write(ANCHORS_HEADER + "\n")
        handle.write(section)
    return anchors_path


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
    output = root / CHECKPOINT_DIRNAME / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    # Guard before any write: a mutated anchor ledger blocks new checkpoints.
    verify_anchors(output.parent / ANCHORS_FILENAME)
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
    serialized = json.dumps(document, indent=2, sort_keys=True) + "\n"
    output.write_text(serialized, encoding="utf-8")
    append_anchor(
        output.parent,
        timestamp=timestamp,
        workflow=workflow,
        phase=phase,
        checkpoint_file=output.name,
        document_sha256=hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    )
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
