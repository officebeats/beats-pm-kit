#!/usr/bin/env python3
"""Human-facing task display and provenance helpers.

Task, Jira, and card IDs are useful internal anchors, but they should not be
the visible language in recurring planning summaries. This module extracts a
display title plus source provenance from existing task files and scrubs hard
IDs from renderer-facing text.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.utils.markdown_tables import split_cells, strip_wikilinks  # noqa: E402


TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{3,}[a-z]?\b")
ISSUE_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d{1,}[a-z]?\b")
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
HEADER_RE_TEMPLATE = r"^>\s+\*\*{label}:\*\*\s*(.+?)\s*$"
PROGRESS_HEADER_RE = re.compile(r"^##\s+(?:[\W_]+\s+)?Progress(?: Log)?\s*$")


@dataclass
class SourcePointer:
    label: str
    date: str = ""
    detail: str = ""


@dataclass
class DisplayProvenance:
    display_title: str
    started_at: str = ""
    initial_source: SourcePointer | None = None
    latest_source: SourcePointer | None = None
    agent_refs: list[str] = field(default_factory=list)


@dataclass
class ProgressEntry:
    date: str
    source: str
    update: str = ""
    status: str = ""


def strip_markdown(value: str) -> str:
    value = strip_wikilinks(value or "")
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("~~", "")
    value = re.sub(r"[*_`#>]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def table_cells(line: str) -> list[str]:
    return split_cells(line)


def header_value(text: str, label: str) -> str:
    pattern = re.compile(HEADER_RE_TEMPLATE.format(label=re.escape(label)), flags=re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def frontmatter_value(text: str, key: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        return ""
    match = re.search(rf"^{re.escape(key)}:\s*[\"']?(.+?)[\"']?\s*$", text[4:end], flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def display_title_from_title(value: str, fallback: str = "Untitled task") -> str:
    title = strip_markdown(value)
    title = re.sub(r"^[A-Z][A-Z0-9]+-\d{1,}[a-z]?\s*(?:[:\-\u2014]\s*)?", "", title).strip()
    title = re.sub(r"^20\d{2}-\d{2}-\d{2}\s*(?:[:\-\u2014]\s*)?", "", title).strip()
    title = re.split(r'\s+"', title, maxsplit=1)[0].strip()
    title = title.strip('"')
    title = re.split(r"\s+(?:\u2014|-)\s+", title, maxsplit=1)[0].strip()
    return title or fallback


def display_title_from_task_text(text: str, fallback: str = "Untitled task") -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return display_title_from_title(stripped[2:], fallback=fallback)
    return fallback


def parse_progress_entries(text: str) -> list[ProgressEntry]:
    entries: list[ProgressEntry] = []
    in_progress = False
    for line in text.splitlines():
        stripped = line.strip()
        if PROGRESS_HEADER_RE.match(stripped):
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
                )
            )
            continue

        cells = table_cells(stripped)
        if len(cells) >= 3 and DATE_RE.search(cells[0]) and cells[0].lower() != "date":
            entries.append(
                ProgressEntry(
                    date=strip_markdown(cells[0]),
                    source=strip_markdown(cells[1]),
                    update=strip_markdown(cells[2]),
                    status=strip_markdown(cells[3]) if len(cells) > 3 else "",
                )
            )
    return entries


def collect_agent_refs(text: str, extra_refs: list[str] | None = None) -> list[str]:
    refs = set(extra_refs or [])
    refs.update(ISSUE_ID_RE.findall(text or ""))
    for match in re.finditer(r"https://trello\.com/c/[A-Za-z0-9]+", text or ""):
        refs.add(match.group(0))
    return sorted(ref for ref in refs if ref)


def source_pointer_from_entry(entry: ProgressEntry) -> SourcePointer:
    return SourcePointer(label=entry.source or "Local tracker", date=entry.date, detail=entry.update)


def build_provenance(
    task_path: Path,
    *,
    fallback_title: str = "Untitled task",
    extra_refs: list[str] | None = None,
) -> DisplayProvenance:
    text = task_path.read_text(encoding="utf-8", errors="replace") if task_path.exists() else ""
    title = display_title_from_task_text(text, fallback=fallback_title)
    created = frontmatter_value(text, "created") or header_value(text, "Created")
    last_updated = frontmatter_value(text, "updated") or header_value(text, "Last Updated")
    progress_entries = parse_progress_entries(text)
    initial = source_pointer_from_entry(progress_entries[0]) if progress_entries else None
    latest = source_pointer_from_entry(progress_entries[-1]) if progress_entries else None
    started_at = created or (initial.date if initial else "")
    if initial is None and started_at:
        initial = SourcePointer(label="Local tracker", date=started_at)
    if latest is None and last_updated:
        latest = SourcePointer(label="Local tracker", date=last_updated)
    return DisplayProvenance(
        display_title=title,
        started_at=started_at,
        initial_source=initial,
        latest_source=latest,
        agent_refs=collect_agent_refs(text, extra_refs=extra_refs),
    )


def provenance_from_title(
    title: str,
    *,
    source: str = "Local tracker",
    date: str = "",
    agent_refs: list[str] | None = None,
) -> DisplayProvenance:
    pointer = SourcePointer(label=source, date=date)
    return DisplayProvenance(
        display_title=display_title_from_title(title),
        started_at=date,
        initial_source=pointer if source or date else None,
        latest_source=pointer if source or date else None,
        agent_refs=sorted(agent_refs or []),
    )


def format_source_pointer(pointer: SourcePointer | None) -> str:
    if pointer is None:
        return "no source recorded"
    label = strip_markdown(pointer.label) or "Local tracker"
    if pointer.date:
        return f"{label} on {pointer.date}"
    return label


def format_evidence(provenance: DisplayProvenance) -> str:
    return (
        f"{provenance.display_title}; "
        f"started from {format_source_pointer(provenance.initial_source)}; "
        f"latest progress from {format_source_pointer(provenance.latest_source)}."
    )


def scrub_visible_refs(text: str, known_titles: dict[str, str] | None = None) -> str:
    known_titles = known_titles or {}

    def replace_issue(match: re.Match[str]) -> str:
        ref = match.group(0)
        if ref in known_titles:
            return known_titles[ref]
        if TASK_ID_RE.fullmatch(ref):
            return "linked task"
        return "linked Jira item"

    cleaned = ISSUE_ID_RE.sub(replace_issue, text or "")
    cleaned = re.sub(r"https://trello\.com/c/[A-Za-z0-9]+", "linked Trello card", cleaned)
    return cleaned
