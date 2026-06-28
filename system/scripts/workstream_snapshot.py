#!/usr/bin/env python3
"""Render the human-facing workstream snapshot for Task Manager.

This helper is local-only and read-only. It prefers the curated workstream
ledger, then falls back to the highest-ranked Task Master commitments when the
workstream ledger is still empty or only contains the template row.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKSTREAMS = Path("5. Trackers/WORKSTREAMS.md")

sys.path.insert(0, str(ROOT))

from system.scripts import critical_commitment_refresh  # noqa: E402
from system.scripts import task_display  # noqa: E402


@dataclass
class WorkstreamSnapshot:
    title: str
    latest_outcome: str
    latest_evidence: str
    completed: str
    completed_evidence: str
    open_items: list[str]
    recommended_next_3: list[str]
    status: str
    source: str
    started_at: str = ""
    initial_source: str = ""
    latest_source: str = ""
    agent_refs: list[str] | None = None


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def strip_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value or "")
    value = value.replace("~~", "")
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def table_cells(line: str) -> list[str]:
    if not line.strip().startswith("|"):
        return []
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if any(cell.startswith(":---") or cell == "---" for cell in cells):
        return []
    return cells


def split_actions(value: str) -> list[str]:
    cleaned = strip_markdown(value)
    if not cleaned or cleaned in {"[top action]", "top action"}:
        return []
    parts = [part.strip(" -;") for part in re.split(r"\s*(?:;|\n|\u2022)\s*", cleaned) if part.strip(" -;")]
    return parts[:3]


def is_placeholder_title(title: str) -> bool:
    return title.lower() in {"workstream", "example workstream", "[example workstream]"}


def parse_workstream_table(root: Path) -> list[WorkstreamSnapshot]:
    text = read_text(root / WORKSTREAMS)
    snapshots: list[WorkstreamSnapshot] = []
    for line in text.splitlines():
        cells = table_cells(line)
        if len(cells) < 6 or cells[0].lower() == "workstream":
            continue
        title = strip_markdown(cells[0])
        if not title or is_placeholder_title(title):
            continue
        latest = strip_markdown(cells[1]) or "No latest outcome recorded"
        completed = strip_markdown(cells[2]) or "None newly confirmed"
        open_cell = strip_markdown(cells[3])
        open_items = split_actions(open_cell)
        if not open_items and open_cell:
            open_items = [open_cell]
        recommended = split_actions(cells[4])
        snapshots.append(
            WorkstreamSnapshot(
                title=title,
                latest_outcome=latest,
                latest_evidence="5. Trackers/WORKSTREAMS.md",
                completed=completed,
                completed_evidence="5. Trackers/WORKSTREAMS.md" if completed != "None newly confirmed" else "",
                open_items=open_items or ["No open item count recorded"],
                recommended_next_3=recommended or [
                    "Confirm the latest outcome and source evidence",
                    "Refresh open items from configured read windows",
                    "Choose the next accepted Task Master action",
                ],
                status=strip_markdown(cells[5]) or "Active",
                source="workstreams",
                agent_refs=[],
            )
        )
    return snapshots


def task_title_to_workstream(title: str) -> str:
    cleaned = task_display.display_title_from_title(title)
    words = cleaned.split()
    return " ".join(words[:9]) if words else "Untitled Workstream"


def parse_owner_from_title(title: str) -> str:
    return "Owner"


def fallback_from_ranked_tasks(root: Path, mode: str, limit: int) -> list[WorkstreamSnapshot]:
    ranked = critical_commitment_refresh.build_ranked_items(root, mode)
    local_rows = critical_commitment_refresh.task_rows(root) + critical_commitment_refresh.boss_items(root)
    status_by_id = {row.get("task_id", ""): strip_markdown(row.get("status", "")) for row in local_rows if row.get("task_id")}
    status_by_title = {strip_markdown(row.get("title", "")): strip_markdown(row.get("status", "")) for row in local_rows if row.get("title")}
    known_titles = {row.get("task_id", ""): task_display.display_title_from_title(row.get("title", "")) for row in local_rows if row.get("task_id")}
    snapshots: list[WorkstreamSnapshot] = []
    seen: set[str] = set()
    for item in ranked:
        title = task_title_to_workstream(item.display_title or item.title)
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        due = f" by {item.gate_date}" if item.gate_date else ""
        completion = "None newly confirmed"
        completion_source = ""
        if item.completion_state == "explicit_complete":
            completion = "Explicit completion present in local ledger"
            completion_source = ", ".join(item.source_refs)
        elif item.completion_state == "implied_complete":
            completion = "Possible completion needs confirmation"
            completion_source = item.display_evidence
        raw_outcome = status_by_id.get(item.task_id) or status_by_title.get(strip_markdown(item.title)) or f"Priority signal: {item.priority_reason}"
        outcome = task_display.scrub_visible_refs(raw_outcome, known_titles)
        evidence = item.display_evidence or task_display.format_evidence(
            task_display.provenance_from_title(item.title, source=item.source)
        )
        snapshots.append(
            WorkstreamSnapshot(
                title=title,
                latest_outcome=outcome,
                latest_evidence=task_display.scrub_visible_refs(evidence, known_titles),
                completed=completion,
                completed_evidence=task_display.scrub_visible_refs(completion_source, known_titles),
                open_items=[f"{parse_owner_from_title(item.title)} - {title}{due}, from local task tracker"],
                recommended_next_3=[
                    "Confirm the latest outcome and whether this is still active",
                    "Identify the next owner-visible deliverable or decision gate",
                    "Update the workstream ledger with source-backed completion evidence",
                ],
                status=item.completion_state,
                source="task_master_fallback",
                started_at=item.started_at,
                initial_source=item.initial_source,
                latest_source=item.latest_source,
                agent_refs=item.agent_refs or [],
            )
        )
        if len(snapshots) >= limit:
            break
    return snapshots


def render_markdown(items: list[WorkstreamSnapshot], *, source_note: str) -> str:
    lines: list[str] = []
    lines.append("## Workstream Snapshot")
    lines.append("")
    lines.append(source_note)
    lines.append("")
    if not items:
        lines.extend(
            [
                "No workstreams are currently recorded.",
                "",
                "Add entries to `5. Trackers/WORKSTREAMS.md` or run a named read-only source refresh before using this snapshot.",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"
    for item in items:
        lines.append(f"### {item.title}")
        lines.append(f"- Latest outcome: {item.latest_outcome}")
        lines.append(f"  - Evidence: {item.latest_evidence or 'No evidence recorded'}")
        lines.append(f"- Completed: {item.completed or 'None newly confirmed'}")
        lines.append(f"  - Completed: {item.completed_evidence or 'None newly confirmed'}")
        lines.append(f"- Open items: {len(item.open_items)}")
        for open_item in item.open_items:
            lines.append(f"  - {open_item}")
        lines.append("- Recommended next 3:")
        for action in (item.recommended_next_3 or [])[:3]:
            lines.append(f"  - {action}")
        while len(item.recommended_next_3) < 3:
            item.recommended_next_3.append("Confirm the next source-backed action")
            lines.append("  - Confirm the next source-backed action")
        if item.agent_refs:
            lines.append(f"- Agent refs: {', '.join(item.agent_refs)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_snapshot(root: Path, mode: str, limit: int) -> tuple[list[WorkstreamSnapshot], str]:
    items = parse_workstream_table(root)
    if items:
        return items[:limit], "Source: `5. Trackers/WORKSTREAMS.md`."
    fallback = fallback_from_ranked_tasks(root, mode, limit)
    return (
        fallback,
        "Source: `5. Trackers/WORKSTREAMS.md` has no non-template workstreams, so this snapshot falls back to ranked local task commitments.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mode", choices=["task", "day", "week", "boss"], default="task")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    mode = "day" if args.mode == "task" else args.mode
    items, note = build_snapshot(args.root.resolve(), mode, args.limit)
    if args.json:
        print(json.dumps({"schema_version": 1, "source_note": note, "workstreams": [asdict(item) for item in items]}, indent=2))
    else:
        print(render_markdown(items, source_note=note), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
