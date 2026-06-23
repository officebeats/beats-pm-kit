"""
Vacuum Script (Centrifuge Protocol)

Archives completed tasks and manages the Tiered Memory System (Hot/Warm/Cold).
Optimized for speed and long-term retrieval.
"""

import sys
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Path setup (MUST be before 'system.*' imports)
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent  # system/
BRAIN_ROOT = SYSTEM_ROOT.parent           # brain root/
sys.path.insert(0, str(BRAIN_ROOT))

# Centralized Config
from system.scripts import sys_config
from system.scripts.root_cleaner import clean_root

# Configuration
TRACKERS_DIR = BRAIN_ROOT / "5. Trackers"
ARCHIVE_DIR = TRACKERS_DIR / "archive"
MEETINGS_DIR = BRAIN_ROOT / "3. Meetings"

def ensure_dirs():
    """Ensure all tiered memory directories exist."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    (MEETINGS_DIR / "transcripts").mkdir(parents=True, exist_ok=True)
    (MEETINGS_DIR / "summaries").mkdir(parents=True, exist_ok=True)
    (MEETINGS_DIR / "archive").mkdir(parents=True, exist_ok=True)

def update_index(entry: str, category: str):
    """Append a retrievable entry to the Global Archive Index."""
    index_file = ARCHIVE_DIR / "INDEX.md"
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    if not index_file.exists():
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# Global Archive Index\n\n| Date | Category | Summary | Location |\n|---|---|---|---|\n")
            
    row = f"| {timestamp} | {category} | {entry} | `archive/` |\n"
    
    with open(index_file, "a", encoding="utf-8") as f:
        f.write(row)

def vacuum_tracker(filename: str) -> int:
    """
    Move completed items to a yearly archive file.
    Returns count of moved items.
    """
    filepath = TRACKERS_DIR / filename
    if not filepath.exists():
        return 0

    print(f"  Scanning {filename}...", end=" ")
    
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    active = []
    completed = []

    for line in lines:
        if line.strip().startswith("- [x]"):
            completed.append(line)
        else:
            active.append(line)

    if not completed:
        print("Clean.")
        return 0

    # Write Active
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(active)

    # Appending to Yearly Archive
    year = datetime.now().year
    archive_file = ARCHIVE_DIR / f"archive_{year}_{filename}"
    
    header = f"\n\n### Vacuumed on {datetime.now().strftime('%Y-%m-%d')}\n"
    
    with open(archive_file, "a", encoding="utf-8") as f:
        f.write(header)
        f.writelines(completed)

    print(f"Moved {len(completed)} items to {archive_file.name}")
    
    # Update Index with a summary
    summary = f"Archived {len(completed)} items from {filename}"
    update_index(summary, "Tracker")
    
    return len(completed)

from system.scripts import kernel_utils
import subprocess
import os

# Import DB Bridge for Transcript Fetching
from system.scripts import db_bridge
# Import File Organizer for Universal Processing
from system.scripts import file_organizer
# Import Librarian for Warm Tier Memory
from system.scripts import librarian

def clean_skeleton():
    """
    Analyze the repo skeleton and preview root cleanup actions.
    """
    print("\n--- 🦴 Skeleton Cleanup (Senior Engineer Audit) ---")
    
    issues_found = 0

    actions = clean_root(BRAIN_ROOT, apply=False)
    if actions:
        print(f"  ⚠️  Root cleaner would take {len(actions)} action(s). Run `python3 system/scripts/root_cleaner.py --apply` to apply.")
        issues_found += len(actions)
    else:
        print("  ✅ Root files: All recognized")

    # Check for Empty Directories at Root
    empty_dirs = []
    for item in BRAIN_ROOT.iterdir():
        if item.is_dir() and item.name not in [".git", ".pytest_cache"]:
            try:
                contents = list(item.iterdir())
                # Only flag if truly empty (no files, no subdirs)
                if len(contents) == 0:
                    empty_dirs.append(item.name)
            except PermissionError:
                pass
    
    if empty_dirs:
        print(f"  ⚠️  Empty directories at root: {empty_dirs}")
        issues_found += len(empty_dirs)
    
    # Hierarchical Integrity Audit (Folders 1, 2, 4)
    print("  🔍 Auditing Hierarchical Integrity...")
    monitored_folders = ["1. Company", "2. Products", "4. People"]
    for folder in monitored_folders:
        folder_path = BRAIN_ROOT / folder
        if not folder_path.exists():
            continue
            
        for entity in folder_path.iterdir():
            if entity.is_dir() and not entity.name.startswith("."):
                # Profile Exception: Check for loose files that AREN'T PROFILE.md or stakeholders.md
                loose_files = []
                allowed_at_entity_root = ["PROFILE.md", "stakeholders.md", "STAKEHOLDER_MAP.md", "SENTIMENT_LOG.md", ".gitkeep"]
                allowed_subdirs = ["Profiles"] # Allow Profiles folder for people
                
                for item in entity.iterdir():
                    if item.is_file():
                        if item.name not in allowed_at_entity_root:
                            loose_files.append(item.name)
                    elif item.is_dir():
                        # Only allow Product subfolders or whitelisted subdirs
                        pass
                
                if loose_files:
                    print(f"  🛑 SLOPPY ALERT: Loose files in {folder}/{entity.name}: {loose_files}")
                    issues_found += len(loose_files)
    
    if issues_found == 0:
        print("  🎯 Skeleton is lean and optimized.")
    else:
        print(f"  📋 Found {issues_found} items that may need attention.")
    
    return issues_found

def clean_repo_structure():
    """
    Apply shared root cleanup and regenerate generated local indices.
    """
    print("\n--- 🏗️  Repo Structure Cleanup ---")

    actions = clean_root(BRAIN_ROOT, apply=True)
    for action in actions:
        if action.destination:
            print(f"  moved: {action.path} -> {action.destination}")
        else:
            print(f"  {action.action}: {action.path}")

    # Regenerate content_index.json for Antigravity when the optional indexer exists.
    try:
        from system.scripts import gps_indexer
        gps_indexer.scan_files()
        print(f"  🔄 Regenerated: content_index.json")
    except Exception as e:
        print(f"  ⚠️  Failed to regenerate content_index.json: {e}")
    
    if actions:
        print(f"  ✅ Applied {len(actions)} root cleanup action(s)")
    else:
        print("  ✅ Repo structure already clean")
    
    return len(actions)

def check_system_access():
    """
    Validation: Ensure the System (Python) can access the GitIgnored "Dark Matter".
    """
    print("\n👁️  System Vision Check...")
    
    sensitive_roots = [
        "1. Company",
        "2. Products",
        "3. Meetings", 
        "4. People", 
        "5. Trackers"
    ]
    
    accessible_count = 0
    total_checked = 0
    
    for folder in sensitive_roots:
        path = BRAIN_ROOT / folder
        # Only check existence if we expect it (though these are required folders)
        if path.exists():
            total_checked += 1
            # Check read AND write access
            if os.access(path, os.R_OK) and os.access(path, os.W_OK):
                 accessible_count += 1
            else:
                 print(f"  🛑 Restricted Permissions: {folder}")
        else:
             print(f"  ⚠️ Missing Directory: {folder}")
             
    if accessible_count == total_checked and total_checked > 0:
        print(f"  ✅ System has full Read/Write access to all {accessible_count} private folders.")
    elif total_checked == 0:
        print("  ⚠️ No private folders found to check.")
    else:
        print(f"  ⚠️ System has access to {accessible_count}/{total_checked} folders.")

def check_git_safety():
    """
    Privacy Audit: Ensure no sensitive Brain files are being verified by Git.
    """
    print("\n🔒 Privacy Check...")
    
    # 1. Ask Git what it is tracking or seeing
    try:
        # Check staged and untracked files
        result = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True, 
            cwd=str(BRAIN_ROOT)
        )
        if result.returncode != 0:
            print("  ⚠️ Git check failed (is this a git repo?). Skipping.")
            return

        files = []
        for line in result.stdout.splitlines():
            # "M  file.ext" -> "file.ext"
            # "?? file.ext" -> "file.ext"
            parts = line.strip().split(" ", 1)
            if len(parts) > 1:
                files.append(parts[1])
                
        # 2. Audit against Kernel Rules
        passed, violations = kernel_utils.check_privacy_rule(files)
        
        if passed:
            print("  ✅ All sensitive files are successfully ignored.")
        else:
            print(f"  🛑 WARNING: Found {len(violations)} sensitive files visible to Git!")
            for v in violations:
                print(f"     - {v}")
            print("  ACTION: These files should be ignored via .gitignore.")

    except Exception as e:
        print(f"  ⚠️ Could not run git check: {e}")

def manage_tiered_memory() -> None:
    """
    Implement Hot/Warm/Cold tiered memory management for meetings.

    Tiers:
        Hot  (Active)    → MEETINGS_DIR/transcripts/  (< 30 days)
        Warm (Recent)    → MEETINGS_DIR/summaries/    (7–30 days)
        Cold (Archived)  → MEETINGS_DIR/archive/      (> 30 days)

    Files older than 30 days in transcripts/ are moved to archive/.
    """
    import time as _time

    transcripts_dir = MEETINGS_DIR / "transcripts"
    archive_dir = MEETINGS_DIR / "archive"

    # Ensure directories exist
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    now = _time.time()
    threshold_seconds = 30 * 24 * 60 * 60  # 30 days in seconds

    moved: List[Path] = []
    for file_path in list(transcripts_dir.iterdir()):
        if not file_path.is_file():
            continue
        age_seconds = now - file_path.stat().st_mtime
        if age_seconds > threshold_seconds:
            destination = archive_dir / file_path.name
            shutil.move(str(file_path), str(destination))
            moved.append(file_path)

    if moved:
        print(f"  [Cold Storage] Moved {len(moved)} old transcript(s) to archive/.")
    else:
        print("  ✅ No transcripts eligible for archiving.")


def archive_transcripts() -> None:
    """Alias for manage_tiered_memory(), called from queue job handlers."""
    manage_tiered_memory()


def main():
    ensure_dirs()
    print("--- 🧹 System Vacuum Protocol ---")
    
    # 1. Fetch Latest Transcripts (The Bridge)
    print("\n--- 🕵️ Fetching Transcripts (Quill Bridge) ---")
    try:
        q_path = db_bridge.get_quill_db_path()
        if q_path:
            db_bridge.extract_transcripts(q_path)
        else:
            print("  ℹ️  Quill DB not found. Skipping fetch.")
    except Exception as e:
        print(f"  ⚠️ Transcript fetch failed: {e}")
        
    # 2. Universal File Processing (The Sorter)
    try:
        file_organizer.scan_and_process()
    except Exception as e:
        print(f"  ⚠️ File processing failed: {e}")
    
    print("\n--- 🗄️ Archiving Old Data ---")
    
    # Vaccum Trackers
    targets = [
        "TASK_MASTER.md", 
        "BUG_TRACKER.md", 
        "BOSS_REQUESTS.md", 
        "PROJECT_TRACKER.md",
        "DELEGATED_TASKS.md",
        "ENG_TASKS.md",
        "UX_TASKS.md"
    ]
    total_cleaned = 0
    for t in targets:
        total_cleaned += vacuum_tracker(t)
        
    # 3. Manage Memory Tiers (Librarian)
    print("\n--- 📚 Managing Memory Tiers (The Librarian) ---")
    meetings_dir = BRAIN_ROOT / "3. Meetings" / "transcripts"
    if meetings_dir.exists():
        for item in os.listdir(meetings_dir):
            item_path = meetings_dir / item
            if item_path.is_file() and item.endswith(".txt"):
                # Check age (7 days)
                age_days = (time.time() - item_path.stat().st_mtime) / (3600 * 24)
                if age_days > 7:
                    print(f"  🕰️  Found old transcript ({int(age_days)} days): {item}")
                    librarian.archive_transcript(str(item_path))
    
    # 4. Skeleton Cleanup (Senior Engineer Audit)
    clean_skeleton()

    # 5. Repo Structure Cleanup
    clean_repo_structure()

    # 6. Deep Memory Consolidation
    print("\n--- 🧠 Deep Memory Consolidation ---")
    try:
        subprocess.run([sys.executable, str(BRAIN_ROOT / ".agent" / "skills" / "memory-consolidator" / "scripts" / "consolidate.py"), "--hours", "168"], check=True, env=dict(os.environ, PYTHONUTF8="1"))
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ Consolidation process encountered an error: {e}")
    except Exception as e:
        print(f"  ⚠️ Could not execute memory consolidation: {e}")

    # TencentDB-Agent-Memory consolidation
    print("\n--- 💾 TencentDB-Agent-Memory Consolidation ---")
    try:
        subprocess.run([sys.executable, str(BRAIN_ROOT / "system" / "scripts" / "agentic_memory.py"), "consolidate", "--hours", "168"], check=True, env=dict(os.environ, PYTHONUTF8="1"))
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ TencentDB memory consolidation process encountered an error: {e}")
    except Exception as e:
        print(f"  ⚠️ Could not execute TencentDB memory consolidation: {e}")

    # Privacy & Access Checks
    check_system_access()
    check_git_safety()
    
    print("\n✅ Optimization Complete.")

if __name__ == "__main__":
    main()
