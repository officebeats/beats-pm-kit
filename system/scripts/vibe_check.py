"""
Vibe Check Script (Centrifuge Protocol)

Validates the Beats PM System environment and configuration.
Checks toolchain, file structure, critical files, and AI model configuration.
"""

import sys
import os
import datetime
from pathlib import Path
from typing import List

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent      # system/
BRAIN_ROOT = SYSTEM_ROOT.parent               # beats-pm-antigravity-brain/
REPORTS_DIR = SYSTEM_ROOT / "reports"

# Add BRAIN_ROOT to path for 'system.*' imports
sys.path.insert(0, str(BRAIN_ROOT))

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

class Logger:
    """Redirects stdout to both console and a log file."""
    def __init__(self):
        self.terminal = sys.stdout
        self.log_file = None
        self.log_path = self._init_log_file()

    def _init_log_file(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = REPORTS_DIR / f"vibe_report_{timestamp}.txt"
        self.log_file = open(filename, "a", encoding="utf-8")
        return filename

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    @property
    def encoding(self):
        return "utf-8"

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
    
    # Fallback default folders if config is empty
    if not folders:
        folders = [
            "0. Incoming/staging",
            "1. Company",
            "2. Products",
            "3. Meetings/transcripts",
            "4. People",
            "5. Trackers"
        ]

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
        get_config("files.kernel", ".agent/rules/GEMINI.md"),
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
    print_cyan("\nAI Agent Skills (Gamma-Class v2.0):")

    skills_dir = BRAIN_ROOT / ".agent/skills"

    if skills_dir.is_dir():
        print_success("Skills Directory: Found")
        
        # Dynamic Scan
        found_skills = [
            d.name for d in skills_dir.iterdir() 
            if d.is_dir() and (d / "SKILL.md").exists()
        ]
        
        found_skills.sort()
        
        for skill in found_skills:
            print_success(f" Skill: {skill} (Loaded)")
            
        if not found_skills:
             print_warning(" No skills found in directory!")
             
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
    # Hijack stdout
    logger = Logger()
    sys.stdout = logger
    
    system = get_system()
    print_cyan(f"--- Antigravity Vibe Check ({system}) ---")
    print_cyan(f"Report saved to: {logger.log_path}")

    # Run all checks
    check_toolchain()
    check_file_structure()
    check_critical_files()
    check_skills_configuration()
    check_extensions()

    print_cyan("\n--- Check Complete ---")


if __name__ == "__main__":
    main()
