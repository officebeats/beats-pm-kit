"""
Vacuum Script

Archives completed tasks from tracker files to keep them clean and organized.
Moves items marked as completed to the archive directory.
"""

import sys
import os
import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import print_info, print_success
from utils.filesystem import ensure_directory, file_exists, read_file, write_file, append_file
from utils.config import get_config


# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TRACKERS_DIR = os.path.join(ROOT_DIR, "5. Trackers")
ARCHIVE_DIR = os.path.join(TRACKERS_DIR, "archive")


def ensure_archive():
    """Ensure the archive directory exists."""
    return ensure_directory(ARCHIVE_DIR)


def vacuum_file(filename):
    """
    Archive completed items from a tracker file.
    
    Args:
        filename: Name of the tracker file to vacuum
    """
    filepath = os.path.join(TRACKERS_DIR, filename)
    
    if not file_exists(filepath):
        print_info(f"File not found: {filename}")
        return
    
    print_info(f"Vacuuming {filename}...")
    
    content = read_file(filepath)
    if content is None:
        print_info(f"Failed to read {filename}")
        return
    
    lines = content.splitlines()
    
    active_lines = []
    archived_lines = []
    
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
    active_content = '\n'.join(active_lines)
    if write_file(filepath, active_content):
        print_success(f"  Cleaned {filename}")
    else:
        print_info(f"  Failed to write back to {filename}")
        return
    
    # Append to archive
    timestamp = datetime.datetime.now().strftime("%Y-%m")
    archive_file = os.path.join(ARCHIVE_DIR, f"archive_{timestamp}_{filename}")
    
    archive_header = f"\n\n--- Archived on {datetime.datetime.now()} ---\n"
    archive_content = archive_header + '\n'.join(archived_lines)
    
    if append_file(archive_file, archive_content):
        print_success(f"  Moved {len(archived_lines)} items to {os.path.basename(archive_file)}")
    else:
        print_info(f"  Failed to archive items")


def main():
    """Main entry point for vacuum script."""
    if not ensure_archive():
        print_info("Failed to create archive directory")
        return
    
    # Get list of files to clean from configuration
    targets = [
        "tasks.md",
        "bugs-master.md",
        "boss-requests.md"
    ]
    
    print_info("Starting vacuum process...")
    
    for target in targets:
        vacuum_file(target)
    
    print_success("Vacuum complete!")


if __name__ == "__main__":
    main()
