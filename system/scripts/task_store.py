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
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.scripts import markdown_humanizer


TASKS_REL = Path("5. Trackers/tasks")
TASK_MASTER_REL = Path("5. Trackers/TASK_MASTER.md")
WORKSTREAMS_REL = Path("5. Trackers/workstreams")
TASK_INDEX_JSON_REL = Path("5. Trackers/.task-index.json")
TRELLO_HOTLIST_REL = Path("5. Trackers/TRELLO_HOTLIST.md")
TRIAGE_SUMMARY_REL = Path("5. Trackers/TRIAGE_SUMMARY.md")
MANUAL_ARCHIVE_REL = Path("5. Trackers/archive/TASK_MASTER_MANUAL_ARCHIVE.md")
MANAGED_START = "<!-- beats-task-index:start -->"
MANAGED_END = "<!-- beats-task-index:end -->"
TRELLO_HOTLIST_MARKERS = ("<!-- TRELLO_HOTLIST:BEGIN -->", "<!-- TRELLO_HOTLIST:END -->")
TRIAGE_SUMMARY_MARKERS = ("<!-- TASK_TRIAGE_SUMMARY:BEGIN -->", "<!-- TASK_TRIAGE_SUMMARY:END -->")
TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")
CLOSED_STATUSES = {"done", "cancelled", "✅ done"}
_GENERATED_LINE_RE = re.compile(r"^> Generated: .*$", flags=re.MULTILINE)


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
    priority: str = ""
    tags: list[str] = field(default_factory=list)
    body: str = ""


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _write(path: Path, text: str) -> None:
    markdown_humanizer.write_generated_markdown(path, text)


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


def _unescape_yaml_scalar(raw: str) -> str:
    """Undo YAML scalar quoting, including doubled-quote escapes.

    A bare `.strip("\"'")` only removes the outer wrapping quotes and leaves
    an internal `''` escape (YAML single-quoted style) doubled forever — each
    read-then-rewrite round trip compounds it further. Detect the wrapping
    quote style first, then unescape only the matching internal sequence.
    """
    if len(raw) >= 2 and raw[0] == raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1].replace('\\"', '"')
    return raw.strip("\"'")


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
            value = _unescape_yaml_scalar(re.sub(r"^\s+-\s+", "", raw).strip())
            current = metadata.setdefault(active_list, [])
            if isinstance(current, list):
                current.append(value)
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", raw)
        if not match:
            continue
        key, value = match.groups()
        value = _unescape_yaml_scalar(value.strip())
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

_PRIORITY_SLUGS = (
    ("do first", "do-first"),
    ("do-first", "do-first"),
    ("schedule", "schedule"),
    ("quick win", "quick-win"),
    ("quick-win", "quick-win"),
    ("monitor", "monitor"),
)


def _priority_slug(raw: str) -> str:
    lowered = raw.strip().lower()
    for needle, slug in _PRIORITY_SLUGS:
        if needle in lowered:
            return slug
    return ""


