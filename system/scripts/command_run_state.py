#!/usr/bin/env python3
"""Track recurring command runs and source checkpoints.

The chat/source manifests track individual source reads. This helper tracks the
task command that requested those reads so recurring commands can shorten future
read windows only after the same source/scope completed successfully.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = Path("3. Meetings/reports/command-runs/_manifest.json")
SUCCESS_STATES = {"completed", "success", "healthy"}


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def isoformat_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_scope(scope: str) -> str:
    return re.sub(r"\s+", " ", (scope or "").strip().lower())


def slugify_scope(scope: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize_scope(scope)).strip("-")
    return slug[:80] or "unspecified"


def source_scope_key(source: str, scope: str) -> str:
    return f"{source.lower()}:{slugify_scope(scope)}"


def empty_manifest() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "runs": {},
        "commands": {},
        "source_scopes": {},
    }


def load_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    path = manifest_path or root / DEFAULT_MANIFEST
    manifest = read_json(path, empty_manifest())
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("runs", {})
    manifest.setdefault("commands", {})
    manifest.setdefault("source_scopes", {})
    return manifest


def manifest_path_for(root: Path, manifest_path: Path | None = None) -> Path:
    return manifest_path or root / DEFAULT_MANIFEST


def latest_successful_checkpoint(
    root: Path,
    source: str,
    scope: str,
    *,
    manifest_path: Path | None = None,
) -> dt.datetime | None:
    if not source or not scope:
        return None
    manifest = load_manifest(root, manifest_path)
    entry = manifest.get("source_scopes", {}).get(source_scope_key(source, scope), {})
    if str(entry.get("last_status", "")).lower() not in SUCCESS_STATES:
        return None
    checkpoint = parse_datetime(entry.get("last_successful_processed_at")) or parse_datetime(entry.get("last_successful_completed_at"))
    return checkpoint


def record_run(
    root: Path,
    *,
    command: str,
    mode: str,
    run_id: str,
    sources: list[dict[str, Any]],
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "completed",
    report_paths: list[str] | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    path = manifest_path_for(root, manifest_path)
    manifest = load_manifest(root, path)
    completed_dt = parse_datetime(completed_at) or now_utc()
    started_dt = parse_datetime(started_at) or completed_dt
    run = {
        "command": command,
        "mode": mode,
        "run_id": run_id,
        "started_at": isoformat_utc(started_dt),
        "completed_at": isoformat_utc(completed_dt),
        "status": status,
        "sources": sources,
        "report_paths": report_paths or [],
    }
    manifest["runs"][run_id] = run
    manifest["commands"][command] = {
        "last_run_id": run_id,
        "last_completed_at": run["completed_at"],
        "last_status": status,
        "mode": mode,
    }
    for source in sources:
        source_name = str(source.get("source") or source.get("platform") or "").lower()
        scope = str(source.get("scope") or "")
        source_status = str(source.get("status") or "").lower()
        if not source_name or not scope:
            continue
        key = source_scope_key(source_name, scope)
        entry = {
            "source": source_name,
            "platform": str(source.get("platform") or source_name),
            "scope": scope,
            "scope_key": key,
            "last_run_id": run_id,
            "last_completed_at": run["completed_at"],
            "last_status": source_status,
            "report_paths": report_paths or [],
        }
        if source_status in SUCCESS_STATES:
            entry["last_successful_run_id"] = run_id
            entry["last_successful_completed_at"] = run["completed_at"]
            entry["last_successful_processed_at"] = str(source.get("processed_through_at") or run["completed_at"])
            manifest["source_scopes"][key] = entry
        else:
            existing = manifest["source_scopes"].get(key, {})
            if existing:
                existing.update(
                    {
                        "last_run_id": run_id,
                        "last_completed_at": run["completed_at"],
                        "last_status": source_status,
                    }
                )
                manifest["source_scopes"][key] = existing
            else:
                manifest["source_scopes"][key] = entry
    manifest["updated_at"] = run["completed_at"]
    write_json(path, manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(ROOT), help="Repo root")
    parser.add_argument("--manifest", default=None, help="Override command-run manifest path")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    checkpoint = subparsers.add_parser("checkpoint", help="Return the latest successful source/scope checkpoint")
    checkpoint.add_argument("--source", required=True)
    checkpoint.add_argument("--scope", required=True)

    record = subparsers.add_parser("record", help="Record a command run with source statuses")
    record.add_argument("--command", required=True)
    record.add_argument("--mode", default="")
    record.add_argument("--run-id", required=True)
    record.add_argument("--source-json", action="append", default=[], help="JSON source record; repeatable")
    record.add_argument("--status", default="completed")
    record.add_argument("--started-at", default=None)
    record.add_argument("--completed-at", default=None)
    record.add_argument("--report-path", action="append", default=[])
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.repo).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else None
    if args.command_name == "checkpoint":
        checkpoint = latest_successful_checkpoint(root, args.source, args.scope, manifest_path=manifest_path)
        print(json.dumps({"ok": True, "checkpoint_at": isoformat_utc(checkpoint) if checkpoint else None}, indent=2, sort_keys=True))
        return 0
    if args.command_name == "record":
        sources = [json.loads(item) for item in args.source_json]
        manifest = record_run(
            root,
            command=args.command,
            mode=args.mode,
            run_id=args.run_id,
            sources=sources,
            started_at=args.started_at,
            completed_at=args.completed_at,
            status=args.status,
            report_paths=args.report_path,
            manifest_path=manifest_path,
        )
        print(json.dumps({"ok": True, "manifest_path": str(manifest_path_for(root, manifest_path)), "updated_at": manifest.get("updated_at")}, indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
