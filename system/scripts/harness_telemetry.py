#!/usr/bin/env python3
"""Record and summarize completed Beats harness workflow trajectories."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEDGER_REL = Path(".beats/harness/telemetry.jsonl")
USAGE_LEDGER_REL = Path(".beats/usage.jsonl")
USAGE_MAX_LINES = 2000
USAGE_KEEP_LINES = 1000
TOKEN_FIELDS = (
    "uncached_input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "tool_payload_tokens",
)
COUNT_FIELDS = ("turns", "retries", "compactions", "source_loads")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def append_usage(
    command: str,
    *,
    sources_loaded: int,
    source_bytes: int,
    wall_ms: float,
    root: Path = ROOT,
    ledger: Path | None = None,
    max_lines: int = USAGE_MAX_LINES,
    keep_lines: int = USAGE_KEEP_LINES,
) -> dict[str, Any]:
    """Append one per-command usage entry to the bounded `.beats/usage.jsonl` ledger."""
    entry = {
        "ts": utc_now(),
        "command": str(command),
        "sources_loaded": int(sources_loaded),
        "source_bytes": int(source_bytes),
        "wall_ms": round(float(wall_ms), 3),
    }
    destination = ledger or root / USAGE_LEDGER_REL
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, separators=(",", ":"), sort_keys=True) + "\n")
    rotate_usage_ledger(destination, max_lines=max_lines, keep_lines=keep_lines)
    return entry


def rotate_usage_ledger(path: Path, *, max_lines: int = USAGE_MAX_LINES, keep_lines: int = USAGE_KEEP_LINES) -> bool:
    """Rewrite the ledger keeping only the newest `keep_lines` once it exceeds `max_lines`."""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return False
    path.write_text("\n".join(lines[-keep_lines:]) + "\n", encoding="utf-8")
    return True


def load_usage(path: Path) -> list[dict[str, Any]]:
    """Load usage entries, tolerating malformed lines (reporting must stay graceful)."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and "command" in entry:
            entries.append(entry)
    return entries


def usage_hotspots(entries: list[dict[str, Any]], *, top: int = 5) -> list[dict[str, Any]]:
    """Rank commands by mean source_bytes per resolution, with run counts."""
    grouped: dict[str, list[int]] = {}
    for entry in entries:
        size = entry.get("source_bytes")
        if isinstance(size, bool) or not isinstance(size, (int, float)):
            continue
        grouped.setdefault(str(entry["command"]), []).append(int(size))
    ranked = [
        {
            "command": command,
            "runs": len(sizes),
            "mean_source_bytes": int(statistics.mean(sizes)),
        }
        for command, sizes in grouped.items()
    ]
    ranked.sort(key=lambda row: (-row["mean_source_bytes"], row["command"]))
    return ranked[:top]


