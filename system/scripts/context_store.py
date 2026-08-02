#!/usr/bin/env python3
"""Archive full local context payloads and return compact, retrievable views."""

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
STORE_REL = Path(".beats/context")
SIGNAL_RE = re.compile(
    r"error|warning|warn|failed|failure|exception|denied|blocked|security|"
    r"\b\d+\s+(?:files?|tests?|matches?|errors?|warnings?|passed|failed)\b|"
    r"(?:^|\s)(?:[\w.-]+/)+[\w.-]+(?::\d+)?",
    re.IGNORECASE,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def estimate_tokens(data: bytes) -> int:
    return (len(data) + 3) // 4


def _store_paths(root: Path, digest: str) -> tuple[Path, Path]:
    base = root / STORE_REL
    return base / "raw" / f"{digest}.blob", base / "records" / f"ctx-{digest[:16]}.json"


def archive_bytes(
    data: bytes,
    *,
    root: Path = ROOT,
    source: str,
    producing_command: str,
    source_type: str = "tool-result",
) -> dict[str, Any]:
    """Persist bytes without rewriting an existing raw object."""
    digest = hashlib.sha256(data).hexdigest()
    raw_path, record_path = _store_paths(root, digest)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    if not raw_path.exists():
        raw_path.write_bytes(data)
    record = {
        "schema_version": 1,
        "id": f"ctx-{digest[:16]}",
        "sha256": digest,
        "source": source,
        "source_type": source_type,
        "captured_at": utc_now(),
        "producing_command": producing_command,
        "bytes": len(data),
        "estimated_tokens": estimate_tokens(data),
        "raw_path": raw_path.relative_to(root).as_posix(),
        "captures": [
            {
                "source": source,
                "source_type": source_type,
                "captured_at": utc_now(),
                "producing_command": producing_command,
            }
        ],
    }
    if record_path.exists():
        prior = json.loads(record_path.read_text(encoding="utf-8"))
        capture = record["captures"][0]
        captures = prior.setdefault("captures", [])
        if not any(
            item.get("source") == capture["source"]
            and item.get("producing_command") == capture["producing_command"]
            for item in captures
        ):
            captures.append(capture)
            record_path.write_text(json.dumps(prior, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = prior
    else:
        record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def archive_file(
    path: Path,
    *,
    root: Path = ROOT,
    producing_command: str,
    source_type: str = "tool-result",
) -> dict[str, Any]:
    path = path.resolve()
    return archive_bytes(
        path.read_bytes(),
        root=root,
        source=str(path),
        producing_command=producing_command,
        source_type=source_type,
    )


def load_record(context_id: str, *, root: Path = ROOT) -> dict[str, Any]:
    if not re.fullmatch(r"ctx-[0-9a-f]{16}", context_id):
        raise ValueError(f"Invalid context ID: {context_id}")
    path = root / STORE_REL / "records" / f"{context_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Unknown context ID: {context_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def retrieve_bytes(context_id: str, *, root: Path = ROOT) -> bytes:
    record = load_record(context_id, root=root)
    raw_path = (root / record["raw_path"]).resolve()
    expected_root = (root / STORE_REL / "raw").resolve()
    if not raw_path.is_relative_to(expected_root):
        raise ValueError("Stored raw path escapes the context store")
    data = raw_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError(f"Hash mismatch for {context_id}")
    return data


def compact_view(context_id: str, *, root: Path = ROOT, max_chars: int = 4000) -> dict[str, Any]:
    """Return a bounded view while retaining deterministic raw retrieval."""
    if max_chars < 400:
        raise ValueError("max_chars must be at least 400")
    record = load_record(context_id, root=root)
    text = retrieve_bytes(context_id, root=root).decode("utf-8", errors="replace")
    lines = text.splitlines()
    signal_lines = [
        {"line": number, "text": line[:500]}
        for number, line in enumerate(lines, start=1)
        if SIGNAL_RE.search(line)
    ][:50]
    selected: list[tuple[int, str]] = []
    selected_numbers = set()
    for number in list(range(1, min(len(lines), 12) + 1)) + [item["line"] for item in signal_lines] + list(
        range(max(1, len(lines) - 7), len(lines) + 1)
    ):
        if number not in selected_numbers and 1 <= number <= len(lines):
            selected.append((number, lines[number - 1]))
            selected_numbers.add(number)
    rendered: list[str] = []
    rendered_numbers = set()
    used = 0
    for number, line in selected:
        candidate = f"L{number}: {line}\n"
        if used + len(candidate) > max_chars:
            break
        rendered.append(candidate)
        rendered_numbers.add(number)
        used += len(candidate)
    return {
        "schema_version": 1,
        "id": context_id,
        "sha256": record["sha256"],
        "source": record["source"],
        "source_type": record["source_type"],
        "producing_command": record["producing_command"],
        "bytes": record["bytes"],
        "estimated_tokens": record["estimated_tokens"],
        "line_count": len(lines),
        "signals": signal_lines,
        "view": "".join(rendered).rstrip(),
        "truncated": len(rendered_numbers) < len(lines),
        "retrieval": f"python3 system/scripts/context_store.py retrieve {context_id}",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="action", required=True)
    archive = subparsers.add_parser("archive")
    archive.add_argument("source", type=Path)
    archive.add_argument("--command", required=True)
    archive.add_argument("--source-type", default="tool-result")
    preview = subparsers.add_parser("preview")
    preview.add_argument("context_id")
    preview.add_argument("--max-chars", type=int, default=4000)
    retrieve = subparsers.add_parser("retrieve")
    retrieve.add_argument("context_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.action == "archive":
            payload = archive_file(
                args.source,
                root=root,
                producing_command=args.command,
                source_type=args.source_type,
            )
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.action == "preview":
            print(json.dumps(compact_view(args.context_id, root=root, max_chars=args.max_chars), indent=2, sort_keys=True))
        else:
            sys.stdout.buffer.write(retrieve_bytes(args.context_id, root=root))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"context-store: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
