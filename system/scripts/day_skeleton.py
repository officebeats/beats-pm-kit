#!/usr/bin/env python3
"""Deterministic daily skeleton renderer for the /day workflow.

Renders `.beats/day_skeleton.md` from real vault state with zero LLM
involvement:

1. Active task table grouped by lane (archived tasks excluded, done/closed
   tasks filtered out).
2. Overdue and due-today rollup from task `due` frontmatter.
3. Workstream snapshot table from `5. Trackers/WORKSTREAMS.md`.
4. Open boss-request items from `5. Trackers/critical/boss-requests.md`.

The nightly consolidation runner (`system/scripts/nightly_consolidate.py`)
regenerates this file so the /day workflow can treat it as a precomputed
base (when fresher than 20 hours) and spend model effort on synthesis and
prioritization only.

CLI: `python3 -m system.scripts.day_skeleton [--json]`
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.scripts import task_display, task_master_triage, task_store, workstream_snapshot  # noqa: E402
from system.utils.markdown_tables import split_cells  # noqa: E402


SKELETON_REL = Path(".beats/day_skeleton.md")
BOSS_REQUESTS_REL = Path("5. Trackers/critical/boss-requests.md")
GENERATED_RE = re.compile(
    r"<!--\s*generated:\s*(?P<ts>\S+)\s+by nightly_consolidate\s*-->"
)
ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
BOSS_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+")


def is_closed(status: str) -> bool:
    """A task/request status counts as closed when done or cancelled."""
    return task_master_triage.is_done(status or "") or "cancelled" in (status or "").lower()


def _cell(value: str) -> str:
    """Render a table cell as plain text: no wikilinks, no unescaped pipes."""
    value = task_display.strip_markdown(value or "")
    return value.replace("|", "\\|") or "—"


def _due_date(raw: str) -> dt.date | None:
    match = ISO_DATE_RE.search(raw or "")
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(1))
    except ValueError:
        return None


def parse_generated_at(text: str) -> dt.datetime | None:
    """Return the generated timestamp from a skeleton's first comment line."""
    match = GENERATED_RE.search(text or "")
    if not match:
        return None
    try:
        return dt.datetime.fromisoformat(match.group("ts"))
    except ValueError:
        return None


def _task_row(record: "task_store.TaskRecord") -> str:
    title = task_display.display_title_from_title(record.title)
    return "| {} | {} | {} | {} | {} |".format(
        _cell(title),
        _cell(record.status),
        _cell(record.due),
        _cell(record.owner),
        _cell(record.workstream),
    )


def _render_task_sections(records: list, today: dt.date) -> tuple[list[str], list[str]]:
    """Return (active-tasks-by-lane lines, due-rollup lines)."""
    active = [record for record in records if not is_closed(record.status)]
    by_lane: dict[str, list] = {}
    for record in active:
        by_lane.setdefault(record.lane or "Triage", []).append(record)

    lane_lines: list[str] = ["## Active Tasks by Lane", ""]
    if not by_lane:
        lane_lines.append("No active tasks found.")
    for lane in sorted(by_lane, key=str.lower):
        rows = sorted(by_lane[lane], key=lambda r: (r.due or "9999-99-99", r.title.lower()))
        lane_lines.append(f"### {lane} ({len(rows)})")
        lane_lines.append("")
        lane_lines.append("| Task | Status | Due | Owner | Workstream |")
        lane_lines.append("|:---|:---|:---|:---|:---|")
        lane_lines.extend(_task_row(record) for record in rows)
        lane_lines.append("")

    overdue: list[tuple[dt.date, object]] = []
    due_today: list = []
    for record in active:
        due = _due_date(record.due)
        if due is None:
            continue
        if due < today:
            overdue.append((due, record))
        elif due == today:
            due_today.append(record)
    overdue.sort(key=lambda item: item[0])

    rollup_lines: list[str] = ["## Due Rollup", ""]
    rollup_lines.append(f"### Overdue ({len(overdue)})")
    rollup_lines.append("")
    if overdue:
        for due, record in overdue:
            title = task_display.display_title_from_title(record.title)
            days = (today - due).days
            rollup_lines.append(f"- {title} — due {due.isoformat()} ({days}d overdue)")
    else:
        rollup_lines.append("- None")
    rollup_lines.append("")
    rollup_lines.append(f"### Due Today ({len(due_today)})")
    rollup_lines.append("")
    if due_today:
        for record in sorted(due_today, key=lambda r: r.title.lower()):
            title = task_display.display_title_from_title(record.title)
            rollup_lines.append(f"- {title} — due {today.isoformat()}")
    else:
        rollup_lines.append("- None")
    rollup_lines.append("")
    return lane_lines, rollup_lines


