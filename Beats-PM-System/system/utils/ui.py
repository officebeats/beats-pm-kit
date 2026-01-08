"""
UI Utilities Module

Provides consistent color printing and user interaction functions
across all Beats PM System scripts.
"""

import sys
import io

# ANSI color codes
COLORS = {
    'cyan': '\033[96m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'gray': '\033[90m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'white': '\033[97m',
    'reset': '\033[0m'
}

# Icons
ICONS = {
    'success': '✓',
    'error': '✗',
    'warning': '!',
    'info': 'i',
    'check': '✓',
    'cross': '✗',
    'arrow': '→',
    'bullet': '•'
}


def _colorize(text: str, color: str) -> str:
    """
    Apply ANSI color to text.
    
    Args:
        text: The text to colorize
        color: The color name (from COLORS dict)
    
    Returns:
        Colorized text with reset code
    """
    color_code = COLORS.get(color, '')
    reset_code = COLORS['reset']
    return f"{color_code}{text}{reset_code}"


def print_cyan(text: str) -> None:
    """Print text in cyan color."""
    _safe_print(_colorize(text, 'cyan'))


def print_green(text: str) -> None:
    """Print text in green color."""
    _safe_print(_colorize(text, 'green'))


def print_yellow(text: str) -> None:
    """Print text in yellow color."""
    _safe_print(_colorize(text, 'yellow'))


def print_red(text: str) -> None:
    """Print text in red color."""
    _safe_print(_colorize(text, 'red'))


def print_gray(text: str) -> None:
    """Print text in gray color."""
    _safe_print(_colorize(text, 'gray'))


def print_blue(text: str) -> None:
    """Print text in blue color."""
    print(_colorize(text, 'blue'))


def print_success(text: str, icon: bool = True) -> None:
    """
    Print a success message.
    
    Args:
        text: The success message
        icon: Whether to prepend a success icon
    """
    prefix = f"{ICONS['success']} " if icon else ""
    _safe_print(_colorize(f"{prefix}{text}", 'green'))


def print_warning(text: str, icon: bool = True) -> None:
    """
    Print a warning message.
    
    Args:
        text: The warning message
        icon: Whether to prepend a warning icon
    """
    prefix = f"{ICONS['warning']} " if icon else ""
    _safe_print(_colorize(f"{prefix}{text}", 'yellow'))


def print_error(text: str, icon: bool = True) -> None:
    """
    Print an error message.
    
    Args:
        text: The error message
        icon: Whether to prepend an error icon
    """
    prefix = f"{ICONS['error']} " if icon else ""
    _safe_print(_colorize(f"{prefix}{text}", 'red'))


def print_info(text: str, icon: bool = True) -> None:
    """
    Print an info message.
    
    Args:
        text: The info message
        icon: Whether to prepend an info icon
    """
    prefix = f"{ICONS['info']} " if icon else ""
    _safe_print(_colorize(f"{prefix}{text}", 'cyan'))


def _safe_print(text: str) -> None:
    """
    Print text with encoding error handling for Windows console.
    
    Args:
        text: Text to print
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))


def print_header(text: str, level: int = 1) -> None:
    """
    Print a formatted header.
    
    Args:
        text: The header text
        level: Header level (1-3)
    """
    if level == 1:
        separator = '=' * len(text)
        _safe_print(_colorize(f"\n{separator}\n{text}\n{separator}", 'cyan'))
    elif level == 2:
        separator = '-' * len(text)
        _safe_print(_colorize(f"\n{text}\n{separator}", 'cyan'))
    else:
        _safe_print(_colorize(f"\n{text}", 'cyan'))


def print_list(items: list, bullet: str = None) -> None:
    """
    Print a list of items with bullets.
    
    Args:
        items: List of items to print
        bullet: Custom bullet character (default: ICONS['bullet'])
    """
    if bullet is None:
        bullet = ICONS['bullet']
    for item in items:
        print(f"  {bullet} {item}")


def print_table(headers: list, rows: list) -> None:
    """
    Print a formatted table.
    
    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)
    """
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = ' | '.join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    separator = '-+-'.join('-' * w for w in col_widths)
    _safe_print(_colorize(header_row, 'cyan'))
    _safe_print(_colorize(separator, 'cyan'))
    
    # Print rows
    for row in rows:
        _safe_print(' | '.join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        prompt: The confirmation prompt
        default: Default value if user just presses Enter
    
    Returns:
        True if user confirms, False otherwise
    """
    default_str = 'Y/n' if default else 'y/N'
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


def get_input(prompt: str, default: str = None, required: bool = False) -> str:
    """
    Get user input with optional default and validation.
    
    Args:
        prompt: The input prompt
        default: Default value if user just presses Enter
        required: Whether input is required (non-empty)
    
    Returns:
        User input or default value
    """
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        response = input(prompt).strip()
        
        if not response and default is not None:
            return default
        
        if required and not response:
            print_error("This field is required. Please enter a value.")
            continue
        
        return response


def progress_bar(current: int, total: int, width: int = 50, prefix: str = '') -> None:
    """
    Print a progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        width: Width of the progress bar in characters
        prefix: Optional prefix text
    """
    if total == 0:
        percent = 100
    else:
        percent = int((current / total) * 100)
    
    filled = int(width * current / total) if total > 0 else width
    bar = '█' * filled + '░' * (width - filled)
    
    print(f"\r{prefix} |{bar}| {percent}%", end='', flush=True)
    
    if current >= total:
        print()  # New line when complete
