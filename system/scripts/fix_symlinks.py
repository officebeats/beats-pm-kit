"""
Fix Symlinks Script
Re-creates all .claude/, .gemini/, .kilocode/ symlinks pointing to .agent/.

Uses RELATIVE symlinks (not absolute) so the repo stays portable across
machines and clone locations.

Usage:
    python3 system/scripts/fix_symlinks.py
"""

import os
import sys
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent   # system/
BRAIN_ROOT = SYSTEM_ROOT.parent            # beats-pm-antigravity-brain/

# Define all symlinks to create/repair
# Format: (link_path, target_path) — both relative to BRAIN_ROOT
SYMLINKS = [
    # .claude/
    (".claude/CLAUDE.md",    ".agent/rules/GEMINI.md"),
    (".claude/commands",     ".agent/workflows"),
    # .gemini/
    (".gemini/GEMINI.md",    ".agent/rules/GEMINI.md"),
    (".gemini/agents",       ".agent/agents"),
    (".gemini/skills",       ".agent/skills"),
    (".gemini/templates",    ".agent/templates"),
    (".gemini/workflows",    ".agent/workflows"),
    # .kilocode/
    (".kilocode/agents",     ".agent/agents"),
    (".kilocode/rules",      ".agent/rules"),
    (".kilocode/skills",     ".agent/skills"),
    (".kilocode/templates",  ".agent/templates"),
    (".kilocode/workflows",  ".agent/workflows"),
]


def _create_relative_symlink(link_path: Path, target_path: Path) -> None:
    """
    Create a relative symlink at link_path pointing to target_path.
    Both paths are resolved relative to BRAIN_ROOT.

    Args:
        link_path:   Where the symlink will live (absolute or relative to BRAIN_ROOT).
        target_path: What the symlink points at (absolute or relative to BRAIN_ROOT).
    """
    abs_link = BRAIN_ROOT / link_path
    abs_target = BRAIN_ROOT / target_path

    # Ensure the target actually exists before linking
    if not abs_target.exists():
        print(f"  ⚠️  Target missing, skipping: {target_path}")
        return

    # Compute the relative path from the link's parent directory to the target
    rel_target = os.path.relpath(abs_target, start=abs_link.parent)

    # Remove existing link or broken link
    if abs_link.is_symlink() or abs_link.exists():
        abs_link.unlink()
        print(f"  🗑️  Removed: {link_path}")

    # Ensure parent directory exists
    abs_link.parent.mkdir(parents=True, exist_ok=True)

    # Create the symlink
    abs_link.symlink_to(rel_target)
    print(f"  ✅  Created: {link_path} → {rel_target}")


def main() -> None:
    print(f"\n🔗 Fixing symlinks in: {BRAIN_ROOT}\n")
    for link_str, target_str in SYMLINKS:
        _create_relative_symlink(Path(link_str), Path(target_str))
    print("\n✅  All symlinks repaired.\n")


if __name__ == "__main__":
    main()