def _render_workstreams(root: Path) -> list[str]:
    snapshots = workstream_snapshot.parse_workstream_table(root)
    if not snapshots:
        return []
    lines = [
        "## Workstream Snapshot",
        "",
        "| Workstream | Latest Outcome | Open Items | Status |",
        "|:---|:---|:---|:---|",
    ]
    for item in snapshots:
        lines.append(
            "| {} | {} | {} | {} |".format(
                _cell(item.title),
                _cell(item.latest_outcome),
                _cell("; ".join(item.open_items)),
                _cell(item.status),
            )
        )
    lines.append("")
    return lines


def _parse_boss_open_items(root: Path) -> list[dict[str, str]]:
    path = root / BOSS_REQUESTS_REL
    if not path.exists():
        return []
    items: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = split_cells(line)
        if len(cells) < 5:
            continue
        request_id = task_display.strip_markdown(cells[0])
        if not BOSS_ID_RE.match(request_id):
            continue
        status = cells[4]
        if is_closed(status):
            continue
        items.append(
            {
                "id": request_id,
                "request": cells[1],
                "due": cells[3],
                "status": status,
            }
        )
    return items


def _render_boss_requests(root: Path) -> list[str]:
    items = _parse_boss_open_items(root)
    if not items:
        return []
    lines = [
        "## Boss Requests — Open",
        "",
        "| ID | Request | Due | Status |",
        "|:---|:---|:---|:---|",
    ]
    for item in items:
        lines.append(
            "| {} | {} | {} | {} |".format(
                _cell(item["id"]),
                _cell(item["request"]),
                _cell(item["due"]),
                _cell(item["status"]),
            )
        )
    lines.append("")
    return lines


def render_skeleton(root: Path = ROOT, *, today: dt.date | None = None, now: dt.datetime | None = None) -> tuple[str, dict]:
    """Render the skeleton Markdown; return (text, summary dict)."""
    today = today or dt.date.today()
    now = now or dt.datetime.now().astimezone()
    records = list(task_store.iter_tasks(root))
    active_count = sum(1 for record in records if not is_closed(record.status))

    lane_lines, rollup_lines = _render_task_sections(records, today)
    sections = ["active-tasks", "due-rollup"]
    lines = [
        f"<!-- generated: {now.isoformat(timespec='seconds')} by nightly_consolidate -->",
        "",
        f"# Day Skeleton — {today.isoformat()}",
        "",
        "Deterministic precompute for /day. Real vault state only; no synthesis.",
        "",
    ]
    lines.extend(lane_lines)
    lines.extend(rollup_lines)

    workstream_lines = _render_workstreams(root)
    if workstream_lines:
        sections.append("workstreams")
        lines.extend(workstream_lines)

    boss_lines = _render_boss_requests(root)
    if boss_lines:
        sections.append("boss-requests")
        lines.extend(boss_lines)

    text = "\n".join(lines).rstrip() + "\n"
    summary = {
        "ok": True,
        "path": str(SKELETON_REL),
        "sections": sections,
        "task_count": active_count,
    }
    return text, summary


def generate(root: Path = ROOT, *, today: dt.date | None = None, now: dt.datetime | None = None) -> dict:
    """Write `.beats/day_skeleton.md` and return the summary dict."""
    text, summary = render_skeleton(root, today=today, now=now)
    path = root / SKELETON_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the summary as JSON.")
    args = parser.parse_args(argv)

    summary = generate(ROOT)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            "Day skeleton written to {} ({} sections, {} active tasks)".format(
                summary["path"], len(summary["sections"]), summary["task_count"]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
