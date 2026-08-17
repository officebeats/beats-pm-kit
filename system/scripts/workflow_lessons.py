#!/usr/bin/env python3
"""Per-workflow lessons capture with a bounded FIFO ledger.

Lessons record project-specific failure notes and gotchas per workflow, so
they live under the gitignored ``.beats/lessons/`` directory, never in the
tracked ``.agent/workflows/`` tree. Each file is a plain bullet list:

    - 2026-08-17: Slack chunk caps hid results; pre-chunk windows over 5 days.

Files keep at most ``MAX_LESSONS`` entries; appending beyond the cap drops the
oldest bullet first.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LESSONS_DIR = Path(".beats") / "lessons"
MAX_LESSONS = 10
_BULLET = re.compile(r"^- (\d{4}-\d{2}-\d{2}): (.+)$")


def _slug(workflow: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", workflow.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"invalid workflow name: {workflow!r}")
    return slug


def lessons_path(root: Path, workflow: str) -> Path:
    return root / LESSONS_DIR / f"{_slug(workflow)}.md"


def load_lessons(root: Path, workflow: str) -> list[dict]:
    """Return lessons as ``[{"date": ..., "text": ...}, ...]``, oldest first."""
    path = lessons_path(root, workflow)
    if not path.exists():
        return []
    lessons = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _BULLET.match(line.strip())
        if match:
            lessons.append({"date": match.group(1), "text": match.group(2)})
    return lessons


def append_lesson(root: Path, workflow: str, text: str, *, date: str | None = None) -> Path:
    """Append one dated bullet, dropping the oldest entries beyond the cap."""
    text = " ".join(text.split())
    if not text:
        raise ValueError("lesson text must not be empty")
    when = date or dt.date.today().isoformat()
    lessons = load_lessons(root, workflow)
    lessons.append({"date": when, "text": text})
    lessons = lessons[-MAX_LESSONS:]
    path = lessons_path(root, workflow)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(f"- {item['date']}: {item['text']}" for item in lessons)
    path.write_text(body + "\n", encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="Kit root override")
    sub = parser.add_subparsers(dest="command", required=True)

    cmd_append = sub.add_parser("append", help="Append one lesson bullet")
    cmd_append.add_argument("workflow", help="Workflow name, e.g. beats-slack")
    cmd_append.add_argument("--text", required=True, help="Lesson text")

    cmd_list = sub.add_parser("list", help="List lessons for a workflow")
    cmd_list.add_argument("workflow", help="Workflow name, e.g. beats-slack")
    cmd_list.add_argument("--json", action="store_true", help="Emit JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "append":
        path = append_lesson(args.root, args.workflow, args.text)
        print(str(path))
        return 0
    lessons = load_lessons(args.root, args.workflow)
    if args.json:
        print(json.dumps({"workflow": _slug(args.workflow), "lessons": lessons}, indent=2))
    else:
        for item in lessons:
            print(f"- {item['date']}: {item['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
