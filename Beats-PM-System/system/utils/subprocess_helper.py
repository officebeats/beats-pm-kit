"""
Subprocess Utilities Module

Provides consistent subprocess execution across all Beats PM System scripts.
"""

import subprocess
from typing import Optional, List, Union, Tuple
from .platform import get_shell_flag


def run_command(
    command: Union[str, List[str]],
    capture_output: bool = False,
    check: bool = True,
    shell: Optional[bool] = None,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    timeout: Optional[int] = None
) -> subprocess.CompletedProcess:
    """
    Run a command with consistent error handling.
    
    Args:
        command: Command to run (string or list)
        capture_output: Whether to capture stdout and stderr
        check: Whether to raise an exception on non-zero exit code
        shell: Whether to use shell (default: platform-dependent)
        cwd: Working directory for the command
        env: Environment variables for the command
        timeout: Timeout in seconds
    
    Returns:
        CompletedProcess object
    
    Raises:
        subprocess.CalledProcessError: If check=True and command fails
        subprocess.TimeoutExpired: If timeout is exceeded
    """
    if shell is None:
        shell = get_shell_flag()
    
    return subprocess.run(
        command,
        capture_output=capture_output,
        check=check,
        shell=shell,
        cwd=cwd,
        env=env,
        timeout=timeout
    )


def run_command_silent(
    command: Union[str, List[str]],
    shell: Optional[bool] = None,
    cwd: Optional[str] = None
) -> bool:
    """
    Run a command silently (no output, no exceptions).
    
    Args:
        command: Command to run
        shell: Whether to use shell (default: platform-dependent)
        cwd: Working directory for the command
    
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        run_command(
            command,
            capture_output=True,
            check=True,
            shell=shell,
            cwd=cwd
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists on the system.
    
    Args:
        command: Command name to check
    
    Returns:
        True if command exists, False otherwise
    """
    try:
        run_command(
            [command, '--version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_command_output(
    command: Union[str, List[str]],
    shell: Optional[bool] = None,
    cwd: Optional[str] = None,
    strip: bool = True
) -> Optional[str]:
    """
    Get the output of a command.
    
    Args:
        command: Command to run
        shell: Whether to use shell (default: platform-dependent)
        cwd: Working directory for the command
        strip: Whether to strip whitespace from output
    
    Returns:
        Command output as string, or None on error
    """
    try:
        result = run_command(
            command,
            capture_output=True,
            check=True,
            shell=shell,
            cwd=cwd
        )
        output = result.stdout.decode('utf-8', errors='replace')
        return output.strip() if strip else output
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def get_command_output_lines(
    command: Union[str, List[str]],
    shell: Optional[bool] = None,
    cwd: Optional[str] = None
) -> Optional[List[str]]:
    """
    Get the output of a command as a list of lines.
    
    Args:
        command: Command to run
        shell: Whether to use shell (default: platform-dependent)
        cwd: Working directory for the command
    
    Returns:
        List of output lines, or None on error
    """
    output = get_command_output(command, shell=shell, cwd=cwd, strip=False)
    if output is None:
        return None
    return output.splitlines()


def run_python_script(script_path: str, args: Optional[List[str]] = None) -> bool:
    """
    Run a Python script.
    
    Args:
        script_path: Path to the Python script
        args: Optional list of arguments to pass to the script
    
    Returns:
        True if script ran successfully, False otherwise
    """
    import sys
    from .platform import get_python_executable
    
    command = [get_python_executable(), script_path]
    if args:
        command.extend(args)
    
    return run_command_silent(command)


def install_extension(
    ext_id: str,
    ext_name: str,
    ext_url: Optional[str] = None
) -> bool:
    """
    Install an extension using the antigravity CLI.
    
    Args:
        ext_id: Extension ID
        ext_name: Extension name (for display)
        ext_url: Optional URL to download extension from
    
    Returns:
        True if installation succeeded, False otherwise
    """
    from .ui import print_cyan, print_green, print_error
    from .platform import get_shell_flag
    import os
    import urllib.request
    
    shell = get_shell_flag()
    
    if ext_url:
        # Download and install from URL
        filename = ext_url.split("/")[-1]
        print_cyan(f"  [↓] Downloading {ext_name}...")
        
        try:
            urllib.request.urlretrieve(ext_url, filename)
            print_green(f"  [+] Installing {ext_name}...")
            
            run_command(
                ["antigravity", "--install-extension", filename],
                capture_output=True,
                check=True,
                shell=shell
            )
            
            os.remove(filename)
            print_green(f"  [✓] {ext_name} installed successfully.")
            return True
            
        except Exception as e:
            print_error(f"  [!] Failed to download/install {ext_name}: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return False
    else:
        # Install from Open VSX
        print_green(f"  [+] Installing {ext_name} from Open VSX...")
        
        try:
            run_command(
                ["antigravity", "--install-extension", ext_id],
                capture_output=True,
                check=True,
                shell=shell
            )
            print_green(f"  [✓] {ext_name} installed successfully.")
            return True
            
        except Exception as e:
            print_error(f"  [!] Failed to install {ext_name} from gallery: {e}")
            return False


def check_extension_installed(ext_id: str) -> bool:
    """
    Check if an extension is installed.
    
    Args:
        ext_id: Extension ID to check
    
    Returns:
        True if extension is installed, False otherwise
    """
    try:
        result = run_command(
            ["antigravity", "--list-extensions"],
            capture_output=True,
            check=True
        )
        output = result.stdout.decode('utf-8')
        return ext_id in output
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def run_powershell_script(script_path: str) -> bool:
    """
    Run a PowerShell script (Windows only).
    
    Args:
        script_path: Path to the PowerShell script
    
    Returns:
        True if script ran successfully, False otherwise
    """
    from .platform import is_windows
    
    if not is_windows():
        from .ui import print_error
        print_error("PowerShell scripts can only be run on Windows")
        return False
    
    return run_command_silent(["powershell", "-File", script_path])


def open_file(filepath: str) -> bool:
    """
    Open a file with the default application.
    
    Args:
        filepath: Path to the file to open
    
    Returns:
        True if file was opened successfully, False otherwise
    """
    from .platform import is_windows, is_macos
    
    try:
        if is_windows():
            run_command(["start", filepath], shell=True)
        elif is_macos():
            run_command(["open", filepath])
        else:
            run_command(["xdg-open", filepath])
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def open_url(url: str) -> bool:
    """
    Open a URL in the default browser.
    
    Args:
        url: URL to open
    
    Returns:
        True if URL was opened successfully, False otherwise
    """
    import webbrowser
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False
