"""
Filesystem Utilities Module

Provides consistent file system operations across all Beats PM System scripts.
"""

import shutil
from typing import Optional, List, Union
from pathlib import Path


def ensure_directory(path: Union[str, Path]) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        from .ui import print_error
        print_error(f"Failed to create directory {path}: {e}")
        return False


def ensure_file_directory(filepath: Union[str, Path]) -> bool:
    """Ensure the parent directory of a file exists."""
    return ensure_directory(Path(filepath).parent)


def file_exists(path: Union[str, Path]) -> bool:
    """Check if a file exists."""
    return Path(path).is_file()


def directory_exists(path: Union[str, Path]) -> bool:
    """Check if a directory exists."""
    return Path(path).is_dir()


def path_exists(path: Union[str, Path]) -> bool:
    """Check if a path (file or directory) exists."""
    return Path(path).exists()


def read_file(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Read the contents of a file."""
    try:
        return Path(path).read_text(encoding=encoding)
    except (IOError, UnicodeDecodeError) as e:
        from .ui import print_error
        print_error(f"Failed to read file {path}: {e}")
        return None


def read_file_lines(path: Union[str, Path], encoding: str = 'utf-8') -> Optional[List[str]]:
    """Read the lines of a file."""
    try:
        return Path(path).read_text(encoding=encoding).splitlines(keepends=True)
    except (IOError, UnicodeDecodeError) as e:
        from .ui import print_error
        print_error(f"Failed to read file {path}: {e}")
        return None


def write_file(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Write content to a file, creating parent directories if needed."""
    try:
        p = Path(path)
        ensure_file_directory(p)
        p.write_text(content, encoding=encoding)
        return True
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to write file {path}: {e}")
        return False


def append_file(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Append content to a file."""
    try:
        with Path(path).open('a', encoding=encoding) as f:
            f.write(content)
        return True
    except IOError as e:
        from .ui import print_error
        print_error(f"Failed to append to file {path}: {e}")
        return False


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy a file from source to destination."""
    try:
        s, d = Path(src), Path(dst)
        ensure_file_directory(d)
        shutil.copy2(s, d)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to copy file from {src} to {dst}: {e}")
        return False


def copy_directory(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy a directory from source to destination."""
    try:
        s, d = Path(src), Path(dst)
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(s, d)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to copy directory from {src} to {dst}: {e}")
        return False


def delete_file(path: Union[str, Path]) -> bool:
    """Delete a file."""
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
        return True
    except OSError as e:
        from .ui import print_error
        print_error(f"Failed to delete file {path}: {e}")
        return False


def delete_directory(path: Union[str, Path]) -> bool:
    """Delete a directory and all its contents."""
    try:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)
        return True
    except (IOError, shutil.Error) as e:
        from .ui import print_error
        print_error(f"Failed to delete directory {path}: {e}")
        return False


def get_relative_path(path: Union[str, Path], start: Optional[Union[str, Path]] = None) -> str:
    """Get a relative path."""
    p = Path(path)
    s = Path(start) if start else Path.cwd()
    try:
        return str(p.relative_to(s))
    except ValueError:
        return str(p)


def get_absolute_path(path: Union[str, Path]) -> str:
    """Get the absolute path."""
    return str(Path(path).resolve())


def join_paths(*paths: Union[str, Path]) -> str:
    """Join multiple path components."""
    return str(Path(*paths))


def get_filename(path: Union[str, Path]) -> str:
    """Get the filename from a path."""
    return Path(path).name


def get_directory(path: Union[str, Path]) -> str:
    """Get the directory from a path."""
    return str(Path(path).parent)


def get_file_extension(path: Union[str, Path]) -> str:
    """Get the file extension from a path."""
    return Path(path).suffix


def get_file_stem(path: Union[str, Path]) -> str:
    """Get the file stem from a path."""
    return Path(path).stem


def list_files(directory: Union[str, Path], pattern: str = '*', recursive: bool = False) -> List[str]:
    """List files in a directory."""
    p = Path(directory)
    gen = p.rglob(pattern) if recursive else p.glob(pattern)
    return [str(f) for f in gen if f.is_file()]


def get_file_size(path: Union[str, Path]) -> Optional[int]:
    """Get the size of a file in bytes."""
    try:
        return Path(path).stat().st_size
    except OSError:
        return None


def is_empty_directory(path: Union[str, Path]) -> bool:
    """Check if a directory is empty."""
    p = Path(path)
    if not p.is_dir():
        return True
    return not any(p.iterdir())


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip('. ').strip() or 'unnamed'


def validate_path(path: Union[str, Path], must_exist: bool = False) -> bool:
    """Validate a file path."""
    try:
        p = Path(path)
        if must_exist and not p.exists():
            return False
        return True
    except (OSError, ValueError):
        return False
