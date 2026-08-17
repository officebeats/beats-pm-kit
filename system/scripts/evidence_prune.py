#!/usr/bin/env python3
"""Prune oversized evidence sections in tracker notes.

Keeps the newest N (default 10) top-level bullet entries inside each
``## Evidence`` / ``## Evidence Log`` section of task and workstream notes and
moves the remainder verbatim to ``5. Trackers/archive/evidence/<note-stem>.md``
under a dated ``## Pruned <ISO date>`` heading. Archive files are append-only;
nothing is ever deleted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKERS = ROOT / "5. Trackers"
ARCHIVE_DIR = TRACKERS / "archive" / "evidence"
DEFAULT_LIMIT = 10

EVIDENCE_HEADING_RE = re.compile(r"^##\s+Evidence(\s+Log)?\b.*$")
HEADING_RE = re.compile(r"^(#{1,6})\s")
TOP_BULLET_RE = re.compile(r"^[-*]\s")
DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


@dataclass
class Entry:
    lines: list[str]  # verbatim lines: top-level bullet + nested continuation
    date: dt.date | None

    def text(self) -> str:
        return "\n".join(self.lines)


def parse_date(text: str) -> dt.date | None:
    for m in DATE_RE.finditer(text):
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
    return None


def find_evidence_sections(lines: list[str]) -> list[tuple[int, int]]:
    """Return (start, end) line-index ranges of evidence section bodies.

    ``start`` is the line after the ``## Evidence`` heading; ``end`` is the
    index of the next heading of level <= 2 (or EOF).
    """
    sections = []
    i = 0
    while i < len(lines):
        if EVIDENCE_HEADING_RE.match(lines[i]):
            j = i + 1
            while j < len(lines):
                m = HEADING_RE.match(lines[j])
                if m and len(m.group(1)) <= 2:
                    break
                j += 1
            sections.append((i + 1, j))
            i = j
        else:
            i += 1
    return sections


def parse_entries(lines: list[str], start: int, end: int):
    """Split section body into (prefix_chunks, entries).

    ``chunks`` is an ordered list of ("text", [lines]) or ("entry", Entry)
    preserving everything (blank lines, sub-headings) that is not part of a
    top-level bullet entry.
    """
    chunks: list[tuple[str, object]] = []
    i = start
    while i < end:
        line = lines[i]
        if TOP_BULLET_RE.match(line):
            entry_lines = [line]
            j = i + 1
            while j < end:
                nxt = lines[j]
                if TOP_BULLET_RE.match(nxt) or HEADING_RE.match(nxt):
                    break
                if nxt.strip() == "":
                    # blank line ends an entry only if followed by non-indented content
                    k = j + 1
                    if k < end and lines[k].startswith((" ", "\t")):
                        entry_lines.append(nxt)
                        j += 1
                        continue
                    break
                if nxt.startswith((" ", "\t")):
                    entry_lines.append(nxt)
                    j += 1
                    continue
                break
            chunks.append(("entry", Entry(entry_lines, parse_date("\n".join(entry_lines)))))
            i = j
        else:
            if chunks and chunks[-1][0] == "text":
                chunks[-1][1].append(line)  # type: ignore[union-attr]
            else:
                chunks.append(("text", [line]))
            i += 1
    return chunks


def select_kept(entries: list[Entry], limit: int) -> set[int]:
    """Return indices (into ``entries``) of the newest ``limit`` entries."""
    if len(entries) <= limit:
        return set(range(len(entries)))
    # Inherit dates for undated entries from the nearest preceding dated entry
    # in file order, so grouped/undated bullets stay with their neighbors.
    dates: list[dt.date | None] = []
    last: dt.date | None = None
    for e in entries:
        if e.date is not None:
            last = e.date
        dates.append(e.date if e.date is not None else last)
    # Detect file order from first/last parseable dates.
    dated = [d for d in dates if d is not None]
    newest_first = True
    if len(dated) >= 2 and dated[0] < dated[-1]:
        newest_first = False
    fallback = dt.date.min if newest_first else dt.date.max
    keyed = [
        (dates[idx] or fallback, -idx if newest_first else idx, idx)
        for idx in range(len(entries))
    ]
    keyed.sort(reverse=True)
    return {idx for _, _, idx in keyed[:limit]}


def prune_note(path: Path, limit: int, apply: bool, today: str):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    moved: list[Entry] = []
    new_lines: list[str] = []
    cursor = 0
    for start, end in find_evidence_sections(lines):
        new_lines.extend(lines[cursor:start])
        chunks = parse_entries(lines, start, end)
        entries = [c for kind, c in chunks if kind == "entry"]
        kept_idx = select_kept(entries, limit)  # type: ignore[arg-type]
        entry_no = 0
        for kind, payload in chunks:
            if kind == "text":
                new_lines.extend(payload)  # type: ignore[arg-type]
            else:
                if entry_no in kept_idx:
                    new_lines.extend(payload.lines)  # type: ignore[union-attr]
                else:
                    moved.append(payload)  # type: ignore[arg-type]
                entry_no += 1
        cursor = end
    new_lines.extend(lines[cursor:])
    if not moved:
        return 0
    if apply:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_path = ARCHIVE_DIR / f"{path.stem}.md"
        rel = path.relative_to(ROOT).as_posix()
        block = [f"\n## Pruned {today}\n", f"Source: {rel}\n\n"]
        block.extend(e.text() + "\n" for e in moved)
        header = "" if archive_path.exists() else f"# Evidence archive: {path.stem}\n"
        with archive_path.open("a", encoding="utf-8") as fh:
            fh.write(header + "".join(block))
        path.write_text("\n".join(new_lines), encoding="utf-8")
    return len(moved)


def iter_notes():
    for sub in ("tasks", "workstreams"):
        d = TRACKERS / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.startswith("_"):
                continue
            yield p


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="list what would move (default)")
    mode.add_argument("--apply", action="store_true", help="write changes and archive entries")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="entries kept per note (default 10)")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    args = parser.parse_args(argv)

    today = dt.date.today().isoformat()
    scanned = pruned = moved_total = 0
    details = []
    for path in iter_notes():
        scanned += 1
        moved = prune_note(path, args.limit, args.apply, today)
        if moved:
            pruned += 1
            moved_total += moved
            details.append((path.relative_to(ROOT).as_posix(), moved))

    summary = {
        "mode": "apply" if args.apply else "dry-run",
        "notes_scanned": scanned,
        "notes_pruned": pruned,
        "entries_moved": moved_total,
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for rel, n in details:
            verb = "moved" if args.apply else "would move"
            print(f"{rel}: {verb} {n} entries")
        print(
            f"{summary['mode']}: scanned {scanned} notes, "
            f"pruned {pruned}, entries moved {moved_total}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
