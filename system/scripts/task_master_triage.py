#!/usr/bin/env python3
"""
Local overdue/staleness triage for Beats PM task files.

This script is intentionally local-only. It reads TASK_MASTER and task detail
files, then writes:

1. A managed triage block in TASK_MASTER.
2. Managed triage blocks inside flagged task files.
3. A dated local report under 3. Meetings/reports/day/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

try:  # pragma: no cover - import path differs for script vs package execution.
    from . import markdown_humanizer, task_display, task_store
except ImportError:  # pragma: no cover
    import markdown_humanizer
    import task_display
    import task_store


BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from system.utils.markdown_tables import split_cells, strip_wikilinks  # noqa: E402

TASK_MASTER_PATH = BASE_DIR / "5. Trackers" / "TASK_MASTER.md"
TASKS_DIR = BASE_DIR / "5. Trackers" / "tasks"
REPORTS_DIR = BASE_DIR / "3. Meetings" / "reports" / "day"

SUMMARY_BEGIN = "<!-- TASK_TRIAGE_SUMMARY:BEGIN -->"
SUMMARY_END = "<!-- TASK_TRIAGE_SUMMARY:END -->"
TASK_BEGIN = "<!-- TASK_TRIAGE:BEGIN -->"
TASK_END = "<!-- TASK_TRIAGE:END -->"
DEFAULT_STALE_BUSINESS_DAYS = 10

DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
PROGRESS_HEADER_PATTERN = re.compile(r"^##\s+(?:(?:📈\s+)?Progress Log|Progress)\s*$")


@dataclass
class TaskRecord:
    task_id: str
    title: str
    task_master_due: str
    task_master_status: str
    path: Path
    updated: str = ""
    source_refs: list[str] | None = None


@dataclass
class TriageItem:
    task_id: str
    title: str
    path: Path
    need: str
    reason: str
    evidence: str
    question: str
    severity: int
    summary: str
    last_activity: str
    comms_signal: str
    relevant_links: list[str]


@dataclass
class ProgressEntry:
    date: str
    source: str
    update: str
    status: str


@dataclass
class ReferenceLink:
    kind: str
    label: str
    target: str


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def today_local() -> dt.date:
    return now_local().date()


def iso_date(value: dt.date) -> str:
    return value.isoformat()


def parse_iso_date(value: str) -> dt.date | None:
    match = DATE_PATTERN.search(value or "")
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(1))
    except ValueError:
        return None


def business_days_between(start: dt.date, end: dt.date) -> int:
    if start == end:
        return 0
    step = 1 if end > start else -1
    current = start
    total = 0
    while current != end:
        current += dt.timedelta(days=step)
        if current.weekday() < 5:
            total += step
    return total


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    markdown_humanizer.write_generated_markdown(path, text)


def replace_block(text: str, begin: str, end: str, block: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(begin)}.*?{re.escape(end)}\n?",
        flags=re.DOTALL,
    )
    wrapped = f"{begin}\n{block.rstrip()}\n{end}"
    if pattern.search(text):
        updated = pattern.sub(f"\n{wrapped}\n", text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + wrapped + "\n"
    return re.sub(r"\n{3,}", "\n\n", updated)


def remove_block(text: str, begin: str, end: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(begin)}.*?{re.escape(end)}\n?",
        flags=re.DOTALL,
    )
    updated = pattern.sub("\n", text)
    return re.sub(r"\n{3,}", "\n\n", updated).rstrip() + "\n"


def strip_markdown(value: str) -> str:
    value = value.replace("~~", "")
    value = strip_wikilinks(value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def markdown_link(label: str, target: str) -> str:
    if target.startswith("http://") or target.startswith("https://"):
        return f"[{label}]({target})"
    resolved = (BASE_DIR / target).resolve() if not target.startswith("/") else Path(target)
    return f"[{label}]({quote(str(resolved), safe='/:#?=&%.-_~')})"


def parse_headline_title(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            title = strip_markdown(stripped[2:])
            title = re.sub(r"^[A-Z][A-Z0-9-]*\s*[:—-]\s*", "", title).strip()
            return title
    return ""


def parse_context_summary(text: str) -> str:
    match = re.search(
        r"## (?:Summary|Context & Background|Context)\s*(.*?)(?=\n## )",
        text,
        flags=re.DOTALL,
    )
    if not match:
        return ""
    body = match.group(1).strip()
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    if not paragraphs:
        return ""
    first = strip_markdown(paragraphs[0])
    return first[:260]


def parse_progress_entries(text: str) -> list[ProgressEntry]:
    entries: list[ProgressEntry] = []
    in_progress = False
    for line in text.splitlines():
        stripped = line.strip()
        if PROGRESS_HEADER_PATTERN.match(stripped):
            in_progress = True
            continue
        if in_progress and stripped.startswith("## "):
            break
        if not in_progress:
            continue
        bullet_match = re.match(
            r"-\s+\*\*(20\d{2}-\d{2}-\d{2})\s*(?:\(([^)]+)\))?\*\*:\s*(.+)",
            stripped,
        )
        if bullet_match:
            entries.append(
                ProgressEntry(
                    date=bullet_match.group(1),
                    source=strip_markdown(bullet_match.group(2) or "Progress log"),
                    update=strip_markdown(bullet_match.group(3)),
                    status="",
                )
            )
            continue
        if not stripped.startswith("|"):
            continue
        parts = split_cells(stripped)
        if len(parts) < 3 or parts[0].lower() == "date" or not parts[0].startswith("20"):
            continue
        entries.append(
            ProgressEntry(
                date=parts[0],
                source=strip_markdown(parts[1]),
                update=strip_markdown(parts[2]),
                status=strip_markdown(parts[3]) if len(parts) > 3 else "",
            )
        )
    return entries


def parse_reference_links(text: str, base_path: Path) -> list[ReferenceLink]:
    refs: list[ReferenceLink] = []
    match = re.search(r"## 📎 References\s*(.*?)(?=\n## )", text, flags=re.DOTALL)
    if not match:
        return refs
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        parts = split_cells(stripped)
        if len(parts) < 3 or parts[0].lower() == "type" or parts[0].startswith(":"):
            continue
        kind = strip_markdown(parts[0])
        label = strip_markdown(parts[1])
        link_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", parts[2])
        if link_match:
            target = link_match.group(2).strip()
            if not (target.startswith("http://") or target.startswith("https://") or target.startswith("/")):
                target = str((base_path / target).resolve())
            refs.append(
                ReferenceLink(
                    kind=kind,
                    label=strip_markdown(link_match.group(1)) or label,
                    target=target,
                )
            )
        else:
            plain = strip_markdown(parts[2])
            if plain.startswith("http://") or plain.startswith("https://"):
                refs.append(ReferenceLink(kind=kind, label=label, target=plain))
    return refs


def source_type(source: str) -> str:
    lower = source.lower()
    if "calendar" in lower:
        return "Calendar"
    if "slack" in lower:
        return "Slack"
    if "teams" in lower:
        return "Teams"
    if "email" in lower or "outlook" in lower:
        return "Email"
    if "transcript" in lower:
        return "Transcript"
    if "jira" in lower or "rovo" in lower or "atlassian" in lower:
        return "Atlassian"
    return source or "Local"


def infer_comms_signal(entry: ProgressEntry | None) -> str:
    if entry is None:
        return "No recent communication signal found; this is being flagged from local task state only."
    src = source_type(entry.source)
    text = f"{entry.update} {entry.status}".lower()
    if any(term in text for term in ["done", "completed", "resolved", "closed", "shipped"]):
        return f"{src} signal suggests this may be complete, but the task is still open locally."
    if any(
        term in text
        for term in [
            "still active",
            "next step",
            "follow-up",
            "keep",
            "needs",
            "remain",
            "on calendar",
            "active",
            "waiting",
            "due",
            "sync",
            "planning",
        ]
    ):
        return f"{src} signal suggests this should still proceed."
    return f"{src} signal exists, but it does not clearly say this is complete."


def select_relevant_links(task_path: Path, refs: list[ReferenceLink]) -> list[str]:
    selected = [markdown_link("Task file", task_path.relative_to(BASE_DIR).as_posix())]
    preferred_order = ["Slack Intake", "Slack", "Teams", "Email", "Calendar", "Transcript", "Task Master", "Planning Artifact"]
    scored: list[tuple[int, ReferenceLink]] = []
    for ref in refs:
        try:
            score = preferred_order.index(ref.kind)
        except ValueError:
            score = len(preferred_order)
        scored.append((score, ref))
    for _score, ref in sorted(scored, key=lambda item: (item[0], item[1].label))[:3]:
        selected.append(markdown_link(f"{ref.kind}: {ref.label}", ref.target))
    return selected


def parse_task_master() -> list[TaskRecord]:
    tasks: list[TaskRecord] = []
    for task in task_store.iter_tasks(BASE_DIR):
        tasks.append(
            TaskRecord(
                task_id=task.task_id,
                title=task.title,
                task_master_due=task.due,
                task_master_status=task.status,
                path=task.path,
                updated=task.updated,
                source_refs=task.source_refs,
            )
        )
    deduped: dict[str, TaskRecord] = {}
    for task in tasks:
        existing = deduped.get(task.task_id)
        if existing is None:
            deduped[task.task_id] = task
            continue
        if "done" in existing.task_master_status.lower() and "done" not in task.task_master_status.lower():
            deduped[task.task_id] = task
    return list(deduped.values())


def task_header_value(text: str, label: str) -> str:
    pattern = re.compile(rf"^>\s+\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", flags=re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def parse_progress_dates(text: str) -> list[dt.date]:
    dates: list[dt.date] = []
    in_progress = False
    for line in text.splitlines():
        stripped = line.strip()
        if PROGRESS_HEADER_PATTERN.match(stripped):
            in_progress = True
            continue
        if in_progress and stripped.startswith("## "):
            break
        if in_progress and stripped.startswith("|"):
            match = DATE_PATTERN.search(stripped)
            if match:
                parsed = parse_iso_date(match.group(1))
                if parsed:
                    dates.append(parsed)
    return dates


def latest_progress_row(text: str) -> str:
    rows: list[str] = []
    in_progress = False
    for line in text.splitlines():
        stripped = line.strip()
        if PROGRESS_HEADER_PATTERN.match(stripped):
            in_progress = True
            continue
        if in_progress and stripped.startswith("## "):
            break
        if in_progress and (stripped.startswith("| 20") or re.match(r"-\s+\*\*20\d{2}-\d{2}-\d{2}", stripped)):
            rows.append(stripped)
    return rows[-1] if rows else ""


def parse_subtasks(text: str) -> tuple[int, int]:
    total = 0
    done = 0
    in_subtasks = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## ✅ Subtasks") or stripped.startswith("## Next actions"):
            in_subtasks = True
            continue
        if in_subtasks and stripped.startswith("## "):
            break
        if in_subtasks and stripped.startswith("- ["):
            total += 1
            if stripped.lower().startswith("- [x]"):
                done += 1
    return done, total


def is_done(status: str) -> bool:
    lower = status.lower()
    return any(marker in lower for marker in ["done", "completed", "closed"]) or "✅" in status


def is_snoozed(status: str) -> bool:
    lower = status.lower()
    return any(marker in lower for marker in ["on hold", "strategic hold", "deferred", "monitor", "awaiting"])


def likely_complete_signal(status: str, latest_row: str, subtasks_done: int, subtasks_total: int) -> tuple[bool, str]:
    if is_done(status):
        return False, ""
    if subtasks_total > 0 and subtasks_done == subtasks_total:
        return True, f"all {subtasks_total} subtasks are checked but the status is still open"
    lower_row = latest_row.lower()
    phrases = [
        "ready for review",
        "draft v1 complete",
        "final draft complete",
        "follow-up sent",
        "handoff complete",
        "hand-off complete",
        "sent the follow-up",
    ]
    for phrase in phrases:
        if phrase in lower_row:
            return True, f"latest progress log suggests completion or handoff: `{strip_markdown(latest_row)[:140]}`"
    return False, ""


def build_task_block(items: list[TriageItem]) -> str:
    lines = [
        "## Triage Signals",
        "",
        f"- Last triage refresh: {now_local().strftime('%Y-%m-%d %H:%M %Z')}",
    ]
    for item in items:
        lines.append(f"- {item.need}: {item.reason}")
        lines.append(f"  What it is: {item.summary}")
        lines.append(f"  Last activity: {item.last_activity}")
        lines.append(f"  Communication signal: {item.comms_signal}")
        lines.append(f"  Confirmation needed: {item.question}")
    return "\n".join(lines)


def build_summary_block(items: list[TriageItem], report_path: Path) -> str:
    today = now_local().strftime("%Y-%m-%d")
    pillars = items[:3]
    lines = [
        f"## Triage — {today} Daily Health Check",
        "",
        "> Managed by `system/scripts/task_master_triage.py`. Flags open items that are overdue, stale, at risk, or possibly complete but still open.",
        f"> See the [day triage report](../3.%20Meetings/reports/day/{report_path.name}).",
        "",
        "### Top Pillars Today",
        "",
    ]
    if not pillars:
        lines.append("- No urgent triage pillar was detected.")
    else:
        for item in pillars:
            lines.append(f"- {item.title}: {item.reason}")
    lines.extend(
        [
            "",
        "| Task | Triage Need | Why it needs review now | Exact evidence source |",
        "|:-----|:------------|:------------------------|:----------------------|",
        ]
    )
    if not items:
        lines.append("| _None_ | _None_ | No local overdue/stale/possibly-complete items detected. | Local task files |")
    else:
        for item in items:
            link = item.path.relative_to(TASK_MASTER_PATH.parent).as_posix()
            lines.append(
                f"| [{item.title}]({link}) | {item.need} | {item.reason} | {item.evidence} |"
            )
        lines.extend(
            [
                "",
                "### Questions For Owner",
                "",
            ]
        )
        for index, item in enumerate(items, start=1):
            lines.append(f"{index}. {item.title}: {item.question}")
    return "\n".join(lines)


def build_report(items: list[TriageItem]) -> str:
    stamp = now_local().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"# Task Triage Report - {stamp}",
        "",
        "## Summary",
        "",
        f"- Items needing confirmation: {len(items)}",
        f"- Stale threshold: {DEFAULT_STALE_BUSINESS_DAYS} business days",
        "",
        "## Top Pillars Today",
        "",
    ]
    if not items:
        lines.append("- No urgent triage pillar was detected.")
    else:
        for item in items[:3]:
            lines.append(f"- {item.title}: {item.reason}")
    lines.extend(
        [
            "",
            "## Questions",
        "",
        ]
    )
    if not items:
        lines.append("- No overdue, stale, or likely-complete open items were detected from local task files.")
    else:
        for item in items:
            lines.append(f"- {item.title} ({item.need}): {item.question}")
    lines.extend(
        [
            "",
            "## Dialogue Prompts",
            "",
        ]
    )
    if not items:
        lines.append("- No dialogue prompts needed.")
    else:
        for item in items:
            lines.extend(
                [
                    f"### {item.title}",
                    f"- What it is: {item.summary}",
                    f"- Last activity: {item.last_activity}",
                    f"- Communication signal: {item.comms_signal}",
                    f"- Relevant links: {' | '.join(item.relevant_links)}",
                    f"- Agent refs: {item.task_id}",
                    f"- Clarify: {item.question}",
                    "",
                ]
            )
    return "\n".join(lines)


def collect_triage() -> tuple[list[TriageItem], dict[str, list[TriageItem]]]:
    items: list[TriageItem] = []
    by_task: dict[str, list[TriageItem]] = {}
    today = today_local()
    records = parse_task_master()
    known_titles: dict[str, str] = {}
    for record in records:
        text = read_text(record.path)
        known_titles[record.task_id] = parse_headline_title(text) or record.title

    def scrub(value: str) -> str:
        return task_display.scrub_visible_refs(value, known_titles)

    for record in records:
        text = read_text(record.path)
        if not text:
            continue
        status = task_header_value(text, "Status") or record.task_master_status
        combined_status = f"{status} {record.task_master_status}"
        if is_done(combined_status) or is_snoozed(combined_status):
            continue
        due_text = record.task_master_due or task_header_value(text, "Due")
        due_date = parse_iso_date(due_text)
        last_updated_text = record.updated or task_header_value(text, "Last Updated")
        last_updated_date = parse_iso_date(last_updated_text)
        display_title = scrub(parse_headline_title(text) or record.title)
        summary = scrub(parse_context_summary(text) or display_title)
        progress_entries = parse_progress_entries(text)
        progress_dates = [parse_iso_date(entry.date) for entry in progress_entries if parse_iso_date(entry.date)]
        latest_progress = max(progress_dates) if progress_dates else None
        evidence_date = max([date for date in [latest_progress, last_updated_date] if date is not None], default=None)
        latest_entry = progress_entries[-1] if progress_entries else None
        latest_row = latest_progress_row(text)
        if latest_entry:
            last_activity = scrub(f"{latest_entry.date} via {source_type(latest_entry.source)}: {latest_entry.update}")
        elif last_updated_date:
            last_activity = f"Last Updated {iso_date(last_updated_date)} with no structured progress entry."
        else:
            last_activity = "No structured recent activity found in the task file."
        comms_signal = scrub(infer_comms_signal(latest_entry))
        reference_links = parse_reference_links(text, record.path.parent)
        if not reference_links:
            reference_links = [
                ReferenceLink("Evidence", Path(ref).name, str((BASE_DIR / ref).resolve()))
                for ref in (record.source_refs or [])
            ]
        relevant_links = select_relevant_links(record.path, reference_links)
        subtasks_done, subtasks_total = parse_subtasks(text)

        task_items: list[TriageItem] = []

        if due_date:
            days_until_due = business_days_between(today, due_date)
            if due_date < today:
                task_items.append(
                    TriageItem(
                        task_id=record.task_id,
                        title=display_title,
                        path=record.path,
                        need="Overdue",
                        reason=scrub(f"due date {iso_date(due_date)} has passed and the task is still open"),
                        evidence=scrub(f"Task file due `{iso_date(due_date)}`; status `{status}`"),
                        question=f"is this still open, and if yes what exact new due date should replace {iso_date(due_date)}?",
                        severity=0,
                        summary=summary,
                        last_activity=last_activity,
                        comms_signal=comms_signal,
                        relevant_links=relevant_links,
                    )
                )
            elif 0 <= days_until_due <= 5:
                task_items.append(
                    TriageItem(
                        task_id=record.task_id,
                        title=display_title,
                        path=record.path,
                        need="At risk",
                        reason=scrub(f"due date {iso_date(due_date)} is within {days_until_due} business day(s) and the task is not clearly done"),
                        evidence=scrub(f"Task file due `{iso_date(due_date)}`; status `{status}`"),
                        question=f"is the current due date {iso_date(due_date)} still realistic, or should this be rescheduled or split?",
                        severity=3,
                        summary=summary,
                        last_activity=last_activity,
                        comms_signal=comms_signal,
                        relevant_links=relevant_links,
                    )
                )

        if evidence_date:
            stale_days = business_days_between(evidence_date, today)
            if stale_days >= DEFAULT_STALE_BUSINESS_DAYS:
                task_items.append(
                    TriageItem(
                        task_id=record.task_id,
                        title=display_title,
                        path=record.path,
                        need="Stale",
                        reason=scrub(f"no local progress signal has been recorded for {stale_days} business days"),
                        evidence=f"Last Updated `{iso_date(evidence_date)}`",
                        question="is this still active, blocked, or ready to be deprioritized or closed?",
                        severity=2,
                        summary=summary,
                        last_activity=last_activity,
                        comms_signal=comms_signal,
                        relevant_links=relevant_links,
                    )
                )

        likely_complete, complete_reason = likely_complete_signal(status, latest_row, subtasks_done, subtasks_total)
        if likely_complete:
            evidence = "All subtasks checked" if subtasks_total and subtasks_done == subtasks_total else strip_markdown(latest_row)
            task_items.append(
                TriageItem(
                    task_id=record.task_id,
                    title=display_title,
                    path=record.path,
                    need="Possibly complete",
                    reason=scrub(complete_reason),
                    evidence=scrub(evidence or f"Status `{status}`"),
                    question="can this be marked done or partial, or is a remaining deliverable still open?",
                    severity=1,
                    summary=summary,
                    last_activity=last_activity,
                    comms_signal=comms_signal,
                    relevant_links=relevant_links,
                )
            )

        if task_items:
            by_task[record.task_id] = task_items
            items.extend(task_items)

    final_by_task: dict[str, TriageItem] = {}
    for item in items:
        current = final_by_task.get(item.task_id)
        if current is None or item.severity < current.severity:
            final_by_task[item.task_id] = item
    final_items = sorted(final_by_task.values(), key=lambda item: (item.severity, item.task_id, item.need))
    by_task_final: dict[str, list[TriageItem]] = {}
    for item in final_items:
        by_task_final.setdefault(item.task_id, []).append(item)
    return final_items, by_task_final


def apply_updates(
    items: list[TriageItem],
    by_task: dict[str, list[TriageItem]],
    report_path: Path,
    touched_tasks: set[str] | None = None,
) -> None:
    summary_block = build_summary_block(items, report_path)
    master_text = read_text(TASK_MASTER_PATH)
    master_text = replace_block(master_text, SUMMARY_BEGIN, SUMMARY_END, summary_block)
    write_text(TASK_MASTER_PATH, master_text)

    for task_path in TASKS_DIR.glob("*.md"):
        task_text = read_text(task_path)
        parsed = task_store.parse_task(task_path)
        if parsed is None:
            continue
        task_id = parsed.task_id
        if touched_tasks is not None and task_id not in touched_tasks:
            continue
        task_items = by_task.get(task_id, [])
        if task_items:
            block = build_task_block(task_items)
            updated = replace_block(task_text, TASK_BEGIN, TASK_END, block)
            if updated != task_text:
                write_text(task_path, updated)
        elif TASK_BEGIN in task_text and TASK_END in task_text:
            updated = remove_block(task_text, TASK_BEGIN, TASK_END)
            write_text(task_path, updated)


def print_questions(items: list[TriageItem]) -> None:
    print(f"Items needing confirmation: {len(items)}")
    for item in items:
        print(f"- {item.title} [{item.need}]: {item.question}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh local task triage signals.")
    parser.add_argument("--apply", action="store_true", help="Write the managed triage summary, task blocks, and report.")
    parser.add_argument(
        "--touched-task",
        action="append",
        default=[],
        metavar="TASK_ID",
        help=(
            "Fast path for targeted evidence intake. Refresh the TASK_MASTER summary and report, "
            "but only add/remove managed triage blocks for the supplied task ID. May be repeated."
        ),
    )
    args = parser.parse_args()

    items, by_task = collect_triage()
    report_name = f"{today_local().isoformat()}-task-triage.md"
    report_path = REPORTS_DIR / report_name
    report_text = build_report(items)
    touched_tasks = {task_id.strip() for task_id in args.touched_task if task_id.strip()}

    if args.apply:
        write_text(report_path, report_text)
        apply_updates(items, by_task, report_path, touched_tasks or None)
        print(f"Report: {report_path.relative_to(BASE_DIR).as_posix()}")
        if touched_tasks:
            print(f"Touched task blocks refreshed: {', '.join(sorted(touched_tasks))}")

    print_questions(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