def validate_record(record: dict[str, Any]) -> None:
    required = {
        "workflow",
        "scenario",
        "runtime",
        "model",
        "effort",
        "registry_version",
        "repository_fixture",
        "cache_state",
        "elapsed_seconds",
        "quality_result",
        *TOKEN_FIELDS,
        *COUNT_FIELDS,
    }
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError("Missing telemetry fields: " + ", ".join(missing))
    for field in [*TOKEN_FIELDS, *COUNT_FIELDS, "elapsed_seconds"]:
        value = record[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{field} must be a non-negative number")
    if record["cache_state"] not in {"cold", "warm", "mixed"}:
        raise ValueError("cache_state must be cold, warm, or mixed")


def enrich_record(
    record: dict[str, Any],
    *,
    uncached_input_cost_per_million: float = 0.0,
    cached_input_cost_per_million: float = 0.0,
    cache_write_cost_per_million: float = 0.0,
    output_cost_per_million: float = 0.0,
) -> dict[str, Any]:
    validate_record(record)
    total = sum(int(record[field]) for field in TOKEN_FIELDS)
    billable = (
        int(record["uncached_input_tokens"])
        + int(record["cached_input_tokens"])
        + int(record["cache_write_tokens"])
        + int(record["output_tokens"])
    )
    cost = (
        record["uncached_input_tokens"] * uncached_input_cost_per_million
        + record["cached_input_tokens"] * cached_input_cost_per_million
        + record["cache_write_tokens"] * cache_write_cost_per_million
        + record["output_tokens"] * output_cost_per_million
    ) / 1_000_000
    return {
        "schema_version": 1,
        "recorded_at": utc_now(),
        **record,
        "total_processed_tokens": total,
        "estimated_billable_tokens": billable,
        "estimated_billable_cost_usd": round(cost, 8),
    }


def append_record(record: dict[str, Any], *, root: Path = ROOT, ledger: Path | None = None, **rates: float) -> dict[str, Any]:
    enriched = enrich_record(record, **rates)
    destination = ledger or root / LEDGER_REL
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(enriched, separators=(",", ":"), sort_keys=True) + "\n")
    return enriched


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid telemetry JSON on line {number}") from exc
    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"schema_version": 1, "count": 0, "by_cache_state": {}}
    by_cache: dict[str, int] = {}
    for record in records:
        state = str(record["cache_state"])
        by_cache[state] = by_cache.get(state, 0) + 1
    return {
        "schema_version": 1,
        "count": len(records),
        "median_total_processed_tokens": statistics.median(record["total_processed_tokens"] for record in records),
        "median_turns": statistics.median(record["turns"] for record in records),
        "median_elapsed_seconds": statistics.median(record["elapsed_seconds"] for record in records),
        "estimated_billable_cost_usd": round(sum(record["estimated_billable_cost_usd"] for record in records), 8),
        "by_cache_state": by_cache,
    }


def export_optimizer_payload(records: list[dict[str, Any]], *, label: str) -> dict[str, Any]:
    """Convert matched trajectory records into the optimizer's paired schema."""
    scenarios = []
    seen = set()
    quality_fields = {
        "functionality_score",
        "intent_score",
        "source_citation_recall",
        "exact_wording_preserved",
        "approval_privacy_unchanged",
        "artifact_compatible",
    }
    for record in records:
        scenario_id = f"{record['runtime']}:{record['cache_state']}:{record['scenario']}"
        if scenario_id in seen:
            raise ValueError(f"Duplicate paired trajectory: {scenario_id}")
        seen.add(scenario_id)
        quality = record.get("quality_result")
        if not isinstance(quality, dict) or not quality_fields.issubset(quality):
            raise ValueError(f"Trajectory {scenario_id} lacks optimizer quality gates")
        scenarios.append(
            {
                "id": scenario_id,
                "total_processed_tokens": record["total_processed_tokens"],
                "turns": record["turns"],
                "pairing": {
                    "runtime": record["runtime"],
                    "model": record["model"],
                    "effort": record["effort"],
                    "cache_state": record["cache_state"],
                    "repository_fixture": record["repository_fixture"],
                },
                **{field: quality[field] for field in sorted(quality_fields)},
            }
        )
    return {"schema_version": 1, "label": label, "scenarios": scenarios}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--ledger", type=Path)
    subparsers = parser.add_subparsers(dest="action", required=True)
    record = subparsers.add_parser("record")
    record.add_argument("--input", type=Path, required=True)
    record.add_argument("--uncached-input-cost-per-million", type=float, default=0.0)
    record.add_argument("--cached-input-cost-per-million", type=float, default=0.0)
    record.add_argument("--cache-write-cost-per-million", type=float, default=0.0)
    record.add_argument("--output-cost-per-million", type=float, default=0.0)
    subparsers.add_parser("summary")
    export = subparsers.add_parser("export")
    export.add_argument("--label", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    ledger = args.ledger or root / LEDGER_REL
    try:
        if args.action == "record":
            record = json.loads(args.input.read_text(encoding="utf-8"))
            payload = append_record(
                record,
                root=root,
                ledger=ledger,
                uncached_input_cost_per_million=args.uncached_input_cost_per_million,
                cached_input_cost_per_million=args.cached_input_cost_per_million,
                cache_write_cost_per_million=args.cache_write_cost_per_million,
                output_cost_per_million=args.output_cost_per_million,
            )
        elif args.action == "summary":
            payload = summarize(load_records(ledger))
        else:
            payload = export_optimizer_payload(load_records(ledger), label=args.label)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"harness-telemetry: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
