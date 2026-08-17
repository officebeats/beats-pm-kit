#!/usr/bin/env python3
"""Advisory linter for the SKILL.md Quick Path convention.

Scans every `.agent/skills/*/SKILL.md` and reports, per skill:

- ``has_quick_path``: whether the body contains a ``## Quick Path`` section.
- ``quick_path_chars``: character count of the Quick Path section content
  (heading line excluded).
- ``body_bytes``: UTF-8 bytes of the SKILL.md document *excluding* the Quick
  Path section (frontmatter included). Excluding the Quick Path keeps the
  metric stable: adding the section never changes whether a skill is required
  to carry one.
- ``description_chars``: length of the frontmatter ``description`` value.

``--report`` (default) always exits 0. ``--strict`` exits 1 when any skill
whose ``body_bytes`` exceeds ``REQUIRED_BODY_BYTES`` lacks a compliant Quick
Path: present, the first H2 heading in the body, and at most
``QUICK_PATH_MAX_CHARS`` characters.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts.markdown_humanizer import split_frontmatter  # noqa: E402

SKILLS_DIR = ROOT / ".agent" / "skills"
QUICK_PATH_HEADING = "## Quick Path"
# Quick Path budget: roughly 300 tokens.
QUICK_PATH_MAX_CHARS = 1200
# A skill must carry a Quick Path when body_bytes exceeds this constant.
# Chosen 2026-08-17 so that exactly the eight migrated skills are covered:
# the smallest migrated skill (task-manager) measured 5689 body_bytes and the
# largest unmigrated skill (data-analytics) measured 5317.
REQUIRED_BODY_BYTES = 5500


def analyze_text(text: str) -> dict:
    """Analyze one SKILL.md document. Pure; used by tests."""
    _, body, meta = split_frontmatter(text)
    frontmatter_bytes = len(text.encode("utf-8")) - len(body.encode("utf-8"))

    lines = body.split("\n")
    kept: list[str] = []
    quick_path_lines: list[str] = []
    first_h2: str | None = None
    in_quick_path = False
    for line in lines:
        if line.startswith("## "):
            if first_h2 is None:
                first_h2 = line.strip()
            in_quick_path = line.strip() == QUICK_PATH_HEADING
            if in_quick_path:
                continue
        if in_quick_path:
            quick_path_lines.append(line)
        else:
            kept.append(line)

    quick_path_content = "\n".join(quick_path_lines).strip("\n")
    has_quick_path = first_h2 == QUICK_PATH_HEADING or any(
        line.strip() == QUICK_PATH_HEADING for line in lines
    )
    quick_path_chars = len(quick_path_content) if has_quick_path else 0
    body_bytes = frontmatter_bytes + len("\n".join(kept).encode("utf-8"))
    required = body_bytes > REQUIRED_BODY_BYTES
    compliant = (
        has_quick_path
        and first_h2 == QUICK_PATH_HEADING
        and 0 < quick_path_chars <= QUICK_PATH_MAX_CHARS
    )
    return {
        "has_quick_path": has_quick_path,
        "quick_path_first": first_h2 == QUICK_PATH_HEADING,
        "quick_path_chars": quick_path_chars,
        "body_bytes": body_bytes,
        "description_chars": len(meta.get("description", "")),
        "required": required,
        "compliant": compliant,
    }


def scan_skills(skills_dir: Path) -> list[dict]:
    results = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        record = analyze_text(skill_file.read_text(encoding="utf-8"))
        record["skill"] = skill_file.parent.name
        results.append(record)
    return results


def violations(results: list[dict]) -> list[dict]:
    return [row for row in results if row["required"] and not row["compliant"]]


def render_report(results: list[dict]) -> str:
    lines = [
        f"{'skill':<32} {'quick_path':>10} {'qp_chars':>8} {'body_bytes':>10} "
        f"{'desc':>5} {'required':>8} {'ok':>3}"
    ]
    for row in sorted(results, key=lambda r: -r["body_bytes"]):
        lines.append(
            f"{row['skill']:<32} {('yes' if row['has_quick_path'] else 'no'):>10} "
            f"{row['quick_path_chars']:>8} {row['body_bytes']:>10} "
            f"{row['description_chars']:>5} {('yes' if row['required'] else 'no'):>8} "
            f"{('yes' if not row['required'] or row['compliant'] else 'NO'):>3}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="Kit root override")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="Report only; exit 0 (default)")
    mode.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when a required skill lacks a compliant Quick Path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    skills_dir = (args.root / ".agent" / "skills") if args.root else SKILLS_DIR
    if not skills_dir.is_dir():
        print(f"skills directory not found: {skills_dir}", file=sys.stderr)
        return 2
    results = scan_skills(skills_dir)
    failing = violations(results)
    if args.json:
        print(
            json.dumps(
                {
                    "threshold_body_bytes": REQUIRED_BODY_BYTES,
                    "max_quick_path_chars": QUICK_PATH_MAX_CHARS,
                    "skills": results,
                    "violations": [row["skill"] for row in failing],
                },
                indent=2,
            )
        )
    else:
        print(render_report(results))
        if failing:
            print(
                f"\n{len(failing)} required skill(s) missing a compliant Quick Path: "
                + ", ".join(row["skill"] for row in failing)
            )
    if args.strict and failing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
