"""
State helper for read-only communication intake workflows.

This script does not read Slack, Teams, Outlook, or Calendar. It only computes
safe intake windows from local defaults and a local manifest, then records
successful local runs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:  # pragma: no cover - import path differs for script vs package execution.
    from . import command_run_state
except ImportError:  # pragma: no cover
    import command_run_state


CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
DEFAULT_ROOT = SYSTEM_ROOT.parent
DEFAULT_MANIFEST = "3. Meetings/chat-transcripts/_manifest.json"
DEFAULT_SETTINGS = "SETTINGS.md"
DEFAULT_BUSINESS_DAYS = 5
DEFAULT_CALENDAR_DAYS = 14
DEFAULT_SLACK_CHUNK_HOURS = 24
DEFAULT_TIMEZONE = "America/Chicago"
BACKWARD_WINDOW_PLATFORMS = {"slack", "teams", "outlook"}
FORWARD_WINDOW_PLATFORMS = {"calendar"}
VALID_PLATFORMS = BACKWARD_WINDOW_PLATFORMS | FORWARD_WINDOW_PLATFORMS


def business_days_ago(n: int, today: dt.date | None = None) -> dt.date:
    if n < 0:
        raise ValueError("business days must be non-negative")
    current = today or dt.date.today()
    count = 0
    while count < n:
        current -= dt.timedelta(days=1)
        if current.weekday() < 5:
            count += 1
    return current


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


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path, {"schema_version": 1, "scopes": {}})
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("scopes", {})
    return manifest


def normalize_scope(scope: str) -> str:
    normalized = scope.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def slugify_scope(scope: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize_scope(scope)).strip("-")
    return slug[:80] or "unspecified"


def scope_key(platform: str, scope: str) -> str:
    return f"{platform}:{slugify_scope(scope)}"


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
        try:
            parsed_date = dt.date.fromisoformat(text)
        except ValueError:
            return None
        parsed = dt.datetime.combine(parsed_date, dt.time.min)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def parse_boundary_datetime(value: str | None, timezone_name: str = DEFAULT_TIMEZONE) -> dt.datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = dt.timezone.utc
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            parsed_date = dt.date.fromisoformat(text)
        except ValueError:
            return None
        return dt.datetime.combine(parsed_date, dt.time.min, tzinfo=timezone).astimezone(dt.timezone.utc)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(dt.timezone.utc)


def isoformat_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_settings_defaults(root: Path) -> dict[str, Any]:
    settings_path = root / DEFAULT_SETTINGS
    defaults = {
        "default_business_days": DEFAULT_BUSINESS_DAYS,
        "default_scope_policy": "require_scope",
        "route_tasks_by_default": True,
        "source_system_mutation": "prohibited",
        "timezone": DEFAULT_TIMEZONE,
    }
    if not settings_path.exists():
        return defaults
    text = settings_path.read_text(encoding="utf-8", errors="replace")
    section_match = re.search(
        r"^## Communication Intake Defaults\s*(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        return defaults
    body = section_match.group("body")
    for key in list(defaults):
        match = re.search(rf"^\s*-\s*`?{re.escape(key)}`?\s*:\s*(.+?)\s*$", body, flags=re.MULTILINE)
        if not match:
            continue
        raw = match.group(1).strip().strip("`")
        if key == "default_business_days":
            try:
                defaults[key] = int(raw)
            except ValueError:
                pass
        elif key == "route_tasks_by_default":
            defaults[key] = raw.lower() in {"true", "yes", "1", "on"}
        else:
            defaults[key] = raw
    timezone_match = re.search(r"^\s*-\s+\*\*Timezone\*\*:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if timezone_match:
        defaults["timezone"] = timezone_match.group(1).strip()
    return defaults


def default_cutoff_at(
    business_days: int,
    timezone_name: str = DEFAULT_TIMEZONE,
    now: dt.datetime | None = None,
) -> dt.datetime:
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = dt.timezone.utc
    current = (now or dt.datetime.now(dt.timezone.utc)).astimezone(timezone)
    cutoff_day = business_days_ago(business_days, today=current.date())
    local_cutoff = dt.datetime.combine(cutoff_day, dt.time.min, tzinfo=timezone)
    return local_cutoff.astimezone(dt.timezone.utc)


def default_forward_window(
    days: int,
    timezone_name: str = DEFAULT_TIMEZONE,
    now: dt.datetime | None = None,
) -> tuple[dt.datetime, dt.datetime]:
    if days < 0:
        raise ValueError("days must be non-negative")
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = dt.timezone.utc
    start = (now or dt.datetime.now(dt.timezone.utc)).astimezone(timezone)
    end = start + dt.timedelta(days=days)
    return start.astimezone(dt.timezone.utc), end.astimezone(dt.timezone.utc)


def compute_window_result(
    root: Path,
    manifest_path: Path,
    platform: str,
    scope: str,
    business_days: int,
    calendar_days: int,
    settings: dict[str, Any],
) -> dict[str, Any]:
    issues: list[str] = []

    if platform not in VALID_PLATFORMS:
        issues.append("invalid_platform")
    if not scope:
        issues.append("missing_scope")

    manifest = load_manifest(manifest_path)
    normalized_scope = normalize_scope(scope) if scope else ""
    slug = slugify_scope(scope) if scope else ""
    key = scope_key(platform, scope) if scope else ""
    entry = manifest.get("scopes", {}).get(key, {})
    last_success = parse_datetime(entry.get("last_successful_processed_at"))
    command_checkpoint = command_run_state.latest_successful_checkpoint(root, platform, scope)

    now = dt.datetime.now(dt.timezone.utc)
    effective_end: dt.datetime | None = now
    if platform in FORWARD_WINDOW_PLATFORMS:
        cutoff = default_cutoff_at(
            business_days,
            timezone_name=str(settings["timezone"]),
            now=now,
        )
        effective_start = cutoff
        window_source = f"default_{business_days}_business_days_plus_{calendar_days}_calendar_days_forward"
        candidates = [
            ("manifest_last_successful_processed_at", last_success),
            ("command_run_last_successful_processed_at", command_checkpoint),
        ]
        for candidate_source, candidate in candidates:
            if candidate and candidate > effective_start:
                effective_start = candidate
                window_source = candidate_source
        lookahead_start, effective_end = default_forward_window(
            calendar_days,
            timezone_name=str(settings["timezone"]),
            now=now,
        )
    else:
        cutoff = default_cutoff_at(
            business_days,
            timezone_name=str(settings["timezone"]),
            now=now,
        )
        effective_start = cutoff
        window_source = f"default_{business_days}_business_days"
        candidates = [
            ("manifest_last_successful_processed_at", last_success),
            ("command_run_last_successful_processed_at", command_checkpoint),
        ]
        for candidate_source, candidate in candidates:
            if candidate and candidate > effective_start:
                effective_start = candidate
                window_source = candidate_source
        if window_source == f"default_{business_days}_business_days" and last_success:
            window_source = f"default_{business_days}_business_days_last_success_older"
        lookahead_start = None

    return {
        "ok": not issues,
        "platform": platform,
        "scope": scope,
        "normalized_scope": normalized_scope,
        "scope_slug": slug,
        "scope_key": key,
        "default_business_days": business_days,
        "default_calendar_days": DEFAULT_CALENDAR_DAYS,
        "calendar_days": calendar_days if platform in FORWARD_WINDOW_PLATFORMS else None,
        "default_scope_policy": settings["default_scope_policy"],
        "route_tasks_by_default": settings["route_tasks_by_default"],
        "source_system_mutation": settings["source_system_mutation"],
        "timezone": settings["timezone"],
        "manifest_path": str(manifest_path),
        "default_cutoff_at": isoformat_utc(cutoff),
        "last_successful_processed_at": isoformat_utc(last_success) if last_success else None,
        "command_run_last_successful_processed_at": isoformat_utc(command_checkpoint) if command_checkpoint else None,
        "effective_start_at": isoformat_utc(effective_start),
        "effective_end_at": isoformat_utc(effective_end) if effective_end else None,
        "lookahead_start_at": isoformat_utc(lookahead_start) if lookahead_start else None,
        "lookahead_end_at": isoformat_utc(effective_end) if lookahead_start and effective_end else None,
        "window_source": window_source,
        "window_direction": "backward_plus_forward" if platform in FORWARD_WINDOW_PLATFORMS else "backward",
        "window_label": "named read-only source window",
        "issues": issues,
    }


def command_window(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    platform = args.platform.lower()
    scope = (args.scope or "").strip()
    settings = read_settings_defaults(root)
    business_days = args.business_days or int(settings["default_business_days"])
    calendar_days = args.days if args.days is not None else DEFAULT_CALENDAR_DAYS
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    result = compute_window_result(root, manifest_path, platform, scope, business_days, calendar_days, settings)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 2


def build_time_chunks(
    start: dt.datetime,
    end: dt.datetime,
    chunk_hours: int,
    timezone_name: str,
) -> list[dict[str, Any]]:
    if chunk_hours <= 0:
        raise ValueError("chunk hours must be positive")
    if end <= start:
        return []
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = dt.timezone.utc

    chunks: list[dict[str, Any]] = []
    local_current = start.astimezone(timezone)
    local_end = end.astimezone(timezone)
    while local_current < local_end:
        local_next = min(local_current + dt.timedelta(hours=chunk_hours), local_end)
        chunk_start = local_current.astimezone(dt.timezone.utc)
        chunk_end = local_next.astimezone(dt.timezone.utc)
        starts_at_midnight = local_current.timetz().replace(tzinfo=None) == dt.time.min
        ends_at_midnight = local_next.timetz().replace(tzinfo=None) == dt.time.min
        before_date = local_next.date()
        if not ends_at_midnight:
            before_date = before_date + dt.timedelta(days=1)
        chunks.append(
            {
                "index": len(chunks) + 1,
                "start_at": isoformat_utc(chunk_start),
                "end_at": isoformat_utc(chunk_end),
                "start_epoch": int(chunk_start.timestamp()),
                "end_epoch": int(chunk_end.timestamp()),
                "local_start_at": local_current.isoformat(),
                "local_end_at": local_next.isoformat(),
                "slack_query_date_hint": (
                    f"after:{local_current.date().isoformat()} before:{before_date.isoformat()}"
                ),
                "requires_exact_time_filter": not (starts_at_midnight and ends_at_midnight),
            }
        )
        local_current = local_next
    return chunks


def command_chunks(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    platform = args.platform.lower()
    scope = (args.scope or "").strip()
    settings = read_settings_defaults(root)
    business_days = args.business_days or int(settings["default_business_days"])
    calendar_days = args.days if args.days is not None else DEFAULT_CALENDAR_DAYS
    chunk_hours = args.chunk_hours if args.chunk_hours is not None else DEFAULT_SLACK_CHUNK_HOURS
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    issues: list[str] = []

    if platform not in VALID_PLATFORMS:
        issues.append("invalid_platform")
    if not scope:
        issues.append("missing_scope")
    if chunk_hours <= 0:
        issues.append("invalid_chunk_hours")

    window_result = compute_window_result(root, manifest_path, platform, scope, business_days, calendar_days, settings)
    start = parse_boundary_datetime(args.start, str(settings["timezone"])) if args.start else parse_datetime(window_result.get("effective_start_at"))
    end = parse_boundary_datetime(args.end, str(settings["timezone"])) if args.end else parse_datetime(window_result.get("effective_end_at"))
    if start is None:
        issues.append("invalid_start")
    if end is None:
        issues.append("invalid_end")
    if start and end and end <= start:
        issues.append("end_not_after_start")

    chunks: list[dict[str, Any]] = []
    if not issues and start and end:
        chunks = build_time_chunks(start, end, chunk_hours, str(settings["timezone"]))

    result = {
        "ok": not issues,
        "platform": platform,
        "scope": scope,
        "normalized_scope": normalize_scope(scope) if scope else "",
        "scope_slug": slugify_scope(scope) if scope else "",
        "timezone": settings["timezone"],
        "manifest_path": str(manifest_path),
        "window_source": window_result.get("window_source"),
        "window_direction": window_result.get("window_direction"),
        "start_at": isoformat_utc(start) if start else None,
        "end_at": isoformat_utc(end) if end else None,
        "chunk_hours": chunk_hours,
        "chunk_count": len(chunks),
        "strategy": "time_chunked_read",
        "read_order": "oldest_to_newest",
        "boundary_note": "Prefer exact start_epoch/end_epoch filters when the runtime exposes them; Slack date hints are day-granular.",
        "chunks": chunks,
        "issues": sorted(set(issues + window_result.get("issues", []))),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 2


def command_record(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    platform = args.platform.lower()
    scope = (args.scope or "").strip()
    issues: list[str] = []
    if platform not in VALID_PLATFORMS:
        issues.append("invalid_platform")
    if not scope:
        issues.append("missing_scope")
    if not args.run_id:
        issues.append("missing_run_id")
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2, sort_keys=True))
        return 2

    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    manifest = load_manifest(manifest_path)
    manifest.setdefault("scopes", {})
    now = dt.datetime.now(dt.timezone.utc)
    latest_source = parse_datetime(args.latest_source_timestamp)
    processed_at = latest_source or now
    entry_key = scope_key(platform, scope)
    existing = manifest["scopes"].get(entry_key, {})
    entry = {
        "platform": platform,
        "scope": scope,
        "normalized_scope": normalize_scope(scope),
        "scope_slug": slugify_scope(scope),
        "last_run_id": args.run_id,
        "last_successful_processed_at": isoformat_utc(processed_at),
        "latest_source_timestamp": isoformat_utc(latest_source) if latest_source else None,
        "transcript_paths": sorted(set(existing.get("transcript_paths", []) + list(args.transcript_path or []))),
        "run_report_paths": sorted(set(existing.get("run_report_paths", []) + list(args.run_report_path or []))),
        "updated_at": isoformat_utc(now),
    }
    entry["issues"] = []
    if latest_source is None:
        entry["issues"].append("latest_source_timestamp_missing_used_run_completion_time")
    manifest["scopes"][entry_key] = entry
    manifest["updated_at"] = isoformat_utc(now)
    write_json(manifest_path, manifest)
    print(json.dumps({"ok": True, "manifest_path": str(manifest_path), "scope_key": entry_key, "entry": entry}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chat intake state helper")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repo root")
    parser.add_argument("--manifest", default=None, help="Override manifest path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    window = subparsers.add_parser("window", help="Compute the effective read window")
    window.add_argument("--platform", required=True, choices=sorted(VALID_PLATFORMS))
    window.add_argument("--scope", default="")
    window.add_argument("--business-days", type=int, default=None)
    window.add_argument("--days", type=int, default=None, help="Forward lookahead days for calendar windows")
    window.set_defaults(func=command_window)

    chunks = subparsers.add_parser("chunks", help="Compute page-cap-safe source read chunks")
    chunks.add_argument("--platform", required=True, choices=sorted(VALID_PLATFORMS))
    chunks.add_argument("--scope", default="")
    chunks.add_argument("--start", default=None, help="Inclusive start boundary; date-only values use the configured timezone")
    chunks.add_argument("--end", default=None, help="Exclusive end boundary; date-only values use the configured timezone")
    chunks.add_argument("--business-days", type=int, default=None)
    chunks.add_argument("--days", type=int, default=None, help="Forward lookahead days for calendar windows")
    chunks.add_argument("--chunk-hours", type=int, default=None, help="Chunk size; defaults to 24 hours")
    chunks.set_defaults(func=command_chunks)

    record = subparsers.add_parser("record", help="Record a successful local intake run")
    record.add_argument("--platform", required=True, choices=sorted(VALID_PLATFORMS))
    record.add_argument("--scope", required=True)
    record.add_argument("--run-id", required=True)
    record.add_argument("--latest-source-timestamp", default=None)
    record.add_argument("--transcript-path", action="append", default=[])
    record.add_argument("--run-report-path", action="append", default=[])
    record.set_defaults(func=command_record)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
