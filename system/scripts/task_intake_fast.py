#!/usr/bin/env python3
"""Fast raw-evidence intake for Beats PM task-manager snippets.

This path is intentionally shallow and local-only:

1. Save raw pasted evidence first.
2. Add a compact summary/routing read below the raw evidence.
3. Update the best matched task, or create an INBOX candidate task when the
   match is weak.
4. Defer expensive task-health triage to /day, /week, or explicit refresh.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from system.scripts import task_store


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
CACHE_REL = Path(".agent/cache/task_index.json")
TASK_MASTER_REL = Path("5. Trackers/TASK_MASTER.md")
TASKS_REL = Path("5. Trackers/tasks")
RAW_REL = Path("0. Incoming/raw")

TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")
DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
TASK_ROW_RE = re.compile(r"^\|(.+)\|$")

STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "because",
    "been",
    "but",
    "can",
    "context",
    "could",
    "for",
    "from",
    "have",
    "just",
    "like",
    "need",
    "needs",
    "not",
    "now",
    "that",
    "the",
    "their",
    "then",
    "there",
    "this",
    "was",
    "were",
    "what",
    "when",
    "with",
    "would",
    "you",
    "your",
}

ACTION_PATTERNS = (
    "action item",
    "add task",
    "blocked",
    "due",
    "follow up",
    "follow-up",
    "i'll",
    "i will",
    "need to",
    "needs to",
    "next",
    "schedule",
    "set up",
    "todo",
    "to do",
    "will",
)


@dataclass
class TaskIndexEntry:
    task_id: str
    title: str
    path: str
    owner: str = ""
    due: str = ""
    status: str = ""
    keywords: list[str] | None = None


@dataclass
class MatchResult:
    task: TaskIndexEntry | None
    confidence: float
    reason: str
    candidates: list[dict[str, Any]]


@dataclass
class IntakeResult:
    mode: str
    task_id: str
    display_label: str
    task_path: str
    source_note_path: str
    confidence: float
    summary: str
    next_action: str
    triage_deferred: bool
    candidates: list[dict[str, Any]]


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def strip_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("~~", "")
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def table_cells(line: str) -> list[str]:
    if not TASK_ROW_RE.match(line.strip()):
        return []
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if any(cell.startswith(":---") or cell == "---" for cell in cells):
        return []
    return cells


def extract_task_id(value: str) -> str:
    match = TASK_ID_RE.search(value or "")
    return match.group(0) if match else ""


def slugify(value: str, fallback: str = "task-intake") -> str:
    value = strip_markdown(value).lower()
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    value = re.sub(r"-{2,}", "-", value)
    return (value[:72].strip("-") or fallback)


def escape_table(value: str) -> str:
    return strip_markdown(value).replace("|", "\\|")


def tokens(value: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9-]{2,}", value.lower())
    return {word for word in words if word not in STOPWORDS and not word.isdigit()}


def first_meaningful_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\[?\d{1,2}:\d{2}", stripped):
            continue
        if stripped.startswith("http://") or stripped.startswith("https://"):
            continue
        return stripped
    return ""


def infer_summary(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if not collapsed:
        return "Raw intake captured for task-manager review."
    action_line = ""
    for line in text.splitlines():
        lowered = line.lower()
        if any(pattern in lowered for pattern in ACTION_PATTERNS):
            action_line = strip_markdown(line)
            break
    if action_line:
        return action_line[:220]
    sentence = re.split(r"(?<=[.!?])\s+", collapsed, maxsplit=1)[0]
    return strip_markdown(sentence)[:220]


def infer_next_action(text: str, summary: str) -> str:
    for line in text.splitlines():
        clean = strip_markdown(line)
        lowered = clean.lower()
        if any(pattern in lowered for pattern in ACTION_PATTERNS):
            return clean[:180]
    if summary:
        return f"Review intake signal: {summary[:140]}"
    return "Review raw intake signal and decide routing."


def infer_title(text: str, summary: str) -> str:
    combined = f"{summary}\n{text}".lower()
    if "abbey" in combined and ("iad" in combined or "indicia" in combined):
        return "IAD Indicia guideline tenant configuration"
    if "send data" in combined and "api" in combined:
        return "Generic Send Data API"
    if "cadalys" in combined or "zing" in combined:
        return "Cadalys Zing call prep"
    source = summary or first_meaningful_line(text) or "Task intake"
    words = [word for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*", source) if word.lower() not in STOPWORDS]
    title = " ".join(words[:5])
    return title or "Task intake"


def markdown_fence(text: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text.rstrip()}\n{fence}"


def relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def rel_from_task(task_path: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), task_path.parent.resolve())


def parse_task_master(root: Path) -> dict[str, TaskIndexEntry]:
    tasks: dict[str, TaskIndexEntry] = {}
    for task in task_store.iter_tasks(root):
        tasks[task.task_id] = TaskIndexEntry(
            task_id=task.task_id,
            title=task.title,
            path=str(task.path.resolve()),
            owner=task.owner,
            due=task.due,
            status=task.status,
            keywords=[],
        )
    return tasks


def section_body(text: str, heading_regex: str) -> str:
    match = re.search(rf"^{heading_regex}\s*(.*?)(?=^##\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def build_task_index(root: Path) -> dict[str, Any]:
    tasks = parse_task_master(root)
    for entry in tasks.values():
        task_text = read_text(Path(entry.path))
        status_line = ""
        for line in task_text.splitlines():
            if line.startswith("> **Status:**"):
                status_line = line
                break
        context = section_body(task_text, r"##\s+Context & Background")
        stakeholders = section_body(task_text, r"##\s+👥\s+Stakeholders")
        subtasks = section_body(task_text, r"##\s+✅\s+Subtasks")
        keyword_source = "\n".join([entry.title, entry.status, status_line, context[:1200], stakeholders, subtasks[:800]])
        entry.keywords = sorted(tokens(keyword_source))
    return {
        "schema_version": 1,
        "generated_at": now_local().isoformat(timespec="seconds"),
        "tasks": [asdict(entry) for entry in sorted(tasks.values(), key=lambda item: item.task_id)],
    }


def write_task_index(root: Path, index: dict[str, Any]) -> Path:
    cache_path = root / CACHE_REL
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return cache_path


def load_or_build_index(root: Path, rebuild: bool = False) -> dict[str, Any]:
    cache_path = root / CACHE_REL
    if not rebuild and cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    index = build_task_index(root)
    write_task_index(root, index)
    return index


def index_entries(index: dict[str, Any]) -> list[TaskIndexEntry]:
    return [TaskIndexEntry(**item) for item in index.get("tasks", [])]


def match_task(text: str, index: dict[str, Any], explicit_task_id: str = "") -> MatchResult:
    entries = index_entries(index)
    by_id = {entry.task_id: entry for entry in entries}
    ids = [explicit_task_id] if explicit_task_id else TASK_ID_RE.findall(text)
    for task_id in ids:
        if task_id in by_id:
            return MatchResult(by_id[task_id], 1.0, f"Explicit task id {task_id}", [{"task_id": task_id, "score": 1.0}])

    query_tokens = tokens(text)
    scored: list[tuple[float, TaskIndexEntry, list[str]]] = []
    for entry in entries:
        entry_tokens = set(entry.keywords or []) | tokens(entry.title) | tokens(entry.status)
        overlap = sorted(query_tokens & entry_tokens)
        if not overlap:
            continue
        title_overlap = query_tokens & tokens(entry.title)
        status_overlap = query_tokens & tokens(entry.status)
        score = len(overlap) + (2.0 * len(title_overlap)) + (0.5 * len(status_overlap))
        scored.append((score, entry, overlap[:12]))

    scored.sort(key=lambda item: item[0], reverse=True)
    candidates = [
        {
            "task_id": entry.task_id,
            "title": entry.title,
            "score": round(score, 2),
            "matched_terms": overlap,
        }
        for score, entry, overlap in scored[:5]
    ]
    if not scored:
        return MatchResult(None, 0.0, "No task-index keyword match", candidates)

    top_score, top_entry, overlap = scored[0]
    confidence = min(0.95, round(0.18 + (top_score / 18.0), 2))
    return MatchResult(top_entry, confidence, f"Matched task-index terms: {', '.join(overlap[:8])}", candidates)


def next_inbox_id(root: Path, prefix: str = "INBOX") -> str:
    existing: set[int] = set()
    for task in task_store.iter_tasks(root):
        match = re.fullmatch(rf"{re.escape(prefix)}-(\d{{3,}})", task.task_id)
        if match:
            existing.add(int(match.group(1)))
    next_number = 1
    while next_number in existing:
        next_number += 1
    return f"{prefix}-{next_number:03d}"


def save_source_note(
    root: Path,
    raw_text: str,
    source: str,
    title: str,
    summary: str,
    next_action: str,
    routing_lines: list[str],
    captured_at: dt.datetime,
) -> Path:
    day = captured_at.date().isoformat()
    digest = hashlib.sha256(raw_text.encode("utf-8", errors="replace")).hexdigest()[:10]
    filename = f"{day}_{slugify(title)}_{digest}.md"
    path = root / RAW_REL / filename
    yaml_title = title.replace("'", "''")
    yaml_source = source.replace("'", "''")
    body = "\n".join(
        [
            "---",
            f"title: '{yaml_title}'",
            "content_type: task-source",
            f"captured: {captured_at.isoformat(timespec='seconds')}",
            f"source: '{yaml_source}'",
            "---",
            "",
            f"# {title}",
            "",
            f"**Captured:** {captured_at.isoformat(timespec='seconds')}",
            f"**Source:** {source}",
            "",
            "## Raw Evidence",
            "",
            markdown_fence(raw_text),
            "",
            "## Summary",
            "",
            f"- {summary}",
            f"- Next action: {next_action}",
            "",
            "## Routing / Task-Manager Read",
            "",
            *[f"- {line}" for line in routing_lines],
        ]
    )
    write_text(path, body)
    return path


def ensure_reference_section(text: str) -> str:
    if re.search(r"^##\s+📎\s+References\s*$", text, flags=re.MULTILINE):
        return text
    insert = "\n\n## 📎 References\n\n| Type | Source | Link |\n|:-----|:-------|:-----|\n"
    progress = re.search(r"^##\s+(?:📈\s+)?Progress Log\s*$", text, flags=re.MULTILINE)
    if progress:
        return text[: progress.start()].rstrip() + insert + "\n" + text[progress.start() :].lstrip()
    return text.rstrip() + insert


def append_reference(text: str, task_path: Path, source_note: Path, title: str) -> str:
    text = ensure_reference_section(text)
    rel = rel_from_task(task_path, source_note).replace(" ", "%20")
    row = f"| Source Note | {escape_table(title)} | [{source_note.name}]({rel}) |"
    if row in text:
        return text
    match = re.search(r"(^##\s+📎\s+References\s*$.*?)(?=^##\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return text.rstrip() + "\n" + row + "\n"
    block = match.group(1).rstrip() + "\n" + row + "\n"
    return text[: match.start(1)] + block + text[match.end(1) :]


def append_progress(text: str, summary: str, source: str, captured_at: dt.datetime, status: str = "🟡") -> str:
    date = captured_at.date().isoformat()
    row = f"| {date} | {escape_table(source)} | {escape_table(summary)} | {escape_table(status)} |"
    if row in text:
        return text
    progress_match = re.search(r"^##\s+(?:📈\s+)?Progress Log\s*$", text, flags=re.MULTILINE)
    if not progress_match:
        addition = "\n\n## 📈 Progress Log\n\n| Date | Source | Update / Outcome | Status |\n|:-----|:-------|:-----------------|:-------|\n" + row + "\n"
        return text.rstrip() + addition
    section_match = re.search(r"(^##\s+(?:📈\s+)?Progress Log\s*$.*?)(?=^##\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not section_match:
        return text.rstrip() + "\n" + row + "\n"
    block = section_match.group(1).rstrip() + "\n" + row + "\n"
    return text[: section_match.start(1)] + block + text[section_match.end(1) :]


def append_subtask(text: str, next_action: str) -> str:
    action = strip_markdown(next_action).rstrip(".")
    if not action:
        return text
    item = f"- [ ] {action}."
    if item in text:
        return text
    section_match = re.search(r"(^##\s+✅\s+Subtasks\s*$.*?)(?=^##\s+|\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not section_match:
        addition = "\n\n## ✅ Subtasks\n\n" + item + "\n"
        notes = re.search(r"^##\s+Notes\s*$", text, flags=re.MULTILINE)
        if notes:
            return text[: notes.start()].rstrip() + addition + "\n" + text[notes.start() :].lstrip()
        return text.rstrip() + addition
    block = section_match.group(1).rstrip() + "\n" + item + "\n"
    return text[: section_match.start(1)] + block + text[section_match.end(1) :]


def update_last_updated(text: str, captured_at: dt.datetime) -> str:
    date = captured_at.date().isoformat()
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            raw = text[4:end]
            if re.search(r"^updated:\s*.*$", raw, flags=re.MULTILINE):
                raw = re.sub(r"^updated:\s*.*$", f"updated: {date}", raw, count=1, flags=re.MULTILINE)
            else:
                raw = raw.rstrip() + f"\nupdated: {date}"
            return "---\n" + raw + text[end:]
    if "> **Last Updated:**" in text:
        return re.sub(r"^> \*\*Last Updated:\*\*.*$", f"> **Last Updated:** {date}", text, count=1, flags=re.MULTILINE)
    header_end = text.find("\n---")
    line = f"> **Last Updated:** {date}\n"
    if header_end != -1:
        return text[:header_end].rstrip() + "\n" + line + text[header_end:]
    return line + text


def append_frontmatter_source(text: str, source_ref: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end < 0:
        return text
    raw = text[4:end]
    escaped = source_ref.replace("'", "''")
    if re.search(rf"^\s*-\s*['\"]?{re.escape(source_ref)}['\"]?\s*$", raw, flags=re.MULTILINE):
        return text
    lines = raw.splitlines()
    source_index = next((index for index, line in enumerate(lines) if re.match(r"^source_refs:\s*$", line)), None)
    if source_index is None:
        lines.extend(["source_refs:", f"  - '{escaped}'"])
    else:
        insert_at = source_index + 1
        while insert_at < len(lines) and re.match(r"^\s+-\s+", lines[insert_at]):
            insert_at += 1
        lines.insert(insert_at, f"  - '{escaped}'")
    return "---\n" + "\n".join(lines) + text[end:]


def update_task_file(
    root: Path,
    entry: TaskIndexEntry,
    source_note: Path,
    source_title: str,
    summary: str,
    next_action: str,
    source: str,
    captured_at: dt.datetime,
) -> Path:
    path = Path(entry.path)
    if not path.is_absolute():
        path = root / path
    text = read_text(path)
    if not text:
        text = f"# {entry.task_id} — {entry.title}\n\n> **Status:** 🟡 Needs triage\n> **Last Updated:** {captured_at.date().isoformat()}\n"
    text = update_last_updated(text, captured_at)
    text = append_reference(text, path, source_note, source_title)
    text = append_progress(text, summary, source, captured_at)
    text = append_subtask(text, next_action)
    source_ref = relative_to_root(root, source_note)
    if not text.startswith("---\n"):
        text = re.sub(r"^#\s+.*$", f"# {entry.title}", text, count=1, flags=re.MULTILINE)
        text = re.sub(
            r"^>\s*\*\*(?:Internal ID|Status|Lane|Owner|Due|Created|Last Updated):\*\*.*\n?",
            "",
            text,
            flags=re.MULTILINE | re.IGNORECASE,
        )
        yaml_title = entry.title.replace("'", "''")
        yaml_status = entry.status.replace("'", "''")
        yaml_owner = entry.owner.replace("'", "''")
        yaml_due = entry.due.replace("'", "''")
        yaml_source = source_ref.replace("'", "''")
        metadata = "\n".join(
            [
                "---",
                f"title: '{yaml_title}'",
                f"task_id: {entry.task_id}",
                f"status: '{yaml_status}'",
                "lane: Triage",
                f"owner: '{yaml_owner}'",
                "workstream: ''",
                f"due: '{yaml_due}'",
                f"updated: {captured_at.date().isoformat()}",
                "source_refs:",
                f"  - '{yaml_source}'",
                "inferred_fields:",
                "---",
                "",
            ]
        )
        text = metadata + text.lstrip()
    else:
        text = append_frontmatter_source(text, source_ref)
    write_text(path, text)
    return path


def create_candidate_task(
    root: Path,
    task_id: str,
    title: str,
    source_note: Path,
    source_title: str,
    source: str,
    summary: str,
    next_action: str,
    captured_at: dt.datetime,
) -> Path:
    date = captured_at.date().isoformat()
    path = task_store.unique_task_path(root, title)
    record = task_store.TaskRecord(
        task_id=task_id,
        title=title,
        path=path,
        status="needs-triage",
        lane="Triage",
        owner="Unassigned",
        workstream="Unassigned",
        created=date,
        updated=date,
        source_refs=[relative_to_root(root, source_note)],
        inferred_fields=["owner", "due", "workstream"],
    )
    body = task_store.render_task(
        record,
        summary=summary,
        context=(
            "Created from raw task-manager evidence. Review for duplication, confirm the owner and due date, "
            "then promote or close it."
        ),
        next_action=next_action,
        source=source,
    )
    write_text(path, body)
    task_store.rebuild_task_master(root)
    return path


def run_intake(
    root: Path,
    raw_text: str,
    source: str,
    explicit_task_id: str = "",
    title: str = "",
    rebuild_index: bool = False,
    min_confidence: float = 0.42,
    captured_at: dt.datetime | None = None,
) -> IntakeResult:
    root = root.resolve()
    captured_at = captured_at or now_local()
    summary = infer_summary(raw_text)
    next_action = infer_next_action(raw_text, summary)
    title = title or infer_title(raw_text, summary)
    index = load_or_build_index(root, rebuild=rebuild_index)
    match = match_task(raw_text, index, explicit_task_id=explicit_task_id)

    matched_line = "No existing task matched above threshold; candidate task will be created."
    if match.task is not None:
        matched_line = f"Best match: {match.task.title} (internal `{match.task.task_id}`, {match.confidence:.2f})."
    routing_lines = [
        matched_line,
        f"Reason: {match.reason}.",
        "Raw evidence preserved before task update.",
        "Triage refresh deferred for speed; run task_master_triage.py when a full health pass is needed.",
    ]
    source_note = save_source_note(root, raw_text, source, title, summary, next_action, routing_lines, captured_at)

    if match.task is not None and match.confidence >= min_confidence:
        task_path = update_task_file(root, match.task, source_note, title, summary, next_action, source, captured_at)
        task_store.rebuild_task_master(root)
        mode = "updated_existing"
        task_id = match.task.task_id
    else:
        task_id = next_inbox_id(root)
        task_path = create_candidate_task(root, task_id, title, source_note, title, source, summary, next_action, captured_at)
        mode = "created_candidate"

    return IntakeResult(
        mode=mode,
        task_id=task_id,
        display_label=title,
        task_path=relative_to_root(root, task_path),
        source_note_path=relative_to_root(root, source_note),
        confidence=match.confidence,
        summary=summary,
        next_action=next_action,
        triage_deferred=True,
        candidates=match.candidates,
    )


def read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8", errors="replace")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast raw-evidence task-manager intake")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repository root")
    parser.add_argument("--text", help="Raw pasted evidence text")
    parser.add_argument("--file", help="File containing raw pasted evidence")
    parser.add_argument("--source", default="User-pasted task-manager intake", help="Source label for the note")
    parser.add_argument("--task-id", default="", help="Force update of an existing task id")
    parser.add_argument("--title", default="", help="Override source note or candidate task title")
    parser.add_argument("--rebuild-index", action="store_true", help="Rebuild .agent/cache/task_index.json before matching")
    parser.add_argument("--min-confidence", type=float, default=0.42, help="Minimum match confidence before updating an existing task")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    raw_text = read_input(args).strip()
    if not raw_text:
        parser.error("No intake text provided via --text, --file, or stdin")

    result = run_intake(
        root=Path(args.repo),
        raw_text=raw_text,
        source=args.source,
        explicit_task_id=args.task_id,
        title=args.title,
        rebuild_index=args.rebuild_index,
        min_confidence=args.min_confidence,
    )
    if args.json:
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
    else:
        print(f"Mode: {result.mode}")
        print(f"Label: {result.display_label}")
        print(f"Internal task: {result.task_id} ({result.task_path})")
        print(f"Source note: {result.source_note_path}")
        print(f"Confidence: {result.confidence:.2f}")
        print("Triage: deferred")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
