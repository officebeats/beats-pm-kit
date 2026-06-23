"""Compatibility wrapper for runtime adapter regeneration.

Older releases used this script to repair a web of tracked symlinks. The repo now
keeps `.agent/` canonical and generates runtime adapters locally through
`sync_cli_adapters.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    print("Regenerating local runtime adapters from .agent/...")
    return subprocess.run(
        [sys.executable, "system/scripts/sync_cli_adapters.py"],
        cwd=ROOT,
        check=False,
        text=True,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
