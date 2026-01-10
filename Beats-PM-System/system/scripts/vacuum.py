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
from utils.filesystem import (
    ensure_directory, file_exists, read_file, write_file, append_file,
    directory_exists, copy_file, delete_file
)
from utils.config import get_config


# Configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TRACKERS_DIR = os.path.join(ROOT_DIR, "5. Trackers")
ARCHIVE_DIR = os.path.join(TRACKERS_DIR, "archive")


def ensure_archive() -> bool:
    """Ensure the archive directory exists."""
    return ensure_directory(ARCHIVE_DIR)


def vacuum_file(filename: str) -> None:
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
    
    # Append to archive with Micro-Summary
    timestamp = datetime.datetime.now().strftime("%Y-%m")
    archive_file = os.path.join(ARCHIVE_DIR, f"archive_{timestamp}_{filename}")
    
    # Generate Micro-Summary (Heuristic: extract first few words of each task)
    summary_lines = [f"- {line.replace('- [x]', '').strip()[:50]}..." for line in archived_lines if len(line) > 10]
    
    archive_header = f"\n\n--- Archived on {datetime.datetime.now()} ---\n"
    archive_header += f"Summary: Completed {len(archived_lines)} items including: {', '.join(summary_lines[:3])}\n"
    
    archive_content = archive_header + '\n'.join(archived_lines)
    
    if append_file(archive_file, archive_content):
        print_success(f"  Moved {len(archived_lines)} items to {os.path.basename(archive_file)}")
    else:
        print_info(f"  Failed to archive items")


def archive_transcripts() -> None:
    """
    Archive old transcripts based on tiered memory (Hot/Warm/Cold).
    """
    import time
    
    meetings_dir = os.path.join(ROOT_DIR, "3. Meetings")
    transcripts_dir = os.path.join(meetings_dir, "transcripts")
    summaries_dir = os.path.join(meetings_dir, "summaries")
    archive_dir = os.path.join(meetings_dir, "archive")
    
    # Ensure directories exist
    ensure_directory(transcripts_dir)
    ensure_directory(summaries_dir)
    ensure_directory(archive_dir)
    
    print_info("\nChecking for old transcripts...")
    
    # 30 days in seconds
    THIRTY_DAYS = 30 * 24 * 60 * 60
    ONE_YEAR = 365 * 24 * 60 * 60
    now = time.time()
    
    # Check transcripts (Hot -> Warm)
    if not directory_exists(transcripts_dir):
        return

    transcripts = [f for f in os.listdir(transcripts_dir) if os.path.isfile(os.path.join(transcripts_dir, f))]
    
    for filename in transcripts:
        filepath = os.path.join(transcripts_dir, filename)
        file_age = now - os.path.getmtime(filepath)
        
        if file_age > THIRTY_DAYS:
            # Move to Warm (Summaries) - In a real scenario we'd summarize, but here we just move to indicate 'processed'
            # Or better, check if summary exists. If not, maybe we keep it? 
            # For this MVP, let's just move to archive if > 365 days, and maybe WARN if > 30 days without summary.
            pass
            
        if file_age > ONE_YEAR:
            # Move to Cold (Archive)
            dst = os.path.join(archive_dir, filename)
            if copy_file(filepath, dst):
                delete_file(filepath)
                print_success(f"  Archived (Cold): {filename}")


def main() -> None:
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
        
    # Archive old transcripts
    archive_transcripts()
    
    print_success("Vacuum complete!")


if __name__ == "__main__":
    main()
