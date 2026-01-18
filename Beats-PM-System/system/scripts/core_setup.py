"""
Core Setup Script

Initializes the Beats PM System by creating directories, copying templates,
and installing optional extensions.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import (
    print_cyan, print_green, print_yellow, print_gray,
    print_success, print_warning, print_error
)
from utils.platform import get_system
from utils.filesystem import ensure_directory, copy_file, file_exists
from utils.subprocess_helper import check_extension_installed, install_extension, run_python_script
from utils.config import get_config, get_required_directories, get_extensions


def create_directories() -> None:
    """Create required directory structure."""
    directories = get_required_directories()
    
    for directory in directories:
        if not file_exists(directory):
            if ensure_directory(directory):
                print_success(f"Created Directory {directory}/")
            else:
                print_error(f"Failed to create directory {directory}/")


def copy_templates() -> None:
    """Copy template files to their target locations."""
    templates = [
        {
            'src': get_config('templates.settings'),
            'dst': get_config('files.settings')
        },
        {
            'src': get_config('templates.bug_report'),
            'dst': '5. Trackers/bugs/bugs-master.md'
        },
        {
            'src': get_config('templates.boss_request'),
            'dst': '5. Trackers/critical/boss-requests.md'
        },
        {
            'src': get_config('templates.meeting_notes'),
            'dst': '5. Trackers/critical/escalations.md'
        },
        {
            'src': get_config('templates.feature_request'),
            'dst': '5. Trackers/projects/projects-master.md'
        }
    ]
    
    for template in templates:
        src = template['src']
        dst = template['dst']
        
        # Ensure target directory exists
        target_dir = os.path.dirname(dst)
        if target_dir and not file_exists(target_dir):
            ensure_directory(target_dir)
        
        if not file_exists(dst):
            if file_exists(src):
                if copy_file(src, dst):
                    print_success(f"Created {dst}")
                else:
                    print_error(f"Failed to copy {src} to {dst}")
            else:
                print_warning(f"Template missing: {src}")
        else:
            print_gray(f"[skip] {dst} (Exists)")


def install_extensions() -> None:
    """Prompt user to install optional extensions."""
    extensions = get_extensions()
    
    if not extensions:
        return
    
    print_cyan("\n🚀 Optional Power-Ups:")
    
    for ext in extensions:
        ext_id = ext.get('id')
        ext_name = ext.get('name', ext_id)
        ext_url = ext.get('url')
        
        if check_extension_installed(ext_id):
            print_gray(f"[skip] {ext_name} (Already installed)")
        else:
            response = input(f"  [?] Would you like to install {ext_name}? (y/n): ").strip().lower()
            if response == 'y':
                install_extension(ext_id, ext_name, ext_url)


def run_vibe_check() -> None:
    """Run the vibe check script to validate the system."""
    print_cyan("\n🔍 Verifying Intelligence Model...")
    
    vibe_script = os.path.join("Beats-PM-System", "system", "scripts", "vibe_check.py")
    
    if file_exists(vibe_script):
        run_python_script(vibe_script)
    else:
        print_warning("Warning: vibe_check.py not found. Model validation skipped.")



def run_skill_optimizer() -> None:
    """Run the skill optimizer to index skills."""
    print_cyan("\n🧠 Optimizing Agent Skills...")
    script = os.path.join("Beats-PM-System", "system", "scripts", "optimize_skills.py")
    if file_exists(script):
        run_python_script(script)
    else:
        print_warning("Skill optimizer script not found.")

def run_memory_init() -> None:
    """Initialize long-term memory artifacts (Inline)."""
    print_cyan("\n💾 Initializing Long-Term Memory...")
    
    root = get_config('paths.root')
    if not root:
         root = str(os.getcwd())

    # 1. DECISION_LOG.md
    dec_path = get_config('trackers.decision_log')
    if dec_path:
        full_dec_path = os.path.join(root, dec_path)
        if not file_exists(full_dec_path):
            ensure_directory(os.path.dirname(full_dec_path))
            header = ("# Strategic Decision Log\n\n"
                      "> Immutable record of key product and architectural decisions.\n\n"
                      "| Date | Decision | Context | Owner |\n"
                      "|:---|:---|:---|:---|\n")
            with open(full_dec_path, "w", encoding="utf-8") as f:
                f.write(header)
            print_success(f"Created {dec_path}")
        else:
            print_gray(f"[skip] {dec_path} (Exists)")

    # 2. PEOPLE.md
    people_dir = get_config('paths.people')
    if people_dir:
        people_file = os.path.join(root, people_dir, "PEOPLE.md")
        if not file_exists(people_file):
            ensure_directory(os.path.dirname(people_file))
            header = ("# People & Stakeholders\n\n"
                      "> The Human Context. Who does what?\n\n"
                      "| Name | Role | Context |\n"
                      "|:---|:---|:---|\n")
            with open(people_file, "w", encoding="utf-8") as f:
                f.write(header)
            print_success(f"Created {people_dir}/PEOPLE.md")
        else:
            print_gray(f"[skip] {people_dir}/PEOPLE.md (Exists)")

    # 3. quote-index.md
    quote_dir = get_config('paths.meetings')
    if quote_dir:
        quote_file = os.path.join(root, quote_dir, "quote-index.md")
        if not file_exists(quote_file):
            ensure_directory(os.path.dirname(quote_file))
            header = ("# Quote Index\n\n"
                      "> Grep-friendly archive of key verbatim quotes.\n\n"
                      "| Date | Speaker | Quote | Source |\n"
                      "|:---|:---|:---|:---|\n")
            with open(quote_file, "w", encoding="utf-8") as f:
                f.write(header)
            print_success(f"Created {quote_dir}/quote-index.md")
        else:
            print_gray(f"[skip] {quote_dir}/quote-index.md (Exists)")

    # 4. SESSION_MEMORY.md (Root)
    session_file = os.path.join(root, "SESSION_MEMORY.md")
    if not file_exists(session_file):
        header = ("# Session Memory\n"
                  "> Last Known State registry.\n\n"
                  "System Initialized. No previous session data.\n")
        with open(session_file, "w", encoding="utf-8") as f:
            f.write(header)
        print_success("Created SESSION_MEMORY.md")
    else:
        print_gray("[skip] SESSION_MEMORY.md (Exists)")


def run_structure_enforcement() -> None:
    """Run the self-healing structure enforcement."""
    script = os.path.join("Beats-PM-System", "system", "scripts", "enforce_structure.py")
    if file_exists(script):
        run_python_script(script)


def main() -> None:
    """Main entry point for core setup."""
    system = get_system()
    version = get_config('system.version', 'Unknown')
    print_cyan(f"🧠 Hydrating Antigravity Brain v{version} ({system})...")
    
    # 1. Create directories
    create_directories()
    
    # 2. Initialize Memory
    run_memory_init()
    
    # 3. Optimize Skills (Sync - Required for operation)
    run_skill_optimizer()
    
    # 4. Copy templates
    copy_templates()
    
    # 5. Background Heavy Tasks (New Native Optimization)
    # We offload structure enforcement and vacuuming to the background queue
    # so the user gets control back instantly.

    try:
        from system.scripts import turbo_dispatch
        print_cyan("\n⚡ Dispatching Background Optimizations...")
        turbo_dispatch.submit("structure_enforce", {})
        turbo_dispatch.submit("gps_index", {})
    except ImportError:
        print_warning("Could not dispatch background tasks (module missing)")
    
    print_cyan("\n✅ Brain is ready. Your privacy is secured.")
    print_yellow("Active files are ignored by git. You can now add your real data.")
    
    # 6. Install optional extensions
    install_extensions()
    
    # 7. Run vibe check
    run_vibe_check()
    
    # Pause on Windows for visibility
    if system == "Windows":
        time.sleep(3)


if __name__ == "__main__":
    main()
