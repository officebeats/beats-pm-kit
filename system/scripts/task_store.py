#!/usr/bin/env python3
"""Canonical Markdown task storage for Beats PM Kit.

Individual, human-readable Markdown task notes are the source of truth.
TASK_MASTER.md is a generated navigation index over those notes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
TASKS_REL = Path("5. Trackers/tasks")
TASK_MASTER_REL = Path("5. Trackers/TASK_MASTER.md")
MANAGED_START = "<!-- beats-task-index:start -->"
MANAGED_END = "<!-- beats-task-index:end -->"
TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")


@dataclass
class TaskRecord:
    task_id: str
    title: str
    path: Path
    status: str = "inbox"
    lane: str = "Triage"
    owner: str = "Unassigned"
    workstream: str = ""
    due: str = ""
    created: str = ""
    updated: str = ""
    source_refs: list[str] = field(default_factory=list)
    inferred_fields: list[str] = field(default_factory=list)
    body: str = ""


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def human_slug(value: str, fallback: str = "task") -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`#>]", "", value).lower()
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return (re.sub(r"-{2,}", "-", value)[:80].strip("-") or fallback)


def unique_task_path(root: Path, title: str, current: Path | None = None) -> Path:
    tasks_dir = root / TASKS_REL
    base = human_slug(title)
    candidate = tasks_dir / f"{base}.md"
    suffix = 2
    current_resolved = current.resolve() if current else None
    while candidate.exists() and candidate.resolve() != current_resolved:
        candidate = tasks_dir / f"{base}-{suffix}.md"
        suffix += 1
    return candidate


def _frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    metadata: dict[str, str | list[str]] = {}
    active_list = ""
    for raw in text[4:end].splitlines():
        if active_list and re.match(r"^\s+-\s+", raw):
            value = re.sub(r"^\s+-\s+", "", raw).strip().strip("\"'")
            current = metadata.setdefault(active_list, [])
            if isinstance(current, list):
                current.append(value)
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip().strip("\"'")
        if value:
            metadata[key] = value
            active_list = ""
        else:
            metadata[key] = []
            active_list = key
    return metadata, text[end + 5 :]


def _legacy_field(text: str, label: str) -> str:
    match = re.search(rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _title_from_text(path: Path, text: str, metadata: dict[str, str | list[str]]) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if match:
        value = match.group(1).strip()
        value = re.sub(r"^[A-Z][A-Z0-9]+-\d{3,}[a-z]?\s*[—:-]\s*", "", value)
        return value.strip()
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def parse_task(path: Path) -> TaskRecord | None:
    text = _read(path)
    if not text.strip():
        return None
    metadata, body = _frontmatter(text)
    task_id_value = metadata.get("task_id", "")
    task_id = str(task_id_value) if not isinstance(task_id_value, list) else ""
    if not task_id:
        task_id = _legacy_field(text, "Internal ID")
    if not task_id:
        match = TASK_ID_RE.search(text[:500]) or TASK_ID_RE.search(path.stem)
        task_id = match.group(0) if match else ""
    if not task_id:
        return None

    def scalar(key: str, legacy: str, default: str = "") -> str:
        value = metadata.get(key, "")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return _legacy_field(text, legacy) or default

    refs = metadata.get("source_refs", [])
    source_refs = [str(item) for item in refs] if isinstance(refs, list) else ([str(refs)] if refs else [])
    inferred = metadata.get("inferred_fields", [])
    inferred_fields = [str(item) for item in inferred] if isinstance(inferred, list) else ([str(inferred)] if inferred else [])
    return TaskRecord(
        task_id=task_id,
        title=_title_from_text(path, body, metadata),
        path=path,
        status=scalar("status", "Status", "inbox"),
        lane=scalar("lane", "Lane", "Triage"),
        owner=scalar("owner", "Owner", "Unassigned"),
        workstream=scalar("workstream", "Workstream"),
        due=scalar("due", "Due"),
        created=scalar("created", "Created"),
        updated=scalar("updated", "Last Updated"),
        source_refs=source_refs,
        inferred_fields=inferred_fields,
        body=body,
    )


def iter_tasks(root: Path = ROOT) -> Iterable[TaskRecord]:
    tasks_dir = root / TASKS_REL
    if not tasks_dir.exists():
        return
    for path in sorted(tasks_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        task = parse_task(path)
        if task is not None:
            yield task


def task_by_id(root: Path, task_id: str) -> TaskRecord | None:
    return next((task for task in iter_tasks(root) if task.task_id == task_id), None)


def _yaml_value(value: str) -> str:
    if not value:
        return "''"
    if re.fullmatch(r"[A-Za-z0-9_. /:@+-]+", value):
        return value
    return "'" + value.replace("'", "''") + "'"


def render_task(record: TaskRecord, *, summary: str, context: str, next_action: str, source: str) -> str:
    today = record.created or dt.date.today().isoformat()
    updated = record.updated or today
    lines = [
        "---",
        f"title: {_yaml_value(record.title)}",
        f"task_id: {_yaml_value(record.task_id)}",
        f"status: {_yaml_value(record.status)}",
        f"lane: {_yaml_value(record.lane)}",
        f"owner: {_yaml_value(record.owner)}",
        f"workstream: {_yaml_value(record.workstream)}",
        f"due: {_yaml_value(record.due)}",
        f"created: {_yaml_value(today)}",
        f"updated: {_yaml_value(updated)}",
        "source_refs:",
        *[f"  - {_yaml_value(ref)}" for ref in record.source_refs],
        "inferred_fields:",
        *[f"  - {_yaml_value(field)}" for field in record.inferred_fields],
        "---",
        "",
        f"# {record.title}",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## Context",
        "",
        context,
        "",
        "## Success and scope",
        "",
        "- Success criteria need confirmation during triage.",
        "- Keep the task scoped to the outcome described above.",
        "",
        "## Next actions",
        "",
        f"- [ ] {next_action.rstrip('.')}.",
        "",
        "## Evidence",
        "",
        *([f"- `{ref}`" for ref in record.source_refs] or ["- Source reference pending."]),
        "",
        "## Progress",
        "",
        "| Date | Source | Update |",
        "|:---|:---|:---|",
        f"| {updated} | {source} | {summary} |",
        "",
        "## Decisions",
        "",
        "- No decision recorded yet.",
    ]
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


def render_index(tasks: Iterable[TaskRecord]) -> str:
    ordered = sorted(tasks, key=lambda task: (task.status.lower() in {"done", "cancelled", "✅ done"}, task.due or "9999-99-99", task.title.lower()))
    rows = [
        MANAGED_START,
        "> Generated from the readable Markdown notes in `5. Trackers/tasks/`. Edit the task note, then rebuild this index.",
        "",
        "| Task | Owner | Due | Status |",
        "|:---|:---|:---|:---|",
    ]
    for task in ordered:
        relative = Path("tasks") / task.path.name
        rows.append(
            f"| [{_escape_table(task.title)}]({relative.as_posix().replace(' ', '%20')}) "
            f"| {_escape_table(task.owner)} | {_escape_table(task.due or 'TBD')} | {_escape_table(task.status)} |"
        )
    rows.append(MANAGED_END)
    return "\n".join(rows)


def rebuild_task_master(root: Path = ROOT) -> Path:
    path = root / TASK_MASTER_REL
    existing = _read(path)
    title_block = "---\ntitle: Task Master\n---\n\n# Task Master\n\n"
    managed = render_index(iter_tasks(root))
    if MANAGED_START in existing and MANAGED_END in existing:
        pattern = re.compile(rf"{re.escape(MANAGED_START)}.*?{re.escape(MANAGED_END)}", re.DOTALL)
        updated = pattern.sub(managed, existing, count=1)
    else:
        # Preserve manual sections while replacing the first legacy task table.
        content = existing
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end >= 0:
                content = content[end + 5 :].lstrip()
        content = re.sub(r"^#\s+.*?\n+", "", content, count=1, flags=re.MULTILINE)
        legacy_table = re.compile(
            r"(?:^\|\s*ID\s*\|\s*Task\s*\|.*?\n)(?:^\|.*\|\s*$\n?)+",
            flags=re.MULTILINE,
        )
        content = legacy_table.sub("", content, count=1).strip()
        updated = title_block + managed + (("\n\n" + content) if content else "")
    _write(path, updated)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("rebuild", help="Rebuild Task Master from canonical task notes")
    commands.add_parser("list", help="List canonical task notes")
    show = commands.add_parser("show", help="Show one task by its internal ID")
    show.add_argument("task_id")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "rebuild":
        path = rebuild_task_master(root)
        payload = {"ok": True, "task_count": len(list(iter_tasks(root))), "task_master": path.relative_to(root).as_posix()}
    elif args.command == "list":
        payload = [
            {"task_id": task.task_id, "title": task.title, "status": task.status, "path": task.path.relative_to(root).as_posix()}
            for task in iter_tasks(root)
        ]
    else:
        task = task_by_id(root, args.task_id)
        if task is None:
            parser.error(f"Unknown task: {args.task_id}")
        payload = {
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status,
            "path": task.path.relative_to(root).as_posix(),
        }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, list):
        for item in payload:
            print(f"- {item['title']} [{item['status']}] — {item['path']}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
