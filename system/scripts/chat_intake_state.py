"""
State helper for read-only Slack/Teams communication intake workflows.

This script does not read Slack or Teams. It only computes safe intake windows
from local defaults and a local manifest, then records successful local runs.
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


CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
DEFAULT_ROOT = SYSTEM_ROOT.parent
DEFAULT_MANIFEST = "3. Meetings/chat-transcripts/_manifest.json"
DEFAULT_SETTINGS = "SETTINGS.md"
DEFAULT_BUSINESS_DAYS = 5
DEFAULT_TIMEZONE = "America/Chicago"
VALID_PLATFORMS = {"slack", "teams"}


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


def command_window(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    platform = args.platform.lower()
    scope = (args.scope or "").strip()
    settings = read_settings_defaults(root)
    business_days = args.business_days or int(settings["default_business_days"])
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
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
    cutoff = default_cutoff_at(business_days, timezone_name=str(settings["timezone"]))
    last_success = parse_datetime(entry.get("last_successful_processed_at"))

    effective_start = cutoff
    window_source = f"default_{business_days}_business_days"
    if last_success and last_success > cutoff:
        effective_start = last_success
        window_source = "manifest_last_successful_processed_at"
    elif last_success:
        window_source = f"default_{business_days}_business_days_last_success_older"

    result = {
        "ok": not issues,
        "platform": platform,
        "scope": scope,
        "normalized_scope": normalized_scope,
        "scope_slug": slug,
        "scope_key": key,
        "default_business_days": business_days,
        "default_scope_policy": settings["default_scope_policy"],
        "route_tasks_by_default": settings["route_tasks_by_default"],
        "source_system_mutation": settings["source_system_mutation"],
        "timezone": settings["timezone"],
        "manifest_path": str(manifest_path),
        "default_cutoff_at": isoformat_utc(cutoff),
        "last_successful_processed_at": isoformat_utc(last_success) if last_success else None,
        "effective_start_at": isoformat_utc(effective_start),
        "window_source": window_source,
        "issues": issues,
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
    window.set_defaults(func=command_window)

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
