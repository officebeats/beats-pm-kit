import os
import datetime
import shutil
from pathlib import Path

# Paths
BRAIN_ROOT = Path(os.getcwd())
TRANSCRIPTS_DIR = BRAIN_ROOT / "3. Meetings" / "transcripts"
ARCHIVE_DIR = BRAIN_ROOT / "3. Meetings" / "archive"
QUOTE_INDEX = BRAIN_ROOT / "3. Meetings" / "quote-index.md"

def ensure_dirs():
    if not ARCHIVE_DIR.exists():
        ARCHIVE_DIR.mkdir(parents=True)
    if not QUOTE_INDEX.exists():
        with open(QUOTE_INDEX, 'w', encoding='utf-8') as f:
            f.write("# Quote Index (Warm Memory)\n\n| Date | Title | Archive Path |\n| :--- | :--- | :--- |\n")

def archive_transcript(file_path):
    """
    1. Extract Metadata (Filename, Date)
    2. Log to quote-index.md
    3. Move to archive
    """
    ensure_dirs()
    
    path = Path(file_path)
    filename = path.name
    
    # Extract Date (Assumption: YYYY-MM-DD prefix)
    date_str = "Unknown"
    if filename[0:4].isdigit() and filename[4] == '-':
        date_str = filename[0:10]
        
    title = filename
    
    # 2. Log to Index
    entry = f"| {date_str} | {title} | `archive/{filename}` |\n"
    
    try:
        with open(QUOTE_INDEX, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(f"  📖 Indexed: {filename}")
    except Exception as e:
        print(f"  ⚠️ Global Index Failed: {e}")
        
    # 3. Move to Archive
    try:
        dest = ARCHIVE_DIR / filename
        shutil.move(file_path, dest)
        print(f"  ❄️  Archived: {filename}")
    except Exception as e:
        print(f"  ⚠️ Archive Move Failed: {e}")

if __name__ == "__main__":
    print("Librarian Module. Import into vacuum.py to use.")
