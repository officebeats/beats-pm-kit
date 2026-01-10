"""
Vibe Check Script

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
from utils.config import get_default_model, set_default_model, get_config


def check_toolchain() -> None:
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


def check_file_structure() -> None:
    """Check if required directory structure exists."""
    print_cyan("\nCore Infrastructure:")
    
    folders = get_config('directories.required', [])
    
    for folder in folders:
        if directory_exists(folder):
            print_success(f"/{folder}: Found")
        else:
            print_warning(f"/{folder}: Missing (Run #update)")


def check_critical_files() -> None:
    """Check if critical system files exist."""
    print_cyan("\nSystem Files:")
    
    critical_files = [
        get_config('files.kernel', 'KERNEL.md'),
        get_config('files.settings', 'SETTINGS.md'),
        get_config('files.readme', 'README.md')
    ]
    
    for filename in critical_files:
        if file_exists(filename):
            print_success(f"{filename}: Found")
        else:
            print_error(f"{filename}: CRITICAL MISSING")


def check_skills_configuration() -> None:
    """Check if the Skills directory and content exist."""
    print_cyan("\nAI Agent Skills (v3.0.0):")
    
    skills_dir = ".gemini/skills"
    
    if directory_exists(skills_dir):
        print_success(f"Skills Directory: Found")
        
        # Check for core skills
        core_skills = ['meeting-synth', 'bug-chaser', 'prd-author', 'task-manager', 'daily-synth']
        for skill in core_skills:
            if directory_exists(os.path.join(skills_dir, skill)):
                print_success(f" Skill: {skill} (Loaded)")
            else:
                print_warning(f" Skill: {skill} (MISSING)")
    else:
        print_error(f"Skills Directory Missing! (Run #update)")


def check_extensions() -> None:
    """Check if optional extensions are installed."""
    print_cyan("\nOptional Power-Ups:")
    
    extensions = get_config('extensions', [])
    
    for ext in extensions:
        ext_id = ext.get('id')
        ext_name = ext.get('name', ext_id)
        
        if check_extension_installed(ext_id):
            print_success(f"Ext: {ext_name}: Installed")
        else:
            print_warning(f"Ext: {ext_name}: Not Installed")


def main() -> None:
    """Main entry point for vibe check."""
    system = get_system()
    print_cyan(f"--- Antigravity Vibe Check ({system}) ---")
    
    # Run all checks
    check_toolchain()
    check_file_structure()
    check_critical_files()
    check_skills_configuration()
    check_extensions()
    
    print_cyan("\n--- Check Complete ---")


if __name__ == "__main__":
    main()
