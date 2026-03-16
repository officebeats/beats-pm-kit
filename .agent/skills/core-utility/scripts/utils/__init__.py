"""
Beats PM System - Shared Utilities Module

This module provides common utilities for all system scripts,
including UI functions, platform abstraction, file system operations,
subprocess execution, and configuration management.
"""

from .ui import (
    print_cyan,
    print_green,
    print_yellow,
    print_red,
    print_gray,
    print_success,
    print_warning,
    print_error,
    print_info
)

from .platform import (
    get_system,
    is_windows,
    is_macos,
    is_linux,
    get_shell_flag
)

from .filesystem import (
    ensure_directory,
    ensure_file_directory,
    file_exists,
    directory_exists,
    read_file,
    write_file,
    append_file,
    get_relative_path
)

from .subprocess_helper import (
    run_command,
    run_command_silent,
    check_command_exists,
    install_extension
)

from .config import (
    get_config,
    get_config_path,
    load_config,
    save_config
)

__all__ = [
    # UI functions
    'print_cyan', 'print_green', 'print_yellow', 'print_red', 'print_gray',
    'print_success', 'print_warning', 'print_error', 'print_info',
    # Platform functions
    'get_system', 'is_windows', 'is_macos', 'is_linux', 'get_shell_flag',
    # Filesystem functions
    'ensure_directory', 'ensure_file_directory', 'file_exists', 'directory_exists',
    'read_file', 'write_file', 'append_file', 'get_relative_path',
    # Subprocess functions
    'run_command', 'run_command_silent', 'check_command_exists', 'install_extension',
    # Config functions
    'get_config', 'get_config_path', 'load_config', 'save_config'
]
