"""
Clipboard Bridge (Cross-Platform)

Extracts text, images, OR FILES from the system clipboard and saves them to
0. Incoming/ for processing by the /paste or /dump workflow.

Supports: Windows, macOS
Content Types: Text, Images, Files (from file manager)
Dependencies: Pillow (for images)
"""

import os
import sys
import datetime
import subprocess
import shutil
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent
INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
RAW_DIR = INCOMING_DIR / "raw"
STAGING_DIR = INCOMING_DIR / "staging"


def validate_dependencies():
    """Validate and install required dependencies."""
    try:
        from PIL import ImageGrab
    except ImportError:
        print("  ⚠️ Pillow not installed. Installing...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--break-system-packages", "Pillow>=11.0.0"
            ])
            print("  ✅ Pillow installed successfully")
        except subprocess.CalledProcessError:
            print("  ❌ Failed to install Pillow")
            print("  Please install manually: pip3 install --break-system-packages Pillow")
            return False
    return True


# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)


def get_platform():
    """Detect current platform."""
    import platform
    return platform.system()


def get_timestamp():
    """Generate a timestamp for filenames."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")


# --- TEXT CLIPBOARD ---

def get_text_from_clipboard_windows():
    """Get text from Windows clipboard using PowerShell."""
    try:
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  ⚠️ Windows text clipboard error: {e}")
    return None


def get_text_from_clipboard_mac():
    """Get text from macOS clipboard using pbpaste."""
    try:
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  ⚠️ macOS text clipboard error: {e}")
    return None


def get_text_from_clipboard():
    """Get text from clipboard (cross-platform)."""
    platform = get_platform()
    if platform == "Windows":
        return get_text_from_clipboard_windows()
    elif platform == "Darwin":
        return get_text_from_clipboard_mac()
    else:
        print(f"  ⚠️ Unsupported platform: {platform}")
        return None


# --- IMAGE CLIPBOARD ---

def get_image_from_clipboard():
    """Get image from clipboard using Pillow."""
    try:
        from PIL import ImageGrab
        image = ImageGrab.grabclipboard()
        # ImageGrab returns None, an Image, or a list of file paths
        if image is not None and not isinstance(image, list):
            return image
    except ImportError:
        print("  ⚠️ Pillow not installed. Run: pip install Pillow")
    except Exception as e:
        print(f"  ⚠️ Image clipboard error: {e}")
    return None


# --- FILE CLIPBOARD ---

def get_files_from_clipboard_windows():
    """Get file paths from Windows clipboard using PowerShell."""
    try:
        # Get-Clipboard -Format FileDropList returns file paths
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard -Format FileDropList | ForEach-Object { $_.FullName }"],
            capture_output=True,
            shell=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0 and result.stdout.strip():
            paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
            # Verify paths exist
            valid_paths = [p for p in paths if os.path.exists(p)]
            if valid_paths:
                return valid_paths
    except Exception as e:
        print(f"  ⚠️ Windows file clipboard error: {e}")
    return None


def get_files_from_clipboard_mac():
    """Get file paths from macOS clipboard using AppleScript."""
    try:
        # AppleScript to get file paths from clipboard
        script = '''
        tell application "System Events"
            try
                set theFiles to (the clipboard as «class furl»)
                return POSIX path of theFiles
            on error
                return ""
            end try
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            path = result.stdout.strip()
            if os.path.exists(path):
                return [path]
    except Exception as e:
        print(f"  ⚠️ macOS file clipboard error: {e}")
    return None


def get_files_from_clipboard_pillow():
    """Get file paths from clipboard using Pillow (fallback for images copied as files)."""
    try:
        from PIL import ImageGrab
        result = ImageGrab.grabclipboard()
        # On Windows, copying files returns a list of paths
        if isinstance(result, list):
            valid_paths = [p for p in result if os.path.exists(p)]
            if valid_paths:
                return valid_paths
    except ImportError:
        pass  # Pillow not available
    except Exception:
        pass
    return None


def get_files_from_clipboard():
    """Get files from clipboard (cross-platform)."""
    # Try Pillow first (works on Windows for copied files)
    files = get_files_from_clipboard_pillow()
    if files:
        return files
    
    platform = get_platform()
    if platform == "Windows":
        return get_files_from_clipboard_windows()
    elif platform == "Darwin":
        return get_files_from_clipboard_mac()
    return None


# --- SAVE FUNCTIONS ---

def save_text(text):
    """Save text content to incoming/raw."""
    timestamp = get_timestamp()
    filename = f"{timestamp}_clipboard.md"
    filepath = RAW_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Clipboard Capture: {timestamp}\n\n")
        f.write(f"---\n\n")
        f.write(text)
    
    print(f"  ✅ Saved text: {filename}")
    return filepath


def save_image(image):
    """Save image content to incoming/staging."""
    timestamp = get_timestamp()
    filename = f"{timestamp}_screenshot.png"
    filepath = STAGING_DIR / filename
    
    image.save(filepath, "PNG")
    
    print(f"  ✅ Saved image: {filename}")
    return filepath


def save_files(file_paths):
    """Copy files to incoming/staging."""
    saved = []
    timestamp = get_timestamp()
    
    for src_path in file_paths:
        src = Path(src_path)
        if src.is_file():
            # Preserve original filename with timestamp prefix
            dest_name = f"{timestamp}_{src.name}"
            dest = STAGING_DIR / dest_name
            shutil.copy2(src, dest)
            print(f"  ✅ Copied file: {dest_name}")
            saved.append(dest)
        elif src.is_dir():
            # Copy entire directory
            dest_name = f"{timestamp}_{src.name}"
            dest = STAGING_DIR / dest_name
            shutil.copytree(src, dest)
            print(f"  ✅ Copied folder: {dest_name}")
            saved.append(dest)
    
    return saved


# --- MAIN LOGIC ---

def main():
    print("--- 📋 Clipboard Bridge (/paste) ---")
    
    # Validate dependencies
    if not validate_dependencies():
        return
    
    # 1. Try to get FILES first (most specific)
    files = get_files_from_clipboard()
    if files:
        save_files(files)
        print(f"\n  📁 {len(files)} file(s) detected and copied.")
        print(f"  💡 Run '/dump' to process these files.")
        return
    
    # 2. Try to get image
    image = get_image_from_clipboard()
    if image is not None:
        save_image(image)
        print("\n  🖼️  Screenshot detected and saved.")
        print(f"  💡 Run '/dump' to process this image.")
        return
    
    # 3. Fall back to text
    text = get_text_from_clipboard()
    if text:
        save_text(text)
        print("\n  📝 Text detected and saved.")
        print(f"  💡 Run '/dump' to process this content.")
        return
    
    # 4. Empty clipboard
    print("  ❌ Clipboard is empty or contains unsupported content.")


if __name__ == "__main__":
    main()
