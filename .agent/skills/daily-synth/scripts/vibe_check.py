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
        get_config('files.readme', 'README.md')
    ]
    
    for filename in critical_files:
        if file_exists(filename):
            print_success(f"{filename}: Found")
        else:
            print_error(f"{filename}: CRITICAL MISSING")


def check_model_configuration():
    """Check and update AI model configuration."""
    print_cyan("\nAI Model Configuration:")
    
    mesh_path = get_config('ai.mesh_config_path', 'Beats-PM-System/system/agents/mesh.toml')
    latest_model = get_default_model()
    
    if not file_exists(mesh_path):
        print_error(f"mesh.toml missing!")
        return
    
    try:
        content = read_file(mesh_path)
        if content is None:
            print_error(f"Failed to read mesh.toml")
            return
        
        # Check if model is up to date
        if f'default_model = "{latest_model}"' in content:
            print_success(f"Model: {latest_model} (Latest)")
        else:
            print_warning(f"Model is outdated. Updating to {latest_model}...")
            
            # Update the model configuration
            new_content = ""
            for line in content.splitlines():
                if "default_model =" in line:
                    new_content += f'default_model = "{latest_model}" # AUTO-UPDATE: Always set to latest available Flash\n'
                else:
                    new_content += line + "\n"
            
            if write_file(mesh_path, new_content):
                print_success(f"Updated to {latest_model}")
            else:
                print_error(f"Failed to update mesh.toml")
                
    except Exception as e:
        print_error(f"Failed to check mesh.toml: {e}")


def check_extensions():
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


def main():
    """Main entry point for vibe check."""
    system = get_system()
    print_cyan(f"--- Antigravity Vibe Check ({system}) ---")
    
    # Run all checks
    check_toolchain()
    check_file_structure()
    check_critical_files()
    check_model_configuration()
    check_extensions()
    
    print_cyan("\n--- Check Complete ---")


if __name__ == "__main__":
    main()
