"""
Platform Utilities Module

Provides platform detection and abstraction for cross-platform compatibility.
"""

import platform
import subprocess
from typing import Optional


# Platform constants
PLATFORM_WINDOWS = "Windows"
PLATFORM_MACOS = "Darwin"
PLATFORM_LINUX = "Linux"


def get_system() -> str:
    """
    Get the current operating system name.
    
    Returns:
        Platform name (Windows, Darwin, or Linux)
    """
    return platform.system()


def is_windows() -> bool:
    """
    Check if the current platform is Windows.
    
    Returns:
        True if running on Windows, False otherwise
    """
    return get_system() == PLATFORM_WINDOWS


def is_macos() -> bool:
    """
    Check if the current platform is macOS.
    
    Returns:
        True if running on macOS, False otherwise
    """
    return get_system() == PLATFORM_MACOS


def is_linux() -> bool:
    """
    Check if the current platform is Linux.
    
    Returns:
        True if running on Linux, False otherwise
    """
    return get_system() == PLATFORM_LINUX


def get_shell_flag() -> bool:
    """
    Get the appropriate shell flag for subprocess execution.
    
    On Windows, subprocess commands need shell=True for proper execution.
    On Unix-like systems, shell=False is preferred for security.
    
    Returns:
        True if shell=True is needed, False otherwise
    """
    return is_windows()


def get_python_executable() -> str:
    """
    Get the appropriate Python executable name for the current platform.
    
    Returns:
        'python' on Windows, 'python3' on Unix-like systems
    """
    return "python" if is_windows() else "python3"


def get_npm_executable() -> str:
    """
    Get the appropriate NPM executable name for the current platform.
    
    Returns:
        'npm.cmd' on Windows, 'npm' on Unix-like systems
    """
    return "npm.cmd" if is_windows() else "npm"


def get_path_separator() -> str:
    """
    Get the path separator for the current platform.
    
    Returns:
        '\\' on Windows, '/' on Unix-like systems
    """
    return '\\' if is_windows() else '/'


def get_environment_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable value.
    
    Args:
        name: Environment variable name
        default: Default value if variable is not set
    
    Returns:
        Environment variable value or default
    """
    import os
    return os.environ.get(name, default)


def set_environment_variable(name: str, value: str) -> None:
    """
    Set an environment variable.
    
    Args:
        name: Environment variable name
        value: Value to set
    """
    import os
    os.environ[name] = value


def get_home_directory() -> str:
    """
    Get the user's home directory.
    
    Returns:
        Path to the home directory
    """
    import os
    return os.path.expanduser("~")


def get_temp_directory() -> str:
    """
    Get the system's temporary directory.
    
    Returns:
        Path to the temp directory
    """
    import tempfile
    return tempfile.gettempdir()


def get_clipboard_command() -> Optional[list]:
    """
    Get the appropriate clipboard command for the current platform.
    
    Returns:
        List of command arguments for clipboard access, or None if not available
    """
    if is_macos():
        return ['pbpaste']
    elif is_linux():
        # Try xclip first, then xsel
        if check_command_exists('xclip'):
            return ['xclip', '-selection', 'clipboard', '-o']
        elif check_command_exists('xsel'):
            return ['xsel', '--clipboard', '--output']
    return None


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists on the system.
    
    Args:
        command: Command name to check
    
    Returns:
        True if command exists, False otherwise
    """
    try:
        subprocess.run(
            [command, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            shell=get_shell_flag()
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_platform_info() -> dict:
    """
    Get comprehensive platform information.
    
    Returns:
        Dictionary containing platform details
    """
    return {
        'system': get_system(),
        'is_windows': is_windows(),
        'is_macos': is_macos(),
        'is_linux': is_linux(),
        'python_version': platform.python_version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version()
    }


def print_platform_info() -> None:
    """Print platform information in a formatted way."""
    from .ui import print_cyan, print_info
    
    info = get_platform_info()
    
    print_cyan("\n=== Platform Information ===")
    print_info(f"System: {info['system']}")
    print_info(f"Python Version: {info['python_version']}")
    print_info(f"Machine: {info['machine']}")
    print_info(f"Node: {info['node']}")
    print_info(f"Release: {info['release']}")
    print_cyan("============================\n")
