import os
import shutil
import datetime
from pathlib import Path

# Configuration
INCOMING_DIR = Path("0. Incoming")
RAW_DIR = INCOMING_DIR / "raw"
STAGING_DIR = INCOMING_DIR / "staging"
PROCESSED_DIR = INCOMING_DIR / "processed"
FYI_DIR = INCOMING_DIR / "fyi"

# Ensure directories exist
for dir_path in [RAW_DIR, STAGING_DIR, PROCESSED_DIR, FYI_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def get_timestamp():
    """Generate a timestamp for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def scan_pending_content():
    """Scan all Incoming directories for unprocessed files."""
    pending_files = []
    
    dirs_to_scan = [
        RAW_DIR,
        STAGING_DIR,
        INCOMING_DIR,
    ]
    
    for dir_path in dirs_to_scan:
        if dir_path.exists():
            for f in dir_path.iterdir():
                if f.is_file() and f.name not in [".gitkeep"]:
                    pending_files.append(f)
    
    return pending_files

def get_file_category(filepath):
    """Categorize file based on type and content."""
    ext = filepath.suffix.lower()
    
    # Text files
    if ext in ['.md', '.txt', '.json', '.xml', '.csv', '.yaml', '.yml']:
        return 'text'
    
    # Image files
    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        return 'image'
    
    # Document files
    if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
        return 'document'
    
    # Code files
    if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css']:
        return 'code'
    
    # Archive files
    if ext in ['.zip', '.tar', '.gz', '.rar']:
        return 'archive'
    
    return 'other'

def move_to_processed(src, tag="processed"):
    """Move file to processed directory with timestamp prefix."""
    timestamp = get_timestamp()
    name = src.stem
    ext = src.suffix
    new_filename = f"{timestamp}_{name}{ext}"
    dest = PROCESSED_DIR / new_filename
    
    shutil.move(str(src), str(dest))
    return dest

def move_to_fyi(src, topic="reference"):
    """Move file to FYI directory with topic-based filename."""
    timestamp = get_timestamp()
    name = src.stem
    ext = src.suffix
    new_filename = f"{timestamp}_{topic}{ext}"
    dest = FYI_DIR / new_filename
    
    shutil.move(str(src), str(dest))
    return dest

def main():
    """Main scan and report function."""
    print(f"--- 📂 Scanning {INCOMING_DIR} for pending content ---")
    
    pending_files = scan_pending_content()
    
    if not pending_files:
        print("✅ Inbox is clean. No pending items to process.")
        return
    
    print(f"🔎 Found {len(pending_files)} pending file(s):")
    
    for filepath in pending_files:
        category = get_file_category(filepath)
        size = filepath.stat().st_size
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        print(f"  📄 {filepath.name}")
        print(f"     📍 Location: {filepath.parent.name}/")
        print(f"     📏 Size: {size_str}")
        print(f"     🏷️  Category: {category}")
        print()

def scan_and_process():
    """Alias for vacuum integration."""
    main()

if __name__ == "__main__":
    main()
