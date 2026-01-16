"""
Vibe Check Script (v3.1.0)

Validates the Beats PM System environment and configuration.
Checks toolchain, file structure, critical files, and AI model configuration.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import (
    print_cyan, print_green, print_yellow, print_red,
    print_success, print_warning, print_error, print_info
)
from utils.platform import get_system, get_python_executable, get_npm_executable
from utils.filesystem import file_exists, directory_exists, read_file, write_file
from utils.subprocess_helper import check_command_exists, check_extension_installed
from utils.config import get_default_model, get_config


def check_toolchain():
    """Check if required development tools are installed."""
    print_cyan("\nToolchain:")
    
    system = get_system()
    
    # Check Python
    python_cmd = get_python_executable()
    if check_command_exists(python_cmd):
        print_success(f"Python: Installed")
    else:
        print_error(f"Python: Missing")
    
    # Check Git
    if check_command_exists("git"):
        print_success(f"Git: Installed")
    else:
        print_error(f"Git: Missing")
    
    # Check GitHub CLI
    if check_command_exists("gh"):
        print_success(f"GitHub CLI: Installed")
    else:
        print_error(f"GitHub CLI: Missing")
    
    # Check Node/NPM
    npm_cmd = get_npm_executable()
    if check_command_exists(npm_cmd):
        print_success(f"Node/NPM: Installed")
    else:
        print_error(f"Node/NPM: Missing")


def check_file_structure():
    """Check if required directory structure exists."""
    print_cyan("\nCore Infrastructure:")
    
    folders = get_config('directories.required', [])
    
    for folder in folders:
        if directory_exists(folder):
            print_success(f"/{folder}: Found")
        else:
            print_warning(f"/{folder}: Missing (Run #update)")


def check_critical_files():
    """Check if critical system files exist."""
    print_cyan("\nSystem Files:")
    
    critical_files = [
        get_config('files.kernel', 'KERNEL.md'),
        get_config('files.settings', 'SETTINGS.md'),
        get_config('files.readme', 'README.md'),
        get_config('files.status', 'STATUS.md')
    ]
    
    for filename in critical_files:
        if file_exists(filename):
            print_success(f"{filename}: Found")
        else:
            print_error(f"{filename}: CRITICAL MISSING")


def check_skills_configuration():
    """Check if the Skills directory and content exist."""
    print_cyan("\nAI Agent Skills (v3.1.0):")
    
    skills_dir = get_config('paths.skills', '.gemini/skills')
    
    if directory_exists(skills_dir):
        print_success(f"Skills Directory: Found")
        
        # Check for core skills
        core_skills = [
            'core-utility', 'crm', 'meeting-synth', 
            'bug-chaser', 'prd-author', 'task-manager', 'daily-synth'
        ]
        for skill in core_skills:
            if directory_exists(os.path.join(skills_dir, skill)):
                print_success(f" Skill: {skill} (Loaded)")
            else:
                print_warning(f" Skill: {skill} (MISSING)")
    else:
        print_error(f"Skills Directory Missing! (Run #update)")


def check_trackers_flattening():
    """Check if trackers have been flattened to the root of 5. Trackers/."""
    print_cyan("\nFlattened Trackers:")
    
    trackers = get_config('trackers', {})
    
    for name, path in trackers.items():
        if file_exists(path):
            print_success(f"{name}: Found at {path}")
        else:
            print_warning(f"{name}: Missing at {path}")


class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def main():
    """Main entry point for vibe check."""
    
    # Setup logging to file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Go up 5 levels to reach root: scripts -> core-utility -> skills -> .agent -> brain -> root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    report_dir = os.path.join(root_dir, "Beats-PM-System", "reports")
    
    # Ensure report directory exists
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        
    report_file = os.path.join(report_dir, f"vibe_report_{timestamp}.txt")
    
    # Redirect stdout to both console and file
    sys.stdout = Logger(report_file)
    
    try:
        system = get_system()
        version = get_config('system.version', '3.1.0')
        print_cyan(f"--- Antigravity Vibe Check v{version} ({system}) ---")
        print_cyan(f"Report saved to: {report_file}")
        
        # Run all checks
        check_toolchain()
        check_file_structure()
        check_critical_files()
        check_skills_configuration()
        check_trackers_flattening()
        
        print_cyan("\n--- Check Complete ---")
    finally:
        # Restore stdout but keep the file written
        pass

if __name__ == "__main__":
    main()
