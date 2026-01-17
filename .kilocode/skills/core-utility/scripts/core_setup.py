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


def create_directories():
    """Create required directory structure."""
    directories = get_required_directories()
    
    for directory in directories:
        if not file_exists(directory):
            if ensure_directory(directory):
                print_success(f"Created Directory {directory}/")
            else:
                print_error(f"Failed to create directory {directory}/")


def copy_templates():
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


def install_extensions():
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


def run_vibe_check():
    """Run the vibe check script to validate the system."""
    print_cyan("\n🔍 Verifying Intelligence Model...")
    
    vibe_script = os.path.join("Beats-PM-System", "system", "scripts", "vibe_check.py")
    
    if file_exists(vibe_script):
        run_python_script(vibe_script)
    else:
        print_warning("Warning: vibe_check.py not found. Model validation skipped.")


def main():
    """Main entry point for core setup."""
    system = get_system()
    print_cyan(f"🧠 Hydrating Antigravity Brain v2.6.3 ({system})...")
    
    # 1. Create directories
    create_directories()
    
    # 2. Copy templates
    copy_templates()
    
    print_cyan("\n✅ Brain is ready. Your privacy is secured.")
    print_yellow("Active files are ignored by git. You can now add your real data.")
    
    # 3. Install optional extensions
    install_extensions()
    
    # 4. Run vibe check
    run_vibe_check()
    
    # Pause on Windows for visibility
    if system == "Windows":
        time.sleep(3)


if __name__ == "__main__":
    main()