def _lane_slug(raw: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    return lowered


def _status_slug(raw: str) -> str:
    """Reduce a status value to its leading phrase, slugified.

    Body ``> **Status:**`` lines in this vault are sometimes a clean label
    (``In Progress``) and sometimes a label followed by a narrative
    continuation after an em-dash or hyphen (``Overdue — ML-1917 remains a
    Known Reasoning Issue...``). Frontmatter is a queryable index over the
    body, not a replacement for it, so only the leading label — already a
    self-contained phrase in the source text — is kept; the full narrative
    stays intact and unedited in the body. This is truncation at an existing
    boundary, not reinterpretation: no status is ever guessed or upgraded.
    """
    leading = re.split(r"\s+[—-]\s+", raw.strip(), maxsplit=1)[0]
    leading = re.sub(r"^[^\w]+", "", leading).strip()
    return _lane_slug(leading)


def _normalize_iso_date(raw: str) -> str:
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", raw)
    return match.group(1) if match else ""


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

    lane_value = scalar("lane", "Lane", "Triage")
    workstream_value = scalar("workstream", "Workstream")
    priority_value = scalar("priority", "Eisenhower")
    if priority_value and priority_value not in {slug for _, slug in _PRIORITY_SLUGS}:
        priority_value = _priority_slug(priority_value)

    tag_values = metadata.get("tags", [])
    if isinstance(tag_values, list) and tag_values:
        tags = [str(item) for item in tag_values]
    else:
        tags = ["beats-task"]
        workstream_slug = _lane_slug(workstream_value)
        if workstream_slug:
            tags.append(workstream_slug)
        lane_slug = _lane_slug(lane_value)
        if lane_slug:
            tags.append(lane_slug)

    return TaskRecord(
        task_id=task_id,
        title=_title_from_text(path, body, metadata),
        path=path,
        status=scalar("status", "Status", "inbox"),
        lane=lane_value,
        owner=scalar("owner", "Owner", "Unassigned"),
        workstream=workstream_value,
        due=scalar("due", "Due"),
        created=scalar("created", "Created"),
        updated=scalar("updated", "Last Updated"),
        source_refs=source_refs,
        inferred_fields=inferred_fields,
        priority=priority_value,
        tags=tags,
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


def _yaml_scalar_or_null(value: str) -> str:
    if not value or value.strip().lower() in {"unassigned", "tbd"}:
        return "null"
    return _yaml_value(value.strip())


def _tags_or_default(tags: list[str], workstream: str, lane: str) -> list[str]:
    if tags:
        return tags
    result = ["beats-task"]
    workstream_slug = _lane_slug(workstream)
    if workstream_slug:
        result.append(workstream_slug)
    lane_slug = _lane_slug(lane)
    if lane_slug:
        result.append(lane_slug)
    return result


def render_task(record: TaskRecord, *, summary: str, context: str, next_action: str, source: str) -> str:
    today = record.created or dt.date.today().isoformat()
    updated = record.updated or today
    tags = _tags_or_default(record.tags, record.workstream, record.lane)
    due_iso = _normalize_iso_date(record.due)
    lines = [
        "---",
        f"title: {_yaml_value(record.title)}",
        f"task_id: {_yaml_value(record.task_id)}",
        f"status: {_yaml_value(record.status)}",
        f"lane: {_yaml_value(record.lane)}",
        f"workstream: {_yaml_value(record.workstream)}",
        f"created: {_yaml_value(today)}",
        f"updated: {_yaml_value(updated)}",
        "source_refs:",
        *[f"  - {_yaml_value(ref)}" for ref in record.source_refs],
        "inferred_fields:",
        *[f"  - {_yaml_value(field)}" for field in record.inferred_fields],
        f"tags: [{', '.join(tags)}]" if tags else "tags: []",
        f"priority: {_yaml_scalar_or_null(record.priority)}",
        f"due: {_yaml_scalar_or_null(due_iso)}",
        f"owner: {_yaml_scalar_or_null(record.owner)}",
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


def _is_closed(task: TaskRecord) -> bool:
    return task.status.strip().lower() in CLOSED_STATUSES


def _due_key(task: TaskRecord) -> str:
    return _normalize_iso_date(task.due) or "9999-99-99"


def _wikilink_alias(value: str) -> str:
    return re.sub(r"\s+", " ", value).replace("|", "/").replace("[", "").replace("]", "").strip()


def workstream_title(root: Path, slug: str) -> str:
    """Human title for a workstream slug, preferring the workstream note's H1."""
    if not slug:
        return "Unassigned"
    text = _read(root / WORKSTREAMS_REL / f"{slug}.md")
    if text:
        _, body = _frontmatter(text)
        match = re.search(r"^#\s+(.+?)\s*$", body, flags=re.MULTILINE)
        if match and "{{" not in match.group(1):
            return match.group(1)
    words = slug.replace("-", " ").strip()
    return words[:1].upper() + words[1:] if words else "Unassigned"


def _resume_lines(tasks: list[TaskRecord], today: str, titles: dict[str, str]) -> list[str]:
    """'Resume Here' bullets: overdue work first, then the top today-lane task per workstream."""
    open_tasks = [task for task in tasks if not _is_closed(task)]
    lines: list[str] = []
    listed: set[str] = set()
    overdue = [
        task
        for task in open_tasks
        if task.status.strip().lower() == "overdue"
        or (_normalize_iso_date(task.due) and _normalize_iso_date(task.due) < today)
    ]
    for task in sorted(overdue, key=lambda task: (_due_key(task), task.title.lower())):
        due = _normalize_iso_date(task.due)
        reason = f"overdue since {due}" if due else "status is overdue"
        lines.append(f"- [[{task.path.stem}|{_wikilink_alias(task.title)}]] — {reason}")
        listed.add(task.task_id)
    today_lanes: dict[str, list[TaskRecord]] = {}
    for task in open_tasks:
        slug = _lane_slug(task.workstream)
        if slug and _lane_slug(task.lane) == "today":
            today_lanes.setdefault(slug, []).append(task)
    for slug in sorted(today_lanes, key=lambda slug: titles.get(slug, slug).lower()):
        top = min(today_lanes[slug], key=lambda task: (_due_key(task), task.title.lower()))
        if top.task_id in listed:
            continue
        lines.append(
            f"- [[{top.path.stem}|{_wikilink_alias(top.title)}]] — next up in {titles.get(slug, slug)} (today lane)"
        )
        listed.add(top.task_id)
    return lines[:10]


def render_index(tasks: Iterable[TaskRecord], root: Path = ROOT, *, today: str = "", generated: str = "") -> str:
    tasks = list(tasks)
    today = today or dt.date.today().isoformat()
    generated = generated or dt.datetime.now().isoformat(timespec="seconds")
    groups: dict[str, list[TaskRecord]] = {}
    for task in tasks:
        groups.setdefault(_lane_slug(task.workstream), []).append(task)
    titles = {slug: workstream_title(root, slug) for slug in groups}
    ordered_slugs = sorted(
        groups,
        key=lambda slug: (min(_due_key(task) for task in groups[slug]), titles[slug].lower()),
    )
    rows = [
        MANAGED_START,
        "> Generated from the readable Markdown notes in `5. Trackers/tasks/`. Edit the task note, then rebuild this index.",
        f"> Generated: {generated}",
        "",
        "## Resume Here",
        "",
    ]
    rows.extend(
        _resume_lines(tasks, today, titles)
        or ["- Nothing overdue and no today-lane workstream tasks. Pick from the tables below."]
    )
    for slug in ordered_slugs:
        heading = f"### [[{slug}|{titles[slug]}]]" if slug else "### Unassigned"
        rows.extend(["", heading, "", "| Task | Owner | Due | Status |", "|:---|:---|:---|:---|"])
        for task in sorted(groups[slug], key=lambda task: (_is_closed(task), _due_key(task), task.title.lower())):
            rows.append(
                f"| [[{task.path.stem}\\|{_wikilink_alias(task.title)}]] "
                f"| {_escape_table(task.owner)} | {_escape_table(task.due or 'TBD')} | {_escape_table(task.status)} |"
            )
    rows.append(MANAGED_END)
    return "\n".join(rows)


def _relocate_marked_section(root: Path, text: str, markers: tuple[str, str], target_rel: Path, label: str) -> str:
    """One-time migration: move a bridge-managed marker block into its own note, leaving a link."""
    begin, end = markers
    start = text.find(begin)
    if start < 0:
        return text
    stop = text.find(end, start)
    if stop < 0:
        return text
    stop += len(end)
    target = root / target_rel
    if not target.exists() or begin not in _read(target):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text[start:stop].rstrip() + "\n", encoding="utf-8")
    link = f"See [[{target_rel.stem}|{label}]]."
    return text[:start] + link + text[stop:]


def _relocate_manual_archive(root: Path, text: str) -> str:
    """One-time migration: park the stale manual sections in an archive note, leaving a link."""
    match = re.search(r"^## Friday Status Focus.*$", text, flags=re.MULTILINE)
    if not match:
        return text
    start = match.start()
    tail = re.search(r"^\*Source of truth:.*$", text, flags=re.MULTILINE)
    stop = tail.start() if tail and tail.start() > start else len(text)
    target = root / MANUAL_ARCHIVE_REL
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        header = (
            "---\ntitle: Task Master Manual Archive\n---\n\n"
            "# Task Master Manual Archive\n\n"
            "> Relocated verbatim from `5. Trackers/TASK_MASTER.md` to keep the Task Master index lean.\n\n"
        )
        target.write_text(header + text[start:stop].rstrip() + "\n", encoding="utf-8")
    link = f"See [[{MANUAL_ARCHIVE_REL.stem}|Task Master manual archive]] for the pre-refactor manual sections."
    return text[:start] + link + "\n\n" + text[stop:]


def _migrate_task_master_layout(root: Path, text: str) -> str:
    if not text:
        return text
    text = _relocate_marked_section(root, text, TRELLO_HOTLIST_MARKERS, TRELLO_HOTLIST_REL, "Trello Hotlist")
    text = _relocate_marked_section(root, text, TRIAGE_SUMMARY_MARKERS, TRIAGE_SUMMARY_REL, "Task Triage Summary")
    text = _relocate_manual_archive(root, text)
    text = re.sub(r"^> \*\*Last Updated:\*\*.*\n", "", text, flags=re.MULTILINE)
    return re.sub(r"\n{3,}", "\n\n", text)


def write_task_index_json(root: Path, tasks: list[TaskRecord]) -> Path:
    path = root / TASK_INDEX_JSON_REL
    payload = [
        {
            "task_id": task.task_id,
            "title": task.title,
            "workstream": task.workstream,
            "lane": task.lane,
            "status": task.status,
            "due": task.due,
            "owner": task.owner,
            "path": task.path.relative_to(root).as_posix(),
        }
        for task in sorted(tasks, key=lambda task: task.task_id)
    ]
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path


def rebuild_task_master(root: Path = ROOT) -> Path:
    path = root / TASK_MASTER_REL
    existing = _migrate_task_master_layout(root, _read(path))
    tasks = list(iter_tasks(root))
    title_block = "---\ntitle: Task Master\n---\n\n# Task Master\n\n"
    managed = render_index(tasks, root)
    if MANAGED_START in existing and MANAGED_END in existing:
        pattern = re.compile(rf"{re.escape(MANAGED_START)}.*?{re.escape(MANAGED_END)}", re.DOTALL)
        previous = pattern.search(existing).group(0)
        placeholder = "> Generated: -"
        if _GENERATED_LINE_RE.sub(placeholder, previous) == _GENERATED_LINE_RE.sub(placeholder, managed):
            managed = previous  # unchanged index: keep the existing timestamp so rebuilds stay idempotent
        updated = pattern.sub(lambda _: managed, existing, count=1)
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
    write_task_index_json(root, tasks)
    return path


def backfill_frontmatter(path: Path) -> bool:
    """Backfill missing frontmatter keys on an existing task note in place.

    Preserves every existing frontmatter key/value and the entire body verbatim;
    only inserts keys that are absent from frontmatter, evaluated independently
    so a note missing some but not all keys still gets the rest filled in.

    `status`/`lane`/`type` are backfilled from real evidence already in the file
    (frontmatter's own legacy body fields via `parse_task`, or the universal
    `task` note-type constant) — never fabricated. `workstream`/`program` have
    no such body-level fallback for legacy notes; when genuinely unknown they
    are written as explicit YAML `null` rather than omitted, so a Dataview
    query can surface "tasks missing a workstream" as a real, queryable gap
    instead of a silently absent key.

    Idempotent per key: re-running on an already-complete note is a no-op.
    """
    text = _read(path)
    if not text.strip() or not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end < 0:
        return False
    raw_frontmatter = text[4:end]
    existing_keys = set(re.findall(r"^([a-zA-Z_][a-zA-Z0-9_-]*):", raw_frontmatter, flags=re.MULTILINE))
    record = parse_task(path)
    if record is None:
        return False

    missing_new = {"tags", "priority", "due", "owner"} - existing_keys
    missing_legacy = {"status", "lane", "type", "workstream", "program"} - existing_keys
    if not missing_new and not missing_legacy:
        return False

    tags = _tags_or_default(record.tags, record.workstream, record.lane)
    due_iso = _normalize_iso_date(record.due)
    new_lines: list[str] = []
    if "status" in missing_legacy:
        new_lines.append(f"status: {_yaml_scalar_or_null(_status_slug(record.status) or record.status)}")
    if "lane" in missing_legacy:
        new_lines.append(f"lane: {_yaml_scalar_or_null(_lane_slug(record.lane) or record.lane)}")
    if "workstream" in missing_legacy:
        new_lines.append(f"workstream: {_yaml_scalar_or_null(record.workstream)}")
    if "program" in missing_legacy:
        new_lines.append("program: null")
    if "type" in missing_legacy:
        new_lines.append("type: task")
    if "tags" in missing_new:
        new_lines.append(f"tags: [{', '.join(tags)}]" if tags else "tags: []")
    if "priority" in missing_new:
        new_lines.append(f"priority: {_yaml_scalar_or_null(record.priority)}")
    if "due" in missing_new:
        new_lines.append(f"due: {_yaml_scalar_or_null(due_iso)}")
    if "owner" in missing_new:
        new_lines.append(f"owner: {_yaml_scalar_or_null(record.owner)}")

    updated = text[:end] + "\n" + "\n".join(new_lines) + text[end:]
    path.write_text(updated, encoding="utf-8")
    return True


def normalize_status_frontmatter(path: Path) -> bool:
    """Re-slug an existing `status:` frontmatter value if it still carries a
    narrative continuation (e.g. from an earlier /track run that copied the
    full body Status line verbatim). Truncates at the same boundary as
    `_status_slug`; never touches the body, never invents a status.
    Idempotent: a value that is already a clean slug is left untouched.
    """
    text = _read(path)
    if not text.strip() or not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end < 0:
        return False
    raw_frontmatter = text[4:end]
    match = re.search(r"^status:\s*(.+)$", raw_frontmatter, flags=re.MULTILINE)
    if not match:
        return False
    current = match.group(1).strip().strip("\"'")
    if current in {"null", ""}:
        return False
    slugged = _status_slug(current)
    if not slugged or slugged == current:
        return False
    new_frontmatter = raw_frontmatter[: match.start()] + f"status: {slugged}" + raw_frontmatter[match.end() :]
    updated = text[:4] + new_frontmatter + text[end:]
    path.write_text(updated, encoding="utf-8")
    return True


def normalize_all_status_frontmatter(root: Path = ROOT) -> list[str]:
    tasks_dir = root / TASKS_REL
    if not tasks_dir.exists():
        return []
    touched: list[str] = []
    for candidate in sorted(tasks_dir.glob("*.md")):
        if candidate.name.startswith("_"):
            continue
        if normalize_status_frontmatter(candidate):
            touched.append(candidate.relative_to(root).as_posix())
    return touched


def backfill_all_frontmatter(root: Path = ROOT) -> list[str]:
    tasks_dir = root / TASKS_REL
    if not tasks_dir.exists():
        return []
    touched: list[str] = []
    for candidate in sorted(tasks_dir.glob("*.md")):
        if candidate.name.startswith("_"):
            continue
        if backfill_frontmatter(candidate):
            touched.append(candidate.relative_to(root).as_posix())
    return touched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("rebuild", help="Rebuild Task Master from canonical task notes")
    commands.add_parser("list", help="List canonical task notes")
    show = commands.add_parser("show", help="Show one task by its internal ID")
    show.add_argument("task_id")
    commands.add_parser(
        "backfill-frontmatter",
        help="Append tags/priority/due/owner to every task note's frontmatter in place",
    )
    commands.add_parser(
        "normalize-status",
        help="Re-slug any status: frontmatter value that still carries a narrative continuation",
    )
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
    elif args.command == "backfill-frontmatter":
        touched = backfill_all_frontmatter(root)
        payload = {"ok": True, "updated": touched, "count": len(touched)}
    elif args.command == "normalize-status":
        touched = normalize_all_status_frontmatter(root)
        payload = {"ok": True, "updated": touched, "count": len(touched)}
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
