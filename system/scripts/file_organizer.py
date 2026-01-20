import os
import shutil
import datetime
from pathlib import Path

# Configuration
INCOMING_DIR = Path("0. Incoming")
PROCESSED_DIR = INCOMING_DIR / "processed"
FYI_DIR = INCOMING_DIR / "fyi"
BRAIN_ROOT = Path(".").resolve()

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FYI_DIR.mkdir(parents=True, exist_ok=True)

def scan_and_process():
    print(f"--- 📂 Scanning {INCOMING_DIR} for new files ---")
    
    # Get all files in Incoming (not directories)
    new_files = [f for f in INCOMING_DIR.iterdir() if f.is_file() and f.name not in ["BRAIN_DUMP.md", ".gitkeep"]]

    if not new_files:
        print("✅ No new files found.")
        return

    print(f"🔎 Found {len(new_files)} file(s): {', '.join([f.name for f in new_files])}")
    
    for file_path in new_files:
        filename = file_path.name
        
        # 🤖 Auto-Sort Heuristic: Transcripts (YYYY-MM-DD_*.txt)
        if filename[0:4].isdigit() and filename[4] == '-' and filename.endswith(".txt"):
            print(f"🤖 Auto-detected Transcript: {filename} -> Task Source")
            move_to_processed(file_path, filename, "task_source")
            continue

        print(f"\n📄 Processing: {filename}")
        # Note: In an autonomous environment, input() is discouraged. 
        # We assume the agent will handle classified moves.
        # Defaulting to FYI if unclassified.
        print(f"   -> 📂 Moving to {FYI_DIR} (Default Reference)")
        new_path = FYI_DIR / filename
        shutil.move(str(file_path), str(new_path))

def move_to_processed(src, filename, tag):
    # Add timestamp to filename to prevent collisions
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = src.stem
    ext = src.suffix
    new_filename = f"{timestamp}_{name}{ext}"
    dest = PROCESSED_DIR / new_filename
    
    shutil.move(str(src), str(dest))
    print(f"   -> ✅ Archived to {PROCESSED_DIR} (Tag: {tag})")

if __name__ == "__main__":
    scan_and_process()
