#!/usr/bin/env python3
"""Bounded, deterministic vault query CLI.

Lets agents query the big tracker/index files without reading them whole.
Every subcommand prints a one-line summary header (total matches vs shown)
followed by at most ``--limit`` compact result lines.

Subcommands:
    tasks   query per-task notes under ``5. Trackers/tasks/``
    labels  query the ``.beats/markdown-labels.json`` machine sidecar
    quotes  query the ``3. Meetings/quote-index.md`` table

All paths resolve relative to the repo root derived from this script's
location, matching sibling scripts. ``--root`` overrides it (used by tests).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TASKS_DIR = "5. Trackers/tasks"
LABELS_JSON = ".beats/markdown-labels.json"
QUOTE_INDEX = "3. Meetings/quote-index.md"

DEFAULT_LIMIT = 20
QUOTE_SNIPPET_CHARS = 100

HEADER_FIELD_RE = re.compile(r"^>\s*\*\*([A-Za-z ]+):\*\*\s*(.+?)\s*$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def fail(message: str) -> int:
    print(f"vault_query: {message}", file=sys.stderr)
    return 1


def norm(value: str) -> str:
    """Casefolded text with markdown emphasis stripped, for matching."""
    return value.replace("*", "").replace("`", "").casefold()


def contains(haystack: str, needle: str) -> bool:
    return norm(needle) in norm(haystack)


def matches_pattern(value: str, pattern: str) -> bool:
    """Glob match when the pattern has glob chars, else substring match."""
    if any(ch in pattern for ch in "*?["):
        return fnmatch.fnmatchcase(norm(value), pattern.casefold())
    return contains(value, pattern)


def print_summary(kind: str, shown: int, total: int, scanned: int) -> None:
    line = f"# {kind}: showing {shown} of {total} matches ({scanned} scanned)"
    if total > shown:
        line += " — narrow filters or raise --limit"
    print(line)


def frontmatter_value(text: str, key: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return ""
    field = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", match.group(1), re.MULTILINE)
    if not field:
        return ""
    return field.group(1).strip().strip("'\"")


def header_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for name, value in HEADER_FIELD_RE.findall(text):
        fields.setdefault(name.strip(), value.strip())
    return fields


def short(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > limit:
        return value[: limit - 1].rstrip() + "…"
    return value


# --- tasks -----------------------------------------------------------------


def load_tasks(root: Path) -> list[dict[str, str]]:
    tasks_dir = root / TASKS_DIR
    if not tasks_dir.is_dir():
        raise FileNotFoundError(f"tasks directory not found: {tasks_dir}")
    tasks = []
    for path in sorted(tasks_dir.rglob("*.md")):
        if path.name.startswith("_"):
            continue  # templates
        text = path.read_text(encoding="utf-8", errors="replace")
        fields = header_fields(text)
        task_id = frontmatter_value(text, "task_id")
        if not task_id and "Status" not in fields:
            continue  # draft/scratch note, not a task record
        title = frontmatter_value(text, "title").replace("''", "'")
        if not title:
            h1 = H1_RE.search(text)
            title = h1.group(1).strip() if h1 else path.stem
        tasks.append(
            {
                "id": task_id or path.stem,
                "title": title,
                "status": fields.get("Status", ""),
                "lane": fields.get("Lane", ""),
                "due": fields.get("Due", ""),
                "owner": fields.get("Owner", ""),
                "eisenhower": fields.get("Eisenhower", ""),
                "workstream": fields.get("Workstream", ""),
                "labels": fields.get("Labels", ""),
                "path": str(path.relative_to(root)),
                "text": text,
            }
        )
    return tasks


def cmd_tasks(args: argparse.Namespace) -> int:
    try:
        tasks = load_tasks(args.root)
    except (FileNotFoundError, OSError) as exc:
        return fail(str(exc))

    matched = []
    for task in tasks:
        if args.status and not contains(task["status"], args.status):
            continue
        if args.lane and not contains(task["lane"], args.lane):
            continue
        if args.workstream and not contains(task["workstream"], args.workstream):
            continue
        if args.priority and not (
            contains(task["eisenhower"], args.priority) or contains(task["labels"], args.priority)
        ):
            continue
        if args.owner and not contains(task["owner"], args.owner):
            continue
        if args.text and not (contains(task["title"], args.text) or contains(task["text"], args.text)):
            continue
        matched.append(task)

    shown = matched[: args.limit]
    print_summary("tasks", len(shown), len(matched), len(tasks))
    for task in shown:
        status = short(task["status"].split(" — ")[0], 40) or "-"
        lane = task["lane"] or "-"
        due = task["due"] or "-"
        print(f"{task['id']} | {status} | lane={lane} due={due} | {short(task['title'], 70)} | {task['path']}")
    return 0


# --- labels ----------------------------------------------------------------


def load_labels(root: Path) -> list[dict]:
    labels_path = root / LABELS_JSON
    if not labels_path.is_file():
        raise FileNotFoundError(f"labels sidecar not found: {labels_path}")
    try:
        data = json.loads(labels_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"labels sidecar is not valid JSON: {labels_path} ({exc})") from exc
    notes = data.get("notes", []) if isinstance(data, dict) else []
    if not isinstance(notes, list):
        raise ValueError(f"labels sidecar has no usable 'notes' list: {labels_path}")
    return [note for note in notes if isinstance(note, dict)]


def cmd_labels(args: argparse.Namespace) -> int:
    try:
        notes = load_labels(args.root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        return fail(str(exc))

    matched = []
    for note in notes:
        label = str(note.get("label", ""))
        path = str(note.get("path", ""))
        if args.name and not matches_pattern(label, args.name):
            continue
        if args.path and not matches_pattern(path, args.path):
            continue
        if args.needs_review and not note.get("needs_review"):
            continue
        matched.append(note)

    shown = matched[: args.limit]
    print_summary("labels", len(shown), len(matched), len(notes))
    for note in shown:
        line = f"{short(str(note.get('label', '')) or '-', 80)} | {note.get('path', '-')}"
        if note.get("agent_ref"):
            line += f" | ref={note['agent_ref']}"
        if note.get("needs_review"):
            line += " | needs_review"
        print(line)
    return 0


# --- quotes ----------------------------------------------------------------


def parse_quote_rows(text: str) -> list[dict[str, str]]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue  # separator row
        if cells[0].casefold() == "date":
            continue  # header row
        row = {"date": cells[0], "speaker": "", "quote": "", "source": ""}
        if len(cells) >= 4:
            row["speaker"], row["quote"], row["source"] = cells[1], cells[2], cells[3]
        elif len(cells) == 3:
            row["quote"], row["source"] = cells[1], cells[2]
        elif len(cells) == 2:
            row["quote"] = cells[1]
        rows.append(row)
    return rows


def cmd_quotes(args: argparse.Namespace) -> int:
    index_path = args.root / QUOTE_INDEX
    if not index_path.is_file():
        return fail(f"quote index not found: {index_path}")
    rows = parse_quote_rows(index_path.read_text(encoding="utf-8", errors="replace"))

    matched = []
    for row in rows:
        if args.person and not (contains(row["speaker"], args.person) or contains(row["quote"], args.person)):
            continue
        if args.topic and not (contains(row["quote"], args.topic) or contains(row["source"], args.topic)):
            continue
        if args.date and not row["date"].startswith(args.date):
            continue
        matched.append(row)

    shown = matched[: args.limit]
    print_summary("quotes", len(shown), len(matched), len(rows))
    for row in shown:
        speaker = row["speaker"] or "-"
        print(f"{row['date']} | {speaker} | {short(row['quote'], QUOTE_SNIPPET_CHARS)} | {row['source']}")
    return 0


# --- CLI -------------------------------------------------------------------


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("limit must be >= 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vault_query.py",
        description="Bounded queries over vault trackers and indexes.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    tasks = sub.add_parser("tasks", help=f"query task notes under '{TASKS_DIR}/'")
    tasks.add_argument("--status", help="substring match on the Status field")
    tasks.add_argument("--lane", help="substring match on the Lane field")
    tasks.add_argument("--workstream", help="substring match on the Workstream field")
    tasks.add_argument("--priority", help="substring match on Eisenhower or Labels (e.g. P0)")
    tasks.add_argument("--owner", help="substring match on the Owner field")
    tasks.add_argument("--text", help="substring match on title or note body")
    tasks.add_argument("--limit", type=positive_int, default=DEFAULT_LIMIT)
    tasks.set_defaults(func=cmd_tasks)

    labels = sub.add_parser("labels", help=f"query the '{LABELS_JSON}' sidecar")
    labels.add_argument("--name", help="label glob (with * ? [) or substring")
    labels.add_argument("--path", help="note path glob or substring")
    labels.add_argument("--needs-review", action="store_true", help="only entries flagged needs_review")
    labels.add_argument("--limit", type=positive_int, default=DEFAULT_LIMIT)
    labels.set_defaults(func=cmd_labels)

    quotes = sub.add_parser("quotes", help=f"query '{QUOTE_INDEX}'")
    quotes.add_argument("--person", help="substring match on speaker (or quote text)")
    quotes.add_argument("--topic", help="substring match on quote text or source")
    quotes.add_argument("--date", help="date prefix, e.g. 2026-05")
    quotes.add_argument("--limit", type=positive_int, default=DEFAULT_LIMIT)
    quotes.set_defaults(func=cmd_quotes)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
