"""
Update Script (Evolution Protocol)

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
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # brain/
SCRIPTS_DIR = SYSTEM_ROOT / "scripts"
KIT_VERSION = (BRAIN_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (BRAIN_ROOT / "VERSION").exists() else "unknown"
UPDATE_STASH_MARKER = f"Auto-stash before update v{KIT_VERSION}"

# Add BRAIN_ROOT to path for imports
sys.path.insert(0, str(BRAIN_ROOT))

from system.utils.ui import print_cyan, print_success, print_error, print_warning
from system.scripts.root_cleaner import clean_root
from system.scripts import upgrade_compat


def compatibility_gate(stage):
    """Refuse upgrade mutations until existing Markdown is safely migratable."""
    print_cyan(f"\n🔎 Compatibility Check ({stage})...")
    report = upgrade_compat.inspect(BRAIN_ROOT)
    if report.blockers:
        print_error(f"Upgrade blocked by {len(report.blockers)} compatibility error(s).")
        print_warning("Run: python system/scripts/upgrade_compat.py --json")
        return False
    if report.changes:
        print_error(f"Upgrade requires {len(report.changes)} safe Markdown title update(s).")
        print_warning("Review: python system/scripts/upgrade_compat.py --json")
        print_warning("Apply with backup: python system/scripts/upgrade_compat.py --apply")
        return False
    if report.warnings:
        print_warning(f"Compatibility check passed with {len(report.warnings)} source/setup warning(s); see --json for details.")
    print_success("Existing Markdown and task links are compatible.")
    return True

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
        return run_step("Stashing local changes", f'git stash push -m "{UPDATE_STASH_MARKER}"', ignore_error=True)
    return True

def restore_stash():
    """Attempt to pop stashed changes."""
    print_cyan("\n📥 Restoring Local Changes...")
    # Check if we have a stash
    result = subprocess.run("git stash list", shell=True, cwd=str(BRAIN_ROOT), capture_output=True, text=True)
    if UPDATE_STASH_MARKER in result.stdout:
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
    Scans for deprecated root clutter without deleting user work.
    Unknown root content moves to ignored '0. Incoming/root-cleanup/'.
    """
    print_cyan("\n🔍 Migration Scan (Zero Data Loss)...")
    try:
        actions = clean_root(BRAIN_ROOT, apply=True)
    except Exception as exc:
        print_warning(f"Root cleaner failed: {exc}")
        return
    if not actions:
        print_success("Root already clean.")
        return
    for action in actions:
        if action.destination:
            print_success(f"{action.action}: {action.path} -> {action.destination}")
        else:
            print_success(f"{action.action}: {action.path}")

def verify_structure():
    """Run core_setup.py to enforce directory structure and templates."""
    script_path = SCRIPTS_DIR / "core_setup.py"
    return run_step("Verifying System Structure", f'"{sys.executable}" "{script_path}" --headless')

def run_vacuum():
    """Run vacuum.py to clean up task lists and memory."""
    script_path = SCRIPTS_DIR / "vacuum.py"
    return run_step("Running System Vacuum", f'"{sys.executable}" "{script_path}"')

def vibe_check():
    """Run vibe_check.py to verify system health."""
    script_path = SCRIPTS_DIR / "vibe_check.py"
    return run_step("Final Vibe Check", f'"{sys.executable}" "{script_path}"')


def sync_runtime_adapters():
    """Regenerate runtime adapters after updates."""
    cli_sync = SCRIPTS_DIR / "sync_cli_adapters.py"
    codex_sync = SCRIPTS_DIR / "sync_codex_skill_adapters.py"
    return (
        run_step("Syncing CLI Adapters", f'"{sys.executable}" "{cli_sync}"', ignore_error=True)
        and run_step("Syncing Codex Skill Adapters", f'"{sys.executable}" "{codex_sync}"', ignore_error=True)
    )


def install_git_hooks():
    """Install repo-local git hooks for ongoing adapter sync."""
    hook_script = SCRIPTS_DIR / "install_git_hooks.py"
    return run_step("Installing Git Hooks", f'"{sys.executable}" "{hook_script}"', ignore_error=True)

def main():
    print_cyan(f"--- 🚀 System Update Protocol (v{KIT_VERSION}) ---")

    if not compatibility_gate("before update"):
        sys.exit(1)
    
    # 1. PRE-FLIGHT (Stash)
    pre_flight_check()
    
    # 2. GIT PULL
    if not git_update():
        print_warning("Git pull failed (maybe offline?). Continuing with local scripts.")

    if not compatibility_gate("after code update"):
        restore_stash()
        sys.exit(1)
        
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

    # 8. RE-SYNC LOCAL RUNTIME ADAPTERS
    sync_runtime_adapters()
    install_git_hooks()

    print_success("\n✅ System Update Complete. Ready for action.")

if __name__ == "__main__":
    main()
