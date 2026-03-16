
import sys
import datetime
from pathlib import Path
import sqlite3
import shutil
import json
import traceback

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent

# Add BRAIN_ROOT to path for imports
sys.path.insert(0, str(BRAIN_ROOT))

# Attempt imports
try:
    from system.scripts import db_bridge
    from system.utils.ui import print_cyan, print_success, print_gray
except ImportError as e:
    print(f"Import Error: {e}")
    db_bridge = None
    def print_cyan(x): print(x)
    def print_success(x): print(x)
    def print_gray(x): print(x)

def main():
    print_cyan(f"--- 🎙️ Historical Transcript Fetcher (Since Sept 2025) ---")
    
    if db_bridge is None:
        print("Error: db_bridge module not loaded properly.")
        return

    db_path = db_bridge.get_quill_db_path()
    if not db_path:
        print("Quill DB not found.")
        return

    # Set threshold to Sept 1, 2025
    threshold_dt = datetime.datetime(2025, 9, 1)
    threshold_ms = int(threshold_dt.timestamp() * 1000)
    
    print_gray(f"Filtering meetings since: {threshold_dt.strftime('%Y-%m-%d')}")
    
    INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
    
    if not INCOMING_DIR.exists():
        INCOMING_DIR.mkdir(exist_ok=True)
    
    try:
        temp_db = INCOMING_DIR / "temp_quill_fetch_hist.db"
        shutil.copy2(db_path, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Query for all meetings since Sept 1
        cursor.execute("SELECT title, start, audio_transcript FROM Meeting WHERE audio_transcript IS NOT NULL AND start >= ? ORDER BY start DESC", (threshold_ms,))
        rows = cursor.fetchall()
        
        count = 0
        search_hits = 0
        
        for row in rows:
            title = row[0] or "Untitled Meeting"
            timestamp = row[1]
            transcript_json_str = row[2]
            
            dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
            date_str = dt.strftime("%Y-%m-%d")
            safe_title = db_bridge.sanitize_filename(title)
            filename = f"{date_str}_{safe_title}.txt"
            
            target_path = INCOMING_DIR / filename
            
            # Filter for specific keywords
            try:
                data = json.loads(transcript_json_str)
            except:
                continue

            if not data:
                continue

            blocks = data.get('blocks', [])
            full_text = ""
            for block in blocks:
                line = db_bridge.parse_transcript_block(block)
                if line:
                    full_text += line
            
            # Search logic: "Larry" AND ("Athena" OR "Block")
            matches_keywords = "larry" in full_text.lower() and ("athena" in full_text.lower() or "block" in full_text.lower())
            
            if matches_keywords:
                 print_success(f"MATCH FOUND: {filename}")
                 with open(target_path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n")
                    f.write(f"Date: {dt.strftime('%Y-%m-%d %H:%M')}\n\n")
                    f.write(full_text)
                 search_hits += 1
            
            count += 1
        
        conn.close()
        temp_db.unlink()
        
        print_success(f"Scanned {count} meetings. Found {search_hits} matches saved to 0. Incoming/")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
