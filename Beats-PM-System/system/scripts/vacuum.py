"""
Vacuum Script (Centrifuge Protocol)

Archives completed tasks from tracker files to keep them clean and organized.
Moves items marked as completed to the archive directory.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Path setup
CURRENT_FILE = Path(__file__).resolve()
# SYSTEM_ROOT is the directory containing the 'system' package (e.g., /path/to/system)
SYSTEM_ROOT = CURRENT_FILE.parent.parent.parent
# BRAIN_ROOT is the root of the entire project (e.g., /path/to)
BRAIN_ROOT = SYSTEM_ROOT.parent

# Add SYSTEM_ROOT to path for imports
sys.path.insert(0, str(SYSTEM_ROOT))

from system.utils.ui import print_info, print_success
from system.utils.filesystem import (
    ensure_directory,
    file_exists, # These are still used in the original logic, but the refactor replaces them with pathlib methods
    read_file,   # The refactor replaces these with direct file operations
    write_file,
    append_file,
    copy_file,
    delete_file,
)

# Configuration
TRACKERS_DIR = BRAIN_ROOT / "5. Trackers"
ARCHIVE_DIR = TRACKERS_DIR / "archive"


def ensure_archive() -> bool:
    """Ensure the archive directory exists."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    return ARCHIVE_DIR.is_dir()


def vacuum_file(filename: str) -> None:
    """
    Archive completed items from a tracker file.

    Args:
        filename: Name of the tracker file (relative to TRACKERS_DIR)
    """
    filepath = TRACKERS_DIR / filename

    if not filepath.is_file():
        print_info(f"File not found: {filename}")
        return

    print_info(f"Vacuuming {filename}...")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print_info(f"Failed to read {filename}: {e}")
        return

    lines = content.splitlines()

    active_lines: List[str] = []
    archived_lines: List[str] = []

    # Separate active and completed items
    for line in lines:
        if line.strip().startswith("- [x]"):
            archived_lines.append(line)
        else:
            active_lines.append(line)

    if not archived_lines:
        print_info("  No completed items found.")
        return

    # Write back active items
    active_content = "\n".join(active_lines)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(active_content)
        print_success(f"  Cleaned {filename}")
    except Exception as e:
        print_info(f"  Failed to write back to {filename}: {e}")
        return

    # Append to archive with Micro-Summary
    timestamp = datetime.now().strftime("%Y-%m")
    archive_file = ARCHIVE_DIR / f"archive_{timestamp}_{filename}"

    # Generate Micro-Summary (Heuristic: extract first few words of each task)
    summary_lines = [
        f"- {line.replace('- [x]', '').strip()[:50]}..."
        for line in archived_lines
        if len(line) > 10
    ]

    archive_header = f"\n\n--- Archived on {datetime.now()} ---\n"
    archive_header += f"Summary: Completed {len(archived_lines)} items including: {', '.join(summary_lines[:3])}\n"

    archive_content = archive_header + "\n".join(archived_lines)

    try:
        with open(archive_file, "a", encoding="utf-8") as f:
            f.write(archive_content)
        print_success(f"  Moved {len(archived_lines)} items to {archive_file.name}")
    except Exception as e:
        print_info(f"  Failed to archive items: {e}")


def archive_transcripts() -> None:
    """
    Archive old transcripts based on tiered memory (Hot/Warm/Cold).
    """
    meetings_dir = BRAIN_ROOT / "3. Meetings"
    transcripts_dir = meetings_dir / "transcripts"
    archive_dir = meetings_dir / "archive"

    # Ensure directories exist
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    print_info("\nChecking for old transcripts...")

    # 30 days in seconds
    THIRTY_DAYS = 30 * 24 * 60 * 60
    ONE_YEAR = 365 * 24 * 60 * 60
    now = time.time()

    if not transcripts_dir.is_dir():
        return

    for filepath in transcripts_dir.iterdir():
        if not filepath.is_file():
            continue

        file_age = now - filepath.stat().st_mtime

        if file_age > ONE_YEAR:
            # Move to Cold (Archive)
            dst = archive_dir / filepath.name
            try:
                filepath.replace(dst) # pathlib's replace is an atomic move
                print_success(f"  Archived (Cold): {filepath.name}")
            except Exception as e:
                print_info(f"  Failed to archive {filepath.name}: {e}")


def main() -> None:
    """Main entry point for vacuum script."""
    if not ensure_archive():
        print_info("Failed to access archive directory")
        return

    # Get list of files to clean
    targets: List[str] = ["tasks.md", "bugs-master.md", "boss-requests.md"]

    print_info("Starting vacuum process...")

    for target in targets:
        vacuum_file(target)

    # Archive old transcripts
    archive_transcripts()

    print_success("Vacuum complete!")


if __name__ == "__main__":
    main()
