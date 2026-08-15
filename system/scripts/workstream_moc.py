#!/usr/bin/env python3
"""Build workstream MOCs from the frontmatter written by workstream_backfill.py.

Converts the single 720-link "Meeting Evidence" star into one constellation per
workstream. Each workstream note gets an auto-managed, delimited section holding
wikilinks to its member notes, grouped by type. Human-written prose above the
marker is never touched.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
WS_DIR = VAULT / "5. Trackers" / "workstreams"

BEGIN = "<!-- BEGIN AUTO-EVIDENCE (managed by workstream_moc.py) -->"
END = "<!-- END AUTO-EVIDENCE -->"

CONTENT_DIRS = [
    "0. Incoming", "1. Company", "2. Products", "3. Meetings",
    "4. People", "5. Trackers", "6. SOPs", "7. Partners", "8. Clients",
]
SKIP_PARTS = {"archive", "node_modules", "markdown-label-backups"}

TYPE_ORDER = ["decision", "summary", "report", "transcript", "evidence",
              "product", "task", "brief", "deck", "person", "tracker", "note"]


def read_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def iter_notes():
    for d in CONTENT_DIRS:
        base = VAULT / d
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            rel_parts = path.relative_to(VAULT).parts
            if set(rel_parts) & SKIP_PARTS:
                continue
            if any(p.startswith(".") for p in rel_parts):
                continue
            yield path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    members: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
    for path in iter_notes():
        text = path.read_text(encoding="utf-8", errors="ignore")[:800]
        fm = read_frontmatter(text)
        ws = fm.get("workstream")
        if not ws:
            continue
        if path.parent == WS_DIR:          # don't link a workstream note to itself
            continue
        members[ws][fm.get("type", "note")].append(path)

    total = 0
    for ws_path in sorted(WS_DIR.glob("*.md")):
        if ws_path.name == "_TEMPLATE.md":
            continue
        slug = ws_path.stem
        by_type = members.get(slug, {})
        count = sum(len(v) for v in by_type.values())

        lines = [BEGIN, "", f"## Evidence ({count} notes)", ""]
        if not count:
            lines.append("_No classified evidence notes yet._")
        for t in TYPE_ORDER + sorted(set(by_type) - set(TYPE_ORDER)):
            paths = by_type.get(t)
            if not paths:
                continue
            lines.append(f"### {t.title()} ({len(paths)})")
            lines.append("")
            for p in sorted(paths, key=lambda x: x.name, reverse=True):
                # Wikilink by vault-relative path minus .md so Obsidian resolves it.
                target = p.relative_to(VAULT).as_posix()[:-3]
                lines.append(f"- [[{target}|{p.stem}]]")
            lines.append("")
        lines.append(END)
        block = "\n".join(lines) + "\n"

        original = ws_path.read_text(encoding="utf-8", errors="ignore")
        if BEGIN in original and END in original:
            new = re.sub(
                re.escape(BEGIN) + r".*?" + re.escape(END),
                block.rstrip("\n"),
                original,
                flags=re.S,
            )
        else:
            new = original.rstrip("\n") + "\n\n" + block

        print(f"{slug:38s} {count:4d} evidence notes")
        total += count
        if args.apply:
            ws_path.write_text(new, encoding="utf-8")

    print(f"\ntotal evidence links across {len(list(WS_DIR.glob('*.md'))) - 1} MOCs: {total}")
    print("APPLIED" if args.apply else "DRY RUN (no files modified)")


if __name__ == "__main__":
    main()
