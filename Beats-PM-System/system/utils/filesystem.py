"""
Filesystem Utilities Module

Provides consistent file system operations across all Beats PM System scripts.
"""

import os
import shutil
from typing import Optional, List, Union
from pathlib import Path


def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
    
    Returns:
        True if directory exists or was created, False on error
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError as e:
        from .ui import print_error
        print_error(f"Failed to create directory {path}: {e}")
        return False


def ensure_file_directory(filepath: str) -> bool:
    """
    Ensure the parent directory of a file exists.
    
    Args:
        filepath: Path to a file
    
    Returns:
        True if parent directory exists or was created, False on error
    """
    parent_dir = os.path.dirname(filepath)
    if parent_dir and not os.path.exists(parent_dir):
        return ensure_directory(parent_dir)
    return True


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: File path to check
    
    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(path)


def directory_exists(path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        path: Directory path to check
    
    Returns:
        True if directory exists, False otherwise
    """
    return os.path.isdir(path)


def path_exists(path: str) -> bool:
    """
    Check if a path (file or directory) exists.
    
    Args:
        path: Path to check
    
    Returns:
        True if path exists, False otherwise
    """
    return os.path.exists(path)


def read_file(path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Read the contents of a file.
    
    Args:
        path: Path to the file
        encoding: File encoding (default: utf-8)
    
    Returns:
        File contents as string, or None on error
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to read file {path}: {e}")
        return None


def read_file_lines(path: str, encoding: str = 'utf-8') -> Optional[List[str]]:
    """
    Read the lines of a file.
    
    Args:
        path: Path to the file
        encoding: File encoding (default: utf-8)
    
    Returns:
        List of file lines, or None on error
    """
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.readlines()
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to read file {path}: {e}")
        return None


def write_file(path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Write content to a file, creating parent directories if needed.
    
    Args:
        path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
    
    Returns:
        True if write was successful, False on error
    """
    try:
        ensure_file_directory(path)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to write file {path}: {e}")
        return False


def append_file(path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Append content to a file.
    
    Args:
        path: Path to the file
        content: Content to append
        encoding: File encoding (default: utf-8)
    
    Returns:
        True if append was successful, False on error
    """
    try:
        with open(path, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to append to file {path}: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
    
    Returns:
        True if copy was successful, False on error
    """
    try:
        ensure_file_directory(dst)
        shutil.copy(src, dst)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to copy file from {src} to {dst}: {e}")
        return False


def copy_directory(src: str, dst: str) -> bool:
    """
    Copy a directory from source to destination.
    
    Args:
        src: Source directory path
        dst: Destination directory path
    
    Returns:
        True if copy was successful, False on error
    """
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to copy directory from {src} to {dst}: {e}")
        return False


def delete_file(path: str) -> bool:
    """
    Delete a file.
    
    Args:
        path: Path to the file to delete
    
    Returns:
        True if deletion was successful, False on error
    """
    try:
        if os.path.exists(path):
            os.remove(path)
        return True
    except OSError as e:
        from .ui import print_error
        print_error(f"Failed to delete file {path}: {e}")
        return False


def delete_directory(path: str) -> bool:
    """
    Delete a directory and all its contents.
    
    Args:
        path: Path to the directory to delete
    
    Returns:
        True if deletion was successful, False on error
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to delete directory {path}: {e}")
        return False


def get_relative_path(path: str, start: Optional[str] = None) -> str:
    """
    Get a relative path.
    
    Args:
        path: The path to make relative
        start: The start directory (default: current working directory)
    
    Returns:
        Relative path
    """
    if start is None:
        start = os.getcwd()
    return os.path.relpath(path, start)


def get_absolute_path(path: str) -> str:
    """
    Get the absolute path.
    
    Args:
        path: The path to convert
    
    Returns:
        Absolute path
    """
    return os.path.abspath(path)


def join_paths(*paths: str) -> str:
    """
    Join multiple path components.
    
    Args:
        *paths: Path components to join
    
    Returns:
        Joined path
    """
    return os.path.join(*paths)


def get_filename(path: str) -> str:
    """
    Get the filename from a path.
    
    Args:
        path: File path
    
    Returns:
        Filename without directory
    """
    return os.path.basename(path)


def get_directory(path: str) -> str:
    """
    Get the directory from a path.
    
    Args:
        path: File or directory path
    
    Returns:
        Directory path
    """
    return os.path.dirname(path)


def get_file_extension(path: str) -> str:
    """
    Get the file extension from a path.
    
    Args:
        path: File path
    
    Returns:
        File extension (including the dot)
    """
    return os.path.splitext(path)[1]


def get_file_stem(path: str) -> str:
    """
    Get the file stem (filename without extension) from a path.
    
    Args:
        path: File path
    
    Returns:
        File stem
    """
    return os.path.splitext(os.path.basename(path))[0]


def list_files(directory: str, pattern: Optional[str] = None, recursive: bool = False) -> List[str]:
    """
    List files in a directory.
    
    Args:
        directory: Directory to list
        pattern: Optional glob pattern to filter files
        recursive: Whether to search recursively
    
    Returns:
        List of file paths
    """
    import glob
    
    if recursive:
        search_pattern = join_paths(directory, '**', pattern or '*')
        return glob.glob(search_pattern, recursive=True)
    else:
        search_pattern = join_paths(directory, pattern or '*')
        return glob.glob(search_pattern)


def get_file_size(path: str) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        path: Path to the file
    
    Returns:
        File size in bytes, or None on error
    """
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def is_empty_directory(path: str) -> bool:
    """
    Check if a directory is empty.
    
    Args:
        path: Directory path to check
    
    Returns:
        True if directory is empty, False otherwise
    """
    if not directory_exists(path):
        return True
    return len(os.listdir(path)) == 0


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove invalid characters for Windows and Unix
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed'
    
    return filename


def validate_path(path: str, must_exist: bool = False) -> bool:
    """
    Validate a file path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
    
    Returns:
        True if path is valid, False otherwise
    """
    try:
        # Check if path is absolute or relative
        if not os.path.isabs(path):
            # It's a relative path, check if it's valid
            os.path.normpath(path)
        
        if must_exist and not path_exists(path):
            return False
        
        return True
    except (OSError, ValueError):
        return False
