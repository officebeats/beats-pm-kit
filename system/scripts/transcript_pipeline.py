"""
Deterministic transcript pipeline for /transcript workflows.

This script owns the runtime-safe parts of transcript processing:
- import/normalize transcript files
- maintain a hash-based manifest
- create scoped synthesis packets for model runtimes
- validate synthesized summaries before marking transcripts complete
- emit compact recent-meeting output

Model runtimes still perform the actual synthesis and durable PM-memory edits,
but they should work from packets created here rather than rediscovering state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
DEFAULT_ROOT = SYSTEM_ROOT.parent

if str(DEFAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_ROOT))

from system.utils.markdown_tables import split_cells  # noqa: E402

MANIFEST_NAME = "_manifest.json"
SUMMARY_SUFFIX = ".md"
PACKETS_DIRNAME = "packets"
RUNS_DIRNAME = "transcript-runs"
TRANSCRIPT_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<title>.+)\.txt$")
TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+[a-z]?\b")


def business_days_ago(n: int, today: dt.date | None = None) -> dt.date:
    """Return the date n business days before today."""
    if n < 0:
        raise ValueError("business days must be non-negative")
    current = today or dt.date.today()
    count = 0
    while count < n:
        current -= dt.timedelta(days=1)
        if current.weekday() < 5:
            count += 1
    return current


def sanitize_filename(name: str) -> str:
    """Keep filenames portable across local runtimes."""
    cleaned = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned or "Untitled Meeting"


def slugify_summary_name(transcript_path: Path) -> str:
    """Derive a stable summary filename from a transcript filename."""
    stem = transcript_path.stem
    if "_" in stem:
        date_part, title_part = stem.split("_", 1)
        title_part = re.sub(r"\s+", "-", sanitize_filename(title_part))
        return f"{date_part}_{title_part}{SUMMARY_SUFFIX}"
    return f"{sanitize_filename(stem).replace(' ', '-')}{SUMMARY_SUFFIX}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def repo_paths(root: Path) -> dict[str, Path]:
    meetings = root / "3. Meetings"
    transcripts = meetings / "transcripts"
    summaries = meetings / "summaries"
    reports = meetings / "reports"
    packets = reports / PACKETS_DIRNAME
    runs = reports / RUNS_DIRNAME
    return {
        "root": root,
        "incoming": root / "0. Incoming",
        "transcripts": transcripts,
        "summaries": summaries,
        "reports": reports,
        "packets": packets,
        "runs": runs,
        "manifest": transcripts / MANIFEST_NAME,
        "people": root / "4. People",
        "task_master": root / "5. Trackers" / "TASK_MASTER.md",
        "ways": root / "1. Company" / "ways-of-working.md",
    }


def parse_transcript_metadata(path: Path) -> dict[str, str]:
    match = TRANSCRIPT_RE.match(path.name)
    if match:
        return {
            "meeting_date": match.group("date"),
            "title": match.group("title").strip() or path.stem,
        }
    return {"meeting_date": "", "title": path.stem}


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json(path, {"schema_version": 1, "transcripts": {}})
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("transcripts", {})
    return manifest


def existing_summary_for(transcript_path: Path, summaries_dir: Path) -> Path:
    return summaries_dir / slugify_summary_name(transcript_path)


def normalized_relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def discover_people(root: Path, text: str, limit: int = 12) -> list[dict[str, str]]:
    people_dir = repo_paths(root)["people"]
    if not people_dir.exists():
        return []
    lowered = text.lower()
    matches = []
    for path in sorted(people_dir.glob("*.md")):
        if path.name.startswith("_") or path.name == "PEOPLE.md":
            continue
        tokens = [token for token in path.stem.replace("-", " ").split() if len(token) > 2]
        score = sum(1 for token in tokens if token.lower() in lowered)
        if score:
            matches.append({"name": path.stem.replace("-", " ").title(), "path": normalized_relpath(path, root)})
        if len(matches) >= limit:
            break
    return matches


def discover_task_ids(text: str, task_master_text: str, limit: int = 24) -> list[str]:
    found = list(dict.fromkeys(TASK_ID_RE.findall(text)))
    if not found:
        # Include active task IDs from the ledger as lightweight context.
        found = list(dict.fromkeys(TASK_ID_RE.findall(task_master_text)))[:limit]
    return found[:limit]


def classify_packet(text: str) -> dict[str, bool]:
    lowered = text.lower()
    manager = any(token in lowered for token in ("direct manager", "manager sync", "1:1"))
    partner = any(
        token in lowered
        for token in (
            "partner",
            "client",
            "customer",
            "sandbox",
            "access request",
            "commercial risk",
            "competitive signal",
            "gtm signal",
        )
    )
    return {"manager_mode_required": manager, "partner_customer_mode_required": partner}


def build_packet(root: Path, transcript_path: Path, entry: dict[str, Any], run_id: str) -> dict[str, Any]:
    paths = repo_paths(root)
    transcript_text = transcript_path.read_text(encoding="utf-8", errors="replace")
    task_master_text = ""
    if paths["task_master"].exists():
        task_master_text = paths["task_master"].read_text(encoding="utf-8", errors="replace")
    classification = classify_packet(transcript_text)
    required_checks = [
        "Summary",
        "Action Items",
        "Decisions Made",
        "Open Questions",
        "Hybrid Appendix",
        "Routed Updates",
    ]
    if classification["manager_mode_required"]:
        required_checks.extend(
            [
                "Ways-of-working update decision",
                "Manager profile update decision",
                "Stakeholder dynamics update decision",
                "TASK_MASTER update decision",
            ]
        )
    if classification["partner_customer_mode_required"]:
        required_checks.extend(
            [
                "Partner/client file update decision",
                "Access/commercial-risk extraction",
                "Competitive or GTM signal extraction",
            ]
        )

    return {
        "schema_version": 1,
        "run_id": run_id,
        "transcript": {
            "path": entry["transcript_path"],
            "content_sha256": entry["content_sha256"],
            "title": entry["title"],
            "meeting_date": entry["meeting_date"],
            "expected_summary_path": entry["expected_summary_path"],
        },
        "classification_hints": classification,
        "candidate_people": discover_people(root, transcript_text),
        "candidate_task_ids": discover_task_ids(transcript_text, task_master_text),
        "routing_checklist": required_checks,
        "summary_contract": {
            "must_include": [
                "Source Transcript",
                "Transcript SHA256",
                "Pipeline Run ID",
                "Routed Updates",
                "Key Evidence",
            ],
            "raw_transcript_policy": (
                "Hybrid appendix: include key evidence snippets and source path/hash; "
                "do not append the full raw transcript unless explicitly requested."
            ),
        },
    }


def ensure_manifest_entries(root: Path, cutoff_date: dt.date, run_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    paths = repo_paths(root)
    paths["transcripts"].mkdir(parents=True, exist_ok=True)
    paths["summaries"].mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(paths["manifest"])
    entries = manifest["transcripts"]
    current_hashes = set(entries)
    imported = []

    for transcript_path in sorted(paths["transcripts"].glob("*.txt")):
        meta = parse_transcript_metadata(transcript_path)
        if meta["meeting_date"]:
            try:
                meeting_date = dt.date.fromisoformat(meta["meeting_date"])
                if meeting_date < cutoff_date:
                    continue
            except ValueError:
                pass

        content_hash = sha256_file(transcript_path)
        summary_path = existing_summary_for(transcript_path, paths["summaries"])
        existing_entry = entries.get(content_hash, {})
        status = existing_entry.get("status")
        if not status:
            status = "summarized" if summary_path.exists() else "pending"
        entry = {
            "content_sha256": content_hash,
            "title": meta["title"],
            "meeting_date": meta["meeting_date"],
            "source": existing_entry.get("source", "transcripts"),
            "transcript_path": normalized_relpath(transcript_path, root),
            "expected_summary_path": normalized_relpath(summary_path, root),
            "status": status,
            "run_id": existing_entry.get("run_id", run_id if status == "pending" else existing_entry.get("run_id", "")),
            "last_validation": existing_entry.get("last_validation"),
        }
        if existing_entry.get("packet_path"):
            entry["packet_path"] = existing_entry["packet_path"]
        if content_hash not in current_hashes:
            imported.append(entry)
        entries[content_hash] = entry

    manifest["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    return manifest, imported


def run_command(cmd: list[str], root: Path, timeout: int = 45) -> dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:
        return {"command": cmd, "returncode": 1, "stdout": "", "stderr": str(exc)}


def collect_sources(
    root: Path,
    skip_import: bool = False,
    quill_mode: str = "bridge",
) -> dict[str, Any]:
    sources: dict[str, Any] = {}
    if skip_import:
        for source in ("quill", "intake", "outlook", "calendar", "teams"):
            sources[source] = {"status": "skipped"}
        return sources

    if quill_mode == "native-mcp":
        sources["quill"] = {
            "status": "ok",
            "transport": "native_mcp",
            "detail": "Transcript files were staged by the runtime's read-only Quill tools before prepare.",
        }
    else:
        quill = run_command([sys.executable, "system/scripts/quill_mcp_client.py"], root, timeout=90)
        if quill["returncode"] != 0:
            fallback = run_command([sys.executable, "system/scripts/transcript_fetcher.py"], root, timeout=90)
            sources["quill"] = {"status": "fallback", "primary": quill, "fallback": fallback}
        else:
            sources["quill"] = {"status": "ok", "transport": "stdio_bridge", "primary": quill}
    sources["intake"] = run_command([sys.executable, "system/scripts/transcript_intake.py"], root, timeout=45)

    outlook = run_command([sys.executable, "system/scripts/outlook_bridge.py", "--count", "10"], root)
    sources["outlook"] = {"status": "ok" if outlook["returncode"] == 0 else "unavailable", "result": outlook}
    calendar = run_command([sys.executable, "system/scripts/outlook_bridge.py", "--calendar", "14"], root)
    sources["calendar"] = {"status": "ok" if calendar["returncode"] == 0 else "unavailable", "result": calendar}
    teams = run_command([sys.executable, "system/scripts/beats.py", "teams", "--", "--json"], root)
    sources["teams"] = {
        "status": "ok" if teams["returncode"] == 0 else "unavailable",
        "result": teams,
        "remediation": (
            "Prefer a named read-only /beats-comms teams: source window with read-only MS365 MCP/connector access. "
            "If unavailable, open Teams, select/copy the target chat/channel, then rerun prepare."
        ),
    }
    return sources


def prepare(
    root: Path,
    business_days: int,
    json_output: bool,
    skip_import: bool = False,
    quill_mode: str = "bridge",
) -> dict[str, Any]:
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    paths = repo_paths(root)
    for key in ("packets", "runs", "summaries", "transcripts"):
        paths[key].mkdir(parents=True, exist_ok=True)

    sources = collect_sources(root, skip_import=skip_import, quill_mode=quill_mode)
    cutoff = business_days_ago(business_days)
    manifest, imported = ensure_manifest_entries(root, cutoff, run_id)

    packets = []
    skipped = []
    for content_hash, entry in sorted(manifest["transcripts"].items(), key=lambda item: item[1].get("meeting_date", "")):
        transcript_path = root / entry["transcript_path"]
        summary_path = root / entry["expected_summary_path"]
        if not transcript_path.exists():
            entry["status"] = "missing_transcript"
            continue
        if summary_path.exists() or entry.get("status") in {"validated", "summarized"}:
            skipped.append({"content_sha256": content_hash, "reason": "summary_exists_or_already_processed"})
            if summary_path.exists() and entry.get("status") == "pending":
                entry["status"] = "summarized"
            continue
        if entry.get("status") == "packet_ready" and entry.get("packet_path") and (root / entry["packet_path"]).exists():
            skipped.append({"content_sha256": content_hash, "reason": "packet_already_ready"})
            continue
        entry["status"] = "packet_ready"
        entry["run_id"] = run_id
        packet = build_packet(root, transcript_path, entry, run_id)
        packet_path = paths["packets"] / f"{run_id}_{content_hash[:12]}.json"
        write_json(packet_path, packet)
        entry["packet_path"] = normalized_relpath(packet_path, root)
        packets.append({"path": normalized_relpath(packet_path, root), "title": entry["title"]})

    write_json(paths["manifest"], manifest)
    report = {
        "run_id": run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cutoff_date": cutoff.isoformat(),
        "business_days": business_days,
        "sources": sources,
        "imported": imported,
        "packets": packets,
        "skipped": skipped,
        "manifest_path": normalized_relpath(paths["manifest"], root),
    }
    report_path = paths["runs"] / f"{run_id}.json"
    write_json(report_path, report)
    report["report_path"] = normalized_relpath(report_path, root)
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Transcript pipeline prepare run: {run_id}")
        print(f"Packets ready: {len(packets)}")
        print(f"Report: {report['report_path']}")
    return report


def required_summary_markers(packet: dict[str, Any]) -> list[str]:
    markers = ["Source Transcript", "Transcript SHA256", "Pipeline Run ID", "Routed Updates", "Key Evidence"]
    if packet["classification_hints"].get("manager_mode_required"):
        markers.extend(["Ways of Working", "Manager profile", "Stakeholder dynamics", "TASK_MASTER"])
    if packet["classification_hints"].get("partner_customer_mode_required"):
        markers.extend(["Partner/client", "Access", "Commercial Risk"])
    return markers


def marker_present(summary_text: str, marker: str) -> bool:
    def normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    return normalize(marker) in normalize(summary_text)


def validate(root: Path, run_id: str, json_output: bool) -> dict[str, Any]:
    paths = repo_paths(root)
    manifest = load_manifest(paths["manifest"])
    packets = sorted(paths["packets"].glob(f"{run_id}_*.json"))
    results = []
    for packet_path in packets:
        packet = read_json(packet_path, {})
        transcript = packet.get("transcript", {})
        content_hash = transcript.get("content_sha256", "")
        summary_path = root / transcript.get("expected_summary_path", "")
        errors = []
        if not summary_path.exists():
            errors.append("missing_summary")
            summary_text = ""
        else:
            summary_text = summary_path.read_text(encoding="utf-8", errors="replace")
            for marker in required_summary_markers(packet):
                if not marker_present(summary_text, marker):
                    errors.append(f"missing_marker:{marker}")
            if content_hash and content_hash not in summary_text:
                errors.append("missing_source_hash")
        status = "validated" if not errors else "validation_failed"
        entry = manifest["transcripts"].get(content_hash)
        if entry is not None:
            entry["status"] = status
            entry["last_validation"] = {
                "run_id": run_id,
                "validated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "errors": errors,
            }
        results.append(
            {
                "packet_path": normalized_relpath(packet_path, root),
                "summary_path": transcript.get("expected_summary_path", ""),
                "content_sha256": content_hash,
                "status": status,
                "errors": errors,
            }
        )
    write_json(paths["manifest"], manifest)
    report = {"run_id": run_id, "results": results, "ok": all(not item["errors"] for item in results)}
    report_path = paths["runs"] / f"{run_id}_validation.json"
    write_json(report_path, report)
    report["report_path"] = normalized_relpath(report_path, root)
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Validation run: {run_id}")
        print(f"OK: {report['ok']}")
        print(f"Report: {report['report_path']}")
    return report


def extract_summary_bullets(summary_text: str, max_items: int = 3) -> list[str]:
    in_summary = False
    bullets = []
    for line in summary_text.splitlines():
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if in_summary and line.strip().startswith("- "):
            bullets.append(line.strip()[2:])
        if len(bullets) >= max_items:
            break
    return bullets


def extract_action_items(summary_text: str, max_items: int = 5) -> list[str]:
    lines = summary_text.splitlines()
    actions = []
    in_actions = False
    for line in lines:
        if line.strip() == "## Action Items":
            in_actions = True
            continue
        if in_actions and line.startswith("## "):
            break
        if in_actions and line.startswith("|") and "---" not in line and "Due Date" not in line:
            cells = split_cells(line)
            if len(cells) >= 3:
                actions.append(f"{cells[1]}: {cells[2]} ({cells[0]})")
        if len(actions) >= max_items:
            break
    return actions


def validated_summary_paths(root: Path, limit: int) -> list[Path]:
    paths = repo_paths(root)
    manifest = load_manifest(paths["manifest"])
    candidates = []
    for entry in manifest["transcripts"].values():
        if entry.get("status") != "validated":
            continue
        relpath = entry.get("expected_summary_path")
        if not relpath:
            continue
        summary_path = root / relpath
        if not summary_path.exists():
            continue
        last_validation = entry.get("last_validation") or {}
        candidates.append(
            (
                entry.get("meeting_date", ""),
                last_validation.get("validated_at", ""),
                summary_path.stat().st_mtime,
                summary_path,
            )
        )
    return [item[-1] for item in sorted(candidates, reverse=True)[:limit]]


def recent(root: Path, limit: int, markdown: bool) -> str:
    summaries = validated_summary_paths(root, limit)
    blocks = []
    for summary_path in summaries:
        text = summary_path.read_text(encoding="utf-8", errors="replace")
        title = summary_path.stem
        date_match = re.search(r"\*\*Date\*\*:\s*(.+)", text)
        participants_match = re.search(r"\*\*Participants\*\*:\s*(.+)", text)
        bullets = extract_summary_bullets(text)
        actions = extract_action_items(text)
        if markdown:
            block = [f"- **{title}**"]
            block.append(f"  - **Date**: {date_match.group(1) if date_match else 'Unknown'}")
            block.append(f"  - **Participants**: {participants_match.group(1) if participants_match else 'Unknown'}")
            block.append("  - **Summary**:")
            block.extend(f"    - {bullet}" for bullet in bullets)
            block.append("  - **Action Items**:")
            block.extend(f"    - {action}" for action in (actions or ["None captured"]))
            blocks.append("\n".join(block))
        else:
            blocks.append(title)
    output = "\n".join(blocks)
    print(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Beats PM transcript pipeline")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repo root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--business-days", type=int, default=10)
    prepare_parser.add_argument("--json", action="store_true")
    prepare_parser.add_argument("--skip-import", action="store_true", help="Skip bridge imports; useful for tests/debugging")
    prepare_parser.add_argument(
        "--quill-mode",
        choices=("bridge", "native-mcp"),
        default="bridge",
        help="Use the stdio bridge or confirm that native Quill tools already staged transcripts",
    )

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-id", required=True)
    validate_parser.add_argument("--json", action="store_true")

    recent_parser = subparsers.add_parser("recent")
    recent_parser.add_argument("--limit", type=int, default=5)
    recent_parser.add_argument("--md", action="store_true")

    args = parser.parse_args()
    root = Path(args.repo).expanduser().resolve()
    if args.command == "prepare":
        prepare(
            root,
            args.business_days,
            args.json,
            skip_import=args.skip_import,
            quill_mode=args.quill_mode,
        )
    elif args.command == "validate":
        report = validate(root, args.run_id, args.json)
        return 0 if report["ok"] else 1
    elif args.command == "recent":
        recent(root, args.limit, args.md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
