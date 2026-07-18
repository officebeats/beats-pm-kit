#!/usr/bin/env python3
"""Dependency-free compatibility shim for the retired experimental CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {
    "discover": ".agent/workflows/discover.md",
    "retro": ".agent/workflows/retro.md",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["dashboard", *sorted(WORKFLOWS)])
    args = parser.parse_args(argv)
    print("This is a deprecated compatibility shim; it never selects or calls a model provider.")
    if args.command == "dashboard":
        print("Use the canonical Markdown task index at `5. Trackers/TASK_MASTER.md`.")
        print("The optional local dashboard remains under `system/dashboard/`.")
        return 0
    workflow = WORKFLOWS[args.command]
    print(f"Run `/{args.command}` in the active AI runtime by loading `{workflow}`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
