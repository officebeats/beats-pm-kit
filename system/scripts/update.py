"""
Update Script (Evolution Protocol v6.0.0)

Orchestrates the system update process with a "Zero Data Loss" policy:
1. 🛫 Pre-Flight Check (Stash changes)
2. 🔄 Git Pull (Update Code)
3. 🔍 Migration Scan (Recover deprecated/unknown files)
4. 📁 Core Setup (Verify Structure)
5. 🧹 Vacuum (Clean up & Skeleton Audit)
6. ✅ Vibe Check (Verify System Health)
7. 📥 Restore Stash (Pop user changes)
"""

import sys
import subprocess
import os
import shutil
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # brain/
SCRIPTS_DIR = SYSTEM_ROOT / "scripts"

# Add BRAIN_ROOT to path for imports
sys.path.insert(0, str(BRAIN_ROOT))

from system.utils.ui import print_cyan, print_success, print_error, print_warning

def run_step(description, command, cwd=None, ignore_error=False):
    """Run a shell command as a step."""
    print_cyan(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            cwd=cwd or str(BRAIN_ROOT),
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print_success("Done.")
        return True
    except subprocess.CalledProcessError as e:
        if ignore_error:
            print_warning(f"Warning: {e.stderr}")
            # Even if we ignore the error for the script flow, return False so logical checks can potentially use it
            return False 
        else:
            print_error(f"Failed: {e.stderr}")
            return False

def pre_flight_check():
    """Stash any local changes to prevent conflicts."""
    print_cyan("\n🛫 Pre-Flight Check...")
    # Check for changes
    status = subprocess.run("git status --porcelain", shell=True, cwd=str(BRAIN_ROOT), capture_output=True, text=True)
    if status.stdout.strip():
        print_warning("Local changes detected. Stashing them for safety...")
        return run_step("Stashing local changes", 'git stash save "Auto-stash before update v6.0.0"', ignore_error=True)
    return True

def restore_stash():
    """Attempt to pop stashed changes."""
    print_cyan("\n📥 Restoring Local Changes...")
    # Check if we have a stash
    result = subprocess.run("git stash list", shell=True, cwd=str(BRAIN_ROOT), capture_output=True, text=True)
    if "Auto-stash before update v6.0.0" in result.stdout:
        success = run_step("Popping stash", "git stash pop", ignore_error=True)
        if not success:
            print_warning("⚠️  Could not auto-pop stash (likely conflicts).")
            print_warning("   Your changes are safe in the stash!")
            print_warning("   Run 'git stash pop' manually to resolve manually.")
    else:
        print("No specific update stash found to restore.")

def git_update():
    """Pull latest changes from GitHub."""
    return run_step("Pulling latest code from GitHub", "git pull origin main", ignore_error=True)

def migration_scan():
    """
    Scans for deprecated files or misplaced user data from older versions.
    Moves unknown root files to '0. Incoming/' instead of deleting them.
    """
    print_cyan("\n🔍 Migration Scan (Zero Data Loss)...")
    
    # 1. Deprecated Files to Remove (Safe to delete)
    deprecated = [
        "KERNEL.md",           # Now in .agent/rules/GEMINI.md
        "SESSION_MEMORY.md",   # Unused
        ".gitkeep",            # Root clutter
        "temp_copy.py",
        "debug_vacuum.py"
    ]
    
    for item in deprecated:
        path = BRAIN_ROOT / item
        if path.exists():
            try:
                if path.is_file():
                    path.unlink()
                print_success(f"Cleaned deprecated file: {item}")
            except Exception as e:
                print_warning(f"Could not remove {item}: {e}")

    # 2. Key Directories to move to Archive
    legacy_dirs = ["Beats-PM-System", "root", "dst"]
    archive_dir = BRAIN_ROOT / "5. Trackers" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for d in legacy_dirs:
        path = BRAIN_ROOT / d
        if path.exists() and path.is_dir():
            try:
                shutil.move(str(path), str(archive_dir / d))
                print_success(f"Archived legacy directory: {d} -> archive/{d}")
            except Exception as e:
                print_warning(f"Could not archive {d}: {e}")

    # 3. Adopt Unknown Root Files (User Data Safety)
    # If the user saved "MyNotes.txt" in root, move it to Incoming.
    valid_root_files = {
        ".antigravityignore", ".gitattributes", ".gitignore",
        "GEMINI.md", "README.md", "SETTINGS.md", "STATUS.md",
        "requirements.txt", "task.md", "walkthrough.md", "implementation_plan.md"
    }
    
    incoming_dir = BRAIN_ROOT / "0. Incoming"
    incoming_dir.mkdir(parents=True, exist_ok=True)

    for item in BRAIN_ROOT.iterdir():
        if item.is_file() and not item.name.startswith("."):
            if item.name not in valid_root_files:
                try:
                    shutil.move(str(item), str(incoming_dir / item.name))
                    print_success(f"Recovered unknown root file: {item.name} -> 0. Incoming/")
                except Exception as e:
                    print_warning(f"Could not move {item.name}: {e}")

def verify_structure():
    """Run core_setup.py to enforce directory structure and templates."""
    script_path = SCRIPTS_DIR / "core_setup.py"
    return run_step("Verifying System Structure", f'python "{script_path}" --headless')

def run_vacuum():
    """Run vacuum.py to clean up task lists and memory."""
    script_path = SCRIPTS_DIR / "vacuum.py"
    return run_step("Running System Vacuum", f'python "{script_path}"')

def vibe_check():
    """Run vibe_check.py to verify system health."""
    script_path = SCRIPTS_DIR / "vibe_check.py"
    return run_step("Final Vibe Check", f'python "{script_path}"')

def main():
    print_cyan("--- 🚀 System Update Protocol (v6.0.0) ---")
    
    # 1. PRE-FLIGHT (Stash)
    pre_flight_check()
    
    # 2. GIT PULL
    if not git_update():
        print_warning("Git pull failed (maybe offline?). Continuing with local scripts.")
        
    # 3. MIGRATION SCAN
    migration_scan()

    # 4. STRUCTURE & TEMPLATES
    if not verify_structure():
        print_error("Structure verification failed.")
        sys.exit(1)

    # 5. VACUUM
    if not run_vacuum():
        print_warning("Vacuum process had issues, but continuing...")

    # 6. VIBE CHECK
    if not vibe_check():
        print_warning("System Health Check flagged issues.")
        
    # 7. RESTORE STASH
    restore_stash()

    print_success("\n✅ System Update Complete. Ready for action.")

if __name__ == "__main__":
    main()
