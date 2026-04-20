"""
Install versioned git hooks for runtime adapter synchronization.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = ROOT / ".githooks"
HOOK_NAMES = ["pre-commit", "post-merge", "post-checkout", "post-rewrite"]


def ensure_executable(path: Path):
    """Mark a hook file executable."""
    current_mode = path.stat().st_mode
    path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    if not (ROOT / ".git").exists():
        print("Not a git repository. Skipping hook installation.")
        return 0

    for hook_name in HOOK_NAMES:
        hook_path = HOOKS_DIR / hook_name
        if not hook_path.exists():
            print(f"Missing hook file: {hook_path}")
            return 1
        ensure_executable(hook_path)

    subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"],
        cwd=ROOT,
        check=True,
    )
    print("Git hooks installed via core.hooksPath=.githooks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
