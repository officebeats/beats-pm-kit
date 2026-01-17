"""
System Integrity & Structure Enforcement
Antigravity Native Protocol

This script ensures that the actual file system structure matches the 
Canonical Schema defined in config.json.

It is "Self-Healing":
1. Identifies files in root that belong in subfolders.
2. Moves them automatically.
3. Cleans up empty legacy folders.
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import print_cyan, print_green, print_yellow, print_warning, print_success
from utils.config import get_root_directory
from utils.filesystem import ensure_directory

# Schema Definition: File Pattern -> Target Folder (Relative to Root)
# This allows us to sweep the root and organize files based on their naming convention or type.
MIGRATION_MAP: Dict[str, str] = {
    # Documentation & Specs
    "PRD-*.md": "2. Products/specs",
    "SPEC-*.md": "2. Products/specs",
    
    # Meeting Notes & Transcripts
    "TRANSCRIPT-*.md": "3. Meetings/transcripts",
    "MEETING-*.md": "3. Meetings/notes",
    "Call-*.md": "3. Meetings/notes",
    
    # Trackers (Ensure they stay in 5. Trackers or subfolders)
    "BUG-*.md": "5. Trackers/bugs",
    "TASK-*.md": "5. Trackers", 
    "PROJECT-*.md": "5. Trackers/projects",
    
    # Artifacts
    "*.png": "0. Incoming/images",
    "*.jpg": "0. Incoming/images",
    "*.jpeg": "0. Incoming/images",
    "*.pdf": "0. Incoming/files",
    "*.csv": "0. Incoming/files",
}

IGNORE_LIST = [
    "README.md", "KERNEL.md", "SETTINGS.md", "STATUS.md", "GEMINI.md", "SESSION_MEMORY.md",
    "requirements.txt", ".gitignore", ".gitattributes", ".antigravityignore",
    "package.json", "package-lock.json"
]

def scan_and_migrate(root: Path):
    """Scans the root directory and moves loose files to their canonical homes."""
    print_cyan("\n🏗️  Enforcing System Architecture...")
    
    # Ensure targets exist
    for target in MIGRATION_MAP.values():
        ensure_directory(str(root / target))

    count = 0
    
    # Scan Root Only (Depth 0) of files to move
    # We do not want to recursively mess up existing structures, just clean the 'Desktop' (Root)
    for file in root.iterdir():
        if file.is_dir():
            continue
            
        if file.name in IGNORE_LIST:
            continue
            
        # Check patterns
        moved = False
        import fnmatch
        
        for pattern, target_relative in MIGRATION_MAP.items():
            if fnmatch.fnmatch(file.name, pattern):
                target_dir = root / target_relative
                target_path = target_dir / file.name
                
                # Collision handling
                if target_path.exists():
                    timestamp = int(os.path.getmtime(file))
                    target_path = target_dir / f"{file.stem}_{timestamp}{file.suffix}"
                    
                print_yellow(f"  > Moving {file.name} -> {target_relative}/")
                try:
                    shutil.move(str(file), str(target_path))
                    count += 1
                    moved = True
                    break
                except Exception as e:
                    print_warning(f"Failed to move {file.name}: {e}")
        
        # Fallback: Move unknown .md files to '0. Incoming' if strictly configured? 
        # For now, we leave unknown files alone to be safe.

    if count > 0:
        print_success(f"Organized {count} loose files.")
    else:
        print_green("  System structure is clean.")

def cleanup_legacy_folders(root: Path):
    """Removes known legacy folders if empty."""
    legacy_candidates = [
        "tests", # The one we deleted earlier, but good to keep in list
        "tmp",
        ".gemini", # Legacy folder
        "logs"
    ]
    
    for folder in legacy_candidates:
        path = root / folder
        if path.exists() and path.is_dir():
            # Check if empty
            if not any(path.iterdir()):
                try:
                    path.rmdir()
                    print_green(f"  Removed empty legacy folder: {folder}/")
                except:
                    pass

def main():
    root = Path(get_root_directory())
    scan_and_migrate(root)
    cleanup_legacy_folders(root)

if __name__ == "__main__":
    main()
