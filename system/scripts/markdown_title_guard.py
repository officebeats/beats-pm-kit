#!/usr/bin/env python3
"""Require a human-readable title in every tracked Markdown document."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ID_ONLY_RE = re.compile(r"^(?:[A-Z][A-Z0-9]+-\d{2,}|[0-9a-f-]{12,})$", re.IGNORECASE)
ID_ONLY_FILENAME_RE = re.compile(r"^(?:(?:TASK|PLAN|PRD|SPEC|BUG|TRANSCRIPT|MEETING|CALL|DOC|ITEM)-\d{2,}|[0-9a-f-]{12,})\.md$", re.IGNORECASE)

def tracked_markdown(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0:
        return [root / line for line in result.stdout.splitlines() if line.strip() and "fixtures" not in line]
    return [path for path in root.rglob("*.md") if ".git" not in path.parts and "node_modules" not in path.parts and "fixtures" not in path.parts]


def document_title(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            match = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text[4:end], flags=re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def problems(root: Path = ROOT) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in tracked_markdown(root):
        if not path.exists():
            continue
        filename = path.name
        relative = path.relative_to(root).as_posix()
        if ID_ONLY_FILENAME_RE.fullmatch(filename):
            issues.append({"path": relative, "problem": f"ID-only filename: {filename} (must be human-readable kebab-case slug)"})
        title = document_title(path.read_text(encoding="utf-8", errors="replace"))
        if not title:
            issues.append({"path": relative, "problem": "missing title or H1"})
        elif ID_ONLY_RE.fullmatch(title):
            issues.append({"path": relative, "problem": f"ID-only title: {title}"})
    return issues

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    issues = problems(root)
    payload = {"ok": not issues, "checked": len(tracked_markdown(root)), "issues": issues}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Markdown title guard: {'PASS' if not issues else 'FAIL'}")
        for issue in issues:
            print(f"- {issue['path']}: {issue['problem']}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
