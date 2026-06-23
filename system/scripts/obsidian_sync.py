#!/usr/bin/env python3
"""
Backward-compatible wrapper for the Obsidian bridge.

The old command shape still works:
    python system/scripts/obsidian_sync.py --dry-run
    python system/scripts/obsidian_sync.py --folder 3 --clean

New functionality is available through:
    python system/scripts/obsidian_bridge.py status
    python system/scripts/obsidian_bridge.py configure
    python system/scripts/obsidian_bridge.py sync --apply
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.scripts.obsidian_bridge import main as bridge_main


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if args and args[0] in {"status", "configure", "open", "sync", "mcp-template"}:
        return bridge_main(args)
    translated = ["sync"]
    if "--dry-run" not in args and "--apply" not in args:
        translated.append("--apply")
    translated.extend(args)
    return bridge_main(translated)


if __name__ == "__main__":
    sys.exit(main())
