"""
Local state helper for Atlassian context captured during chat intake.

This script never calls Jira, Confluence, Slack, or Teams. It only scans local
chat transcript markdown for Atlassian references, writes local artifact files
from already-fetched connector content, and maintains a local manifest.
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
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
DEFAULT_ROOT = SYSTEM_ROOT.parent
DEFAULT_MANIFEST = "3. Meetings/context-artifacts/atlassian/_manifest.json"
DEFAULT_ARTIFACT_ROOT = "3. Meetings/context-artifacts/atlassian"
DEFAULT_SETTINGS = "SETTINGS.md"
DEFAULT_MAX_REFS = 10
DEFAULT_TIMEZONE = "America/Chicago"
VALID_REFERENCE_TYPES = {"jira", "confluence"}
VALID_PLATFORMS = {"slack", "teams", "comms"}

URL_RE = re.compile(r"https?://[^\s<>\]\"')]+", re.IGNORECASE)
JIRA_KEY_RE = re.compile(r"(?<![A-Z0-9])([A-Z][A-Z0-9]{1,9}-\d+)(?![A-Z0-9])")
CONFLUENCE_PAGE_RE = re.compile(r"/pages/(\d+)", re.IGNORECASE)


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
    manifest = read_json(path, {"schema_version": 1, "references": {}})
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("references", {})
    return manifest


def isoformat_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed


def read_timezone(root: Path) -> str:
    settings_path = root / DEFAULT_SETTINGS
    if not settings_path.exists():
        return DEFAULT_TIMEZONE
    text = settings_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^\s*-\s+\*\*Timezone\*\*:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else DEFAULT_TIMEZONE


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def local_date_stamp(root: Path, value: dt.datetime | None = None) -> str:
    timezone_name = read_timezone(root)
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone = dt.timezone.utc
    return (value or now_utc()).astimezone(timezone).date().isoformat()


def normalize_url(url: str) -> str:
    cleaned = url.strip().rstrip(".,;:")
    return cleaned


def slugify(value: str, fallback: str = "untitled") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:100] or fallback


def short_hash(value: str, length: int = 10) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def content_hash(parts: list[str]) -> str:
    joined = "\n\n".join(part for part in parts if part)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def yaml_string(value: str | None) -> str:
    if value is None:
        return '""'
    return json.dumps(value, ensure_ascii=False)


def reference_key(reference_type: str, reference_id: str) -> str:
    return f"{reference_type}:{reference_id.lower()}"


def classify_url(url: str, line_number: int) -> dict[str, Any] | None:
    normalized = normalize_url(url)
    lower_url = normalized.lower()
    if "atlassian.net" not in lower_url:
        return None

    key_match = JIRA_KEY_RE.search(normalized)
    if key_match:
        issue_key = key_match.group(1).upper()
        return {
            "reference_type": "jira",
            "reference_id": issue_key,
            "original_reference": normalized,
            "source_url": normalized,
            "needs_url_resolution": False,
            "first_seen_line": line_number,
            "suggested_query": issue_key,
        }

    if "/wiki/" in lower_url:
        page_match = CONFLUENCE_PAGE_RE.search(normalized)
        reference_id = f"page-{page_match.group(1)}" if page_match else f"url-{short_hash(normalized)}"
        return {
            "reference_type": "confluence",
            "reference_id": reference_id,
            "original_reference": normalized,
            "source_url": normalized,
            "needs_url_resolution": False,
            "first_seen_line": line_number,
            "suggested_query": normalized,
        }

    return {
        "reference_type": "unknown",
        "reference_id": f"url-{short_hash(normalized)}",
        "original_reference": normalized,
        "source_url": normalized,
        "needs_url_resolution": True,
        "first_seen_line": line_number,
        "suggested_query": normalized,
        "issue": "ambiguous_atlassian_url",
    }


def extract_references(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    references: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    index_by_key: dict[str, int] = {}
    url_spans_by_line: dict[int, list[tuple[int, int]]] = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        spans: list[tuple[int, int]] = []
        for match in URL_RE.finditer(line):
            spans.append(match.span())
            classified = classify_url(match.group(0), line_number)
            if classified is None:
                continue
            if classified["reference_type"] not in VALID_REFERENCE_TYPES:
                skipped.append(
                    {
                        "reason": classified.get("issue", "unsupported_atlassian_url"),
                        "original_reference": classified["original_reference"],
                        "first_seen_line": line_number,
                    }
                )
                continue
            key = reference_key(classified["reference_type"], classified["reference_id"])
            if key in index_by_key:
                existing = references[index_by_key[key]]
                if not existing.get("source_url") and classified.get("source_url"):
                    existing["source_url"] = classified["source_url"]
                    existing["needs_url_resolution"] = False
                    existing["url_enriched_from_line"] = line_number
                skipped.append(
                    {
                        "reason": "duplicate_in_transcript",
                        "reference_key": key,
                        "original_reference": classified["original_reference"],
                        "first_seen_line": line_number,
                    }
                )
                continue
            classified["reference_key"] = key
            index_by_key[key] = len(references)
            references.append(classified)
        url_spans_by_line[line_number] = spans

        for match in JIRA_KEY_RE.finditer(line):
            if any(start <= match.start() < end for start, end in url_spans_by_line.get(line_number, [])):
                continue
            issue_key = match.group(1).upper()
            key = reference_key("jira", issue_key)
            if key in index_by_key:
                skipped.append(
                    {
                        "reason": "duplicate_in_transcript",
                        "reference_key": key,
                        "original_reference": issue_key,
                        "first_seen_line": line_number,
                    }
                )
                continue
            index_by_key[key] = len(references)
            references.append(
                {
                    "reference_type": "jira",
                    "reference_id": issue_key,
                    "reference_key": key,
                    "original_reference": issue_key,
                    "source_url": None,
                    "needs_url_resolution": True,
                    "first_seen_line": line_number,
                    "suggested_query": issue_key,
                }
            )

    return references, skipped


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    artifact_root = root / DEFAULT_ARTIFACT_ROOT
    for child in ("jira", "confluence"):
        (artifact_root / child).mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    manifest = load_manifest(manifest_path)
    manifest["updated_at"] = isoformat_utc(now_utc())
    write_json(manifest_path, manifest)
    print(json.dumps({"ok": True, "artifact_root": str(artifact_root), "manifest_path": str(manifest_path)}, indent=2, sort_keys=True))
    return 0


def command_scan(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    transcript_path = Path(args.transcript_path).expanduser()
    if not transcript_path.is_absolute():
        transcript_path = root / transcript_path
    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    manifest = load_manifest(manifest_path)
    issues: list[str] = []

    if not transcript_path.exists():
        print(json.dumps({"ok": False, "issues": ["transcript_path_missing"], "transcript_path": str(transcript_path)}, indent=2, sort_keys=True))
        return 2

    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    references, skipped = extract_references(text)
    max_refs = args.max_refs if args.max_refs is not None else DEFAULT_MAX_REFS
    if max_refs < 0:
        max_refs = DEFAULT_MAX_REFS
    if len(references) > max_refs:
        for ref in references[max_refs:]:
            skipped.append(
                {
                    "reason": "reference_cap_exceeded",
                    "reference_key": ref["reference_key"],
                    "original_reference": ref["original_reference"],
                    "first_seen_line": ref["first_seen_line"],
                }
            )
        references = references[:max_refs]
        issues.append("reference_cap_exceeded")

    for ref in references:
        existing = manifest.get("references", {}).get(ref["reference_key"], {})
        ref["previously_seen"] = bool(existing)
        ref["previous_artifact_paths"] = existing.get("artifact_paths", [])
        ref["latest_content_hash"] = existing.get("latest_content_hash")

    result = {
        "ok": True,
        "transcript_path": str(transcript_path),
        "manifest_path": str(manifest_path),
        "max_refs": max_refs,
        "references": references,
        "skipped": skipped,
        "issues": issues,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def read_content_arg(args: argparse.Namespace, root: Path) -> str:
    if args.fetched_content_file:
        content_path = Path(args.fetched_content_file).expanduser()
        if not content_path.is_absolute():
            content_path = root / content_path
        return content_path.read_text(encoding="utf-8", errors="replace")
    return args.fetched_content or ""


def artifact_path_for(args: argparse.Namespace, root: Path, fetched_at: dt.datetime) -> Path:
    if args.artifact_path:
        path = Path(args.artifact_path).expanduser()
        return path if path.is_absolute() else root / path
    date_stamp = local_date_stamp(root, fetched_at)
    if args.reference_type == "jira":
        filename_id = args.reference_id.upper()
    else:
        title_slug = slugify(args.title or args.reference_id, fallback=args.reference_id.lower())
        filename_id = title_slug
    filename = f"{date_stamp}_{filename_id}_{args.run_id}.md"
    return root / DEFAULT_ARTIFACT_ROOT / args.reference_type / filename


def render_artifact(
    args: argparse.Namespace,
    fetched_at: dt.datetime,
    source_content: str,
    digest: str,
) -> str:
    reference_label = args.reference_id.upper() if args.reference_type == "jira" else args.reference_id
    title = args.title or reference_label
    transcript_paths = list(args.transcript_path or [])
    message_refs = list(args.message_reference or [])
    summary = args.summary or "No extracted summary provided."
    source_updated_at = args.source_updated_at or ""
    owner = args.owner or ""
    status = args.status or ""
    first_seen_at = args.first_seen_at or ""

    frontmatter = [
        "---",
        'artifact_type: "atlassian_context"',
        f"reference_type: {yaml_string(args.reference_type)}",
        f"reference_id: {yaml_string(reference_label)}",
        f"source_url: {yaml_string(args.source_url)}",
        f"fetched_at: {yaml_string(isoformat_utc(fetched_at))}",
        f"source_updated_at: {yaml_string(source_updated_at)}",
        f"run_id: {yaml_string(args.run_id)}",
        f"platform: {yaml_string(args.platform)}",
        f"title: {yaml_string(title)}",
        f"status: {yaml_string(status)}",
        f"owner: {yaml_string(owner)}",
        f"first_seen_at: {yaml_string(first_seen_at)}",
        f"content_hash: {yaml_string(digest)}",
        "---",
        "",
    ]

    lines = [
        *frontmatter,
        f"# Atlassian Context - {args.reference_type.title()} - {title}",
        "",
        f"**Source**: [{args.source_url}]({args.source_url})",
        f"**Fetched At**: {isoformat_utc(fetched_at)}",
        f"**Reference ID**: {reference_label}",
        f"**Platform Source**: {args.platform}",
    ]
    if source_updated_at:
        lines.append(f"**Source Updated At**: {source_updated_at}")
    if status:
        lines.append(f"**Status**: {status}")
    if owner:
        lines.append(f"**Owner**: {owner}")
    if first_seen_at:
        lines.append(f"**First Seen At**: {first_seen_at}")

    lines.extend(["", "## Chat References"])
    if transcript_paths:
        lines.extend(f"- Transcript: `{path}`" for path in transcript_paths)
    else:
        lines.append("- Transcript: not provided")
    if message_refs:
        lines.extend(f"- Message: {ref}" for ref in message_refs)

    lines.extend(["", "## Extracted Context", "", summary])

    lines.extend(["", "## Source Content Snapshot"])
    lines.append("")
    if source_content.strip():
        lines.append(source_content.strip())
    else:
        lines.append("No fetched content snapshot was provided.")

    lines.extend(["", "## Routing Notes"])
    lines.append("- Route durable tasks or status updates to local tracker files only when confidence is clear.")
    lines.append("- Do not mutate Jira, Confluence, Slack, or Teams from this artifact.")
    lines.append("")
    return "\n".join(lines)


def command_record(args: argparse.Namespace) -> int:
    root = Path(args.repo).expanduser().resolve()
    issues: list[str] = []
    reference_type = args.reference_type.lower()
    platform = args.platform.lower()

    if reference_type not in VALID_REFERENCE_TYPES:
        issues.append("invalid_reference_type")
    if platform not in VALID_PLATFORMS:
        issues.append("invalid_platform")
    if not args.reference_id:
        issues.append("missing_reference_id")
    if not args.run_id:
        issues.append("missing_run_id")
    if not args.source_url or not re.match(r"^https?://", args.source_url):
        issues.append("source_url_missing_or_invalid")
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2, sort_keys=True))
        return 2

    manifest_path = Path(args.manifest).expanduser() if args.manifest else root / DEFAULT_MANIFEST
    manifest = load_manifest(manifest_path)
    fetched_at = now_utc()
    source_content = read_content_arg(args, root)
    reference_id = args.reference_id.upper() if reference_type == "jira" else args.reference_id
    digest = content_hash(
        [
            args.source_url,
            reference_type,
            reference_id,
            args.title or "",
            args.status or "",
            args.owner or "",
            args.source_updated_at or "",
            args.summary or "",
            source_content,
        ]
    )
    key = reference_key(reference_type, reference_id)
    existing = manifest["references"].get(key, {})

    if existing.get("latest_content_hash") == digest and not args.force:
        existing["last_seen_at"] = isoformat_utc(fetched_at)
        existing["last_run_id"] = args.run_id
        existing["transcript_paths"] = sorted(set(existing.get("transcript_paths", []) + list(args.transcript_path or [])))
        existing["platforms"] = sorted(set(existing.get("platforms", []) + [platform]))
        manifest["references"][key] = existing
        manifest["updated_at"] = isoformat_utc(fetched_at)
        write_json(manifest_path, manifest)
        print(
            json.dumps(
                {
                    "ok": True,
                    "stored": False,
                    "skipped_reason": "duplicate_unchanged_content",
                    "reference_key": key,
                    "artifact_paths": existing.get("artifact_paths", []),
                    "manifest_path": str(manifest_path),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    artifact_path = artifact_path_for(args, root, fetched_at)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_text = render_artifact(args, fetched_at, source_content, digest)
    artifact_path.write_text(artifact_text, encoding="utf-8")

    entry = {
        "reference_type": reference_type,
        "reference_id": reference_id,
        "source_url": args.source_url,
        "title": args.title or "",
        "status": args.status or "",
        "owner": args.owner or "",
        "source_updated_at": args.source_updated_at or "",
        "latest_content_hash": digest,
        "artifact_paths": sorted(set(existing.get("artifact_paths", []) + [str(artifact_path)])),
        "transcript_paths": sorted(set(existing.get("transcript_paths", []) + list(args.transcript_path or []))),
        "platforms": sorted(set(existing.get("platforms", []) + [platform])),
        "first_seen_at": existing.get("first_seen_at") or args.first_seen_at or isoformat_utc(fetched_at),
        "last_seen_at": isoformat_utc(fetched_at),
        "last_fetched_at": isoformat_utc(fetched_at),
        "last_run_id": args.run_id,
    }
    manifest["references"][key] = entry
    manifest["updated_at"] = isoformat_utc(fetched_at)
    write_json(manifest_path, manifest)

    print(
        json.dumps(
            {
                "ok": True,
                "stored": True,
                "reference_key": key,
                "artifact_path": str(artifact_path),
                "manifest_path": str(manifest_path),
                "content_hash": digest,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Atlassian context archive state helper")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repo root")
    parser.add_argument("--manifest", default=None, help="Override manifest path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create Atlassian artifact folders and manifest")
    init.set_defaults(func=command_init)

    scan = subparsers.add_parser("scan", help="Scan a local chat transcript for Atlassian references")
    scan.add_argument("--transcript-path", required=True)
    scan.add_argument("--max-refs", type=int, default=DEFAULT_MAX_REFS)
    scan.set_defaults(func=command_scan)

    record = subparsers.add_parser("record", help="Write a fetched Atlassian context artifact and update manifest")
    record.add_argument("--reference-type", required=True, choices=sorted(VALID_REFERENCE_TYPES))
    record.add_argument("--reference-id", required=True)
    record.add_argument("--source-url", required=True)
    record.add_argument("--run-id", required=True)
    record.add_argument("--platform", required=True, choices=sorted(VALID_PLATFORMS))
    record.add_argument("--title", default="")
    record.add_argument("--status", default="")
    record.add_argument("--owner", default="")
    record.add_argument("--summary", default="")
    record.add_argument("--source-updated-at", default="")
    record.add_argument("--first-seen-at", default="")
    record.add_argument("--transcript-path", action="append", default=[])
    record.add_argument("--message-reference", action="append", default=[])
    record.add_argument("--fetched-content", default="")
    record.add_argument("--fetched-content-file", default="")
    record.add_argument("--artifact-path", default="")
    record.add_argument("--force", action="store_true")
    record.set_defaults(func=command_record)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
