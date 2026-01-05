import sys
import os
import shutil
import datetime
import platform
import subprocess

# Configuration
STAGING_DIR = os.path.join(os.getcwd(), "00-DROP-FILES-HERE-00")
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_staging():
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)

def get_macos_clipboard_files():
    """Extracts file paths from macOS clipboard using AppleScript."""
    script = '''
    tell application "System Events"
        try
            set pboardData to get the clipboard as list
            return pboardData
        on error
            return ""
        end try
    end tell
    '''
    # Start simplistic: use swift or osascript to get file references
    # For now, we'll implement the text/image fallback for reliable Mac support
    # and suggest the user install 'pngpaste' for images if needed.
    return []

def save_image_windows():
    import ctypes
    # Implementation placeholder for direct Win32 API or fallback to PS
    # For reliability in this v1, we will call the existing PS script if on Windows
    # This ensures we don't break your current working setup while wrapping it.
    subprocess.run(["powershell", "-File", "Beats-PM-System/system/scripts/capture-clipboard.ps1"], check=True)

def save_image_mac():
    # Use pngpaste if available, otherwise fallback to text
    img_path = os.path.join(STAGING_DIR, f"screenshot_{TIMESTAMP}.png")
    try:
        subprocess.run(["pngpaste", img_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Captured: {img_path}")
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False

def save_text_clipboard():
    import pyperclip # Requires pip install pyperclip
    try:
        content = pyperclip.paste()
        if content:
            file_path = os.path.join(STAGING_DIR, f"clip_note_{TIMESTAMP}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Captured Text: {file_path}")
    except ImportError:
        print("Error: 'pyperclip' module not found. Please run: pip install pyperclip")

def main():
    ensure_staging()
    system = platform.system()

    print(f"--- Universal Ingest v1.0 ({system}) ---")

    if system == "Windows":
        # On Windows, we piggyback the solid PS script for now
        save_image_windows()
    elif system == "Darwin": # macOS
        # Try image first
        if not save_image_mac():
             # Fallback to Text
             # We assume text because file-copy on Mac requires specialized bridges
             # or 'osascript' parsing which is often flaky.
             # For a robust solution, we use 'pbpaste'
             try:
                content = subprocess.check_output("pbpaste").decode('utf-8')
                if content:
                    file_path = os.path.join(STAGING_DIR, f"clip_note_{TIMESTAMP}.txt")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Captured Text: {file_path}")
             except Exception as e:
                 print(f"Clipboard read error: {e}")
    else:
        print("Unsupported OS")

if __name__ == "__main__":
    main()
