#!/usr/bin/env python3
"""Build the cached task index used by fast task-manager intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from system.scripts.task_intake_fast import DEFAULT_ROOT, build_task_index, write_task_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Build .agent/cache/task_index.json")
    parser.add_argument("--repo", default=str(DEFAULT_ROOT), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print index JSON")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    index = build_task_index(root)
    path = write_task_index(root, index)
    if args.json:
        print(json.dumps(index, indent=2, sort_keys=True))
    else:
        print(f"Wrote {path}")
        print(f"Indexed {len(index.get('tasks', []))} tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
