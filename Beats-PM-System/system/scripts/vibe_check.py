"""
Vibe Check Script (Centrifuge Protocol)

Validates the Beats PM System environment and configuration.
Checks toolchain, file structure, critical files, and AI model configuration.
"""

import sys
from pathlib import Path
from typing import List

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent.parent  # Beats-PM-System/
BRAIN_ROOT = SYSTEM_ROOT.parent                 # beats-pm-antigravity-brain/

# Add SYSTEM_ROOT to path for 'system.*' imports
sys.path.insert(0, str(SYSTEM_ROOT))

from system.utils.ui import (
    print_cyan,
    print_success,
    print_warning,
    print_error,
)
from system.utils.platform import (
    get_system,
    get_python_executable,
    get_npm_executable,
)
from system.utils.subprocess_helper import (
    check_command_exists,
    check_extension_installed,
)
from system.utils.config import get_config


def check_toolchain() -> None:
    """Check if required development tools are installed."""
    print_cyan("\nToolchain:")

    # Check Python
    python_cmd = get_python_executable()
    if check_command_exists(python_cmd):
        print_success("Python: Installed")
    else:
        print_error("Python: Missing")

    # Check Git
    if check_command_exists("git"):
        print_success("Git: Installed")
    else:
        print_error("Git: Missing")

    # Check GitHub CLI
    if check_command_exists("gh"):
        print_success("GitHub CLI: Installed")
    else:
        print_error("GitHub CLI: Missing")

    # Check Node/NPM
    npm_cmd = get_npm_executable()
    if check_command_exists(npm_cmd):
        print_success("Node/NPM: Installed")
    else:
        print_error("Node/NPM: Missing")


def check_file_structure() -> None:
    """Check if required directory structure exists."""
    print_cyan("\nCore Infrastructure:")

    folders = get_config("directories.required", [])

    for folder in folders:
        folder_path = BRAIN_ROOT / folder
        if folder_path.is_dir():
            print_success(f"/{folder}: Found")
        else:
            print_warning(f"/{folder}: Missing (Run #update)")


def check_critical_files() -> None:
    """Check if critical system files exist."""
    print_cyan("\nSystem Files:")

    critical_files = [
        get_config("files.kernel", "KERNEL.md"),
        get_config("files.settings", "SETTINGS.md"),
        get_config("files.readme", "README.md"),
    ]

    for filename in critical_files:
        filepath = BRAIN_ROOT / filename
        if filepath.is_file():
            print_success(f"{filename}: Found")
        else:
            print_error(f"{filename}: CRITICAL MISSING")


def check_skills_configuration() -> None:
    """Check if the Skills directory and content exist."""
    print_cyan("\nAI Agent Skills (v4.4.0):")

    skills_dir = BRAIN_ROOT / ".agent/skills"

    if skills_dir.is_dir():
        print_success("Skills Directory: Found")

        # Check for core skills
        core_skills = [
            "meeting-synth",
            "bug-chaser",
            "prd-author",
            "task-manager",
            "daily-synth",
        ]
        for skill in core_skills:
            skill_path = skills_dir / skill
            if skill_path.is_dir():
                print_success(f" Skill: {skill} (Loaded)")
            else:
                print_warning(f" Skill: {skill} (MISSING)")
    else:
        print_error("Skills Directory Missing! (Run #update)")


def check_extensions() -> None:
    """Check if optional extensions are installed."""
    print_cyan("\nOptional Power-Ups:")

    extensions = get_config("extensions", [])

    for ext in extensions:
        ext_id = ext.get("id")
        ext_name = ext.get("name", ext_id)

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
