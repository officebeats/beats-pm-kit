"""
DB Bridge (Stealth Integration)

Extracts data from local SQLite databases (Quill) and deposits
formatted transcripts into 0. Incoming/ for processing.

Privacy: READ-ONLY access.
"""

import sqlite3
import shutil
import os
import sys
import json
import datetime
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent
INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
TRANSCRIPTS_DIR = BRAIN_ROOT / "3. Meetings/transcripts"

def get_quill_db_path():
    """Locate Quill DB on Windows or Mac."""
    home = Path.home()
    
    # MacOS (Standard Electron App Path)
    # User Note: When on Mac, verify this path exists or update if using App Store version.
    mac_path = home / "Library/Application Support/Quill/quill.db"
    if mac_path.exists():
        return mac_path
        
    # Windows
    appdata = os.getenv('APPDATA')
    if appdata:
        win_path = Path(appdata) / "Quill" / "quill.db"
        if win_path.exists():
            return win_path
            
    return None

def sanitize_filename(title):
    return "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()

def parse_transcript_block(block):
    speaker = block.get('speaker_id', 'Unknown')
    text = block.get('text', '')
    if text:
        return f"[{speaker}]: {text}\n\n"
    return None

def extract_transcripts(db_path):
    """Dump transcripts from DB."""
    print(f"  🔌 Connecting to: {db_path}")
    
    try:
        # Copy to temp to avoid locking issues
        temp_db = INCOMING_DIR / "temp_quill_dump.db"
        shutil.copy2(db_path, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Query Meeting Table
        # We only care about meetings that have a transcript
        cursor.execute("SELECT title, start, audio_transcript FROM Meeting WHERE audio_transcript IS NOT NULL ORDER BY start DESC LIMIT 10")
        rows = cursor.fetchall()
        
        imported_count = 0
        
        for row in rows:
            title = row[0] or "Untitled Meeting"
            timestamp = row[1] # ms
            transcript_json_str = row[2]
            
            # 1. Parse Date
            dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
            date_str = dt.strftime("%Y-%m-%d")
            
            # 2. Sanitize Title
            safe_title = sanitize_filename(title)
            filename = f"{date_str}_{safe_title}.txt"
            
            # 3. Check for duplicates (in Incoming AND processed Transcripts)
            target_path = INCOMING_DIR / filename
            processed_path = TRANSCRIPTS_DIR / filename
            
            if target_path.exists() or processed_path.exists():
                print(f"  ⏭️  Skipping {filename} (Already exists)")
                continue
            
            # 4. Parse JSON
            try:
                data = json.loads(transcript_json_str)
                blocks = data.get('blocks', [])
                
                # 5. Write to File
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n")
                    f.write(f"Date: {dt.strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"Source: Quill Auto-Import\n\n")
                    
                    for block in blocks:
                        line = parse_transcript_block(block)
                        if line:
                            f.write(line)
                
                print(f"  ✅ Imported: {filename}")
                imported_count += 1
                
            except json.JSONDecodeError:
                print(f"  ❌ Error decoding JSON for {title}")
                continue



        conn.close()
        
        # Cleanup
        if temp_db.exists():
            os.remove(temp_db)
        
        # Clean up debug dumps if they exist
        debug_dump = INCOMING_DIR / f"quill_dump_{datetime.date.today()}.txt"
        if debug_dump.exists():
            os.remove(debug_dump)
            
    except Exception as e:
        print(f"  ❌ DB Error: {e}")

def main():
    print("--- 🕵️ External Data Bridge ---")
    
    # 1. Quill
    q_path = get_quill_db_path()
    if q_path:
        extract_transcripts(q_path)
    else:
        print("  [Quill] Database not found in default paths.")

if __name__ == "__main__":
    main()
