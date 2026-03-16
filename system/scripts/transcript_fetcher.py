"""
Transcript Fetcher (10 Business Day Logic)
Fetches Quill transcripts and deposits them in 0. Incoming/
"""

import sys
import datetime
from pathlib import Path

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent

# Add BRAIN_ROOT to path for imports
sys.path.insert(0, str(BRAIN_ROOT))

try:
    from system.scripts import db_bridge
    from system.utils.ui import print_cyan, print_success, print_gray
except ImportError:
    # Fallback if structure is still hydrating
    db_bridge = None

def get_business_days_ago(n):
    """Calculate the timestamp for n business days ago."""
    d = datetime.date.today()
    count = 0
    while count < n:
        d -= datetime.timedelta(days=1)
        if d.weekday() < 5: # Monday to Friday
            count += 1
    return datetime.datetime.combine(d, datetime.time.min)

def main():
    print_cyan(f"--- 🎙️ Transcript Fetcher (10 Business Days) ---")
    
    if not db_bridge:
        print("Error: db_bridge.py not found or imports failed.")
        return

    db_path = db_bridge.get_quill_db_path()
    if not db_path:
        print("Quill DB not found.")
        return

    # Calculate threshold (approx 10 business days)
    threshold_dt = get_business_days_ago(10)
    threshold_ms = int(threshold_dt.timestamp() * 1000)
    
    print_gray(f"Filtering meetings since: {threshold_dt.strftime('%Y-%m-%d')}")
    
    # We'll use a modified version of extract_transcripts or similar logic
    # instead of modifying db_bridge.py which might be used elsewhere
    import sqlite3
    import shutil
    import json
    
    INCOMING_DIR = BRAIN_ROOT / "0. Incoming"
    TRANSCRIPTS_DIR = BRAIN_ROOT / "3. Meetings/transcripts"
    
    try:
        temp_db = INCOMING_DIR / "temp_quill_fetch.db"
        shutil.copy2(db_path, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, start, audio_transcript FROM Meeting WHERE audio_transcript IS NOT NULL AND start >= ? ORDER BY start DESC", (threshold_ms,))
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            title = row[0] or "Untitled Meeting"
            timestamp = row[1]
            transcript_json_str = row[2]
            
            dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
            date_str = dt.strftime("%Y-%m-%d")
            safe_title = db_bridge.sanitize_filename(title)
            filename = f"{date_str}_{safe_title}.txt"
            
            target_path = INCOMING_DIR / filename
            processed_path = TRANSCRIPTS_DIR / filename
            
            if target_path.exists() or processed_path.exists():
                continue
                
            try:
                data = json.loads(transcript_json_str)
                blocks = data.get('blocks', [])
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n")
                    f.write(f"Date: {dt.strftime('%Y-%m-%d %H:%M')}\n\n")
                    for block in blocks:
                        line = db_bridge.parse_transcript_block(block)
                        if line:
                            f.write(line)
                print_success(f"Imported: {filename}")
                count += 1
            except:
                continue
        
        conn.close()
        temp_db.unlink()
        
        if count == 0:
            print_gray("No new meetings found in the last 10 business days.")
        else:
            print_success(f"Successfully processed {count} new meetings.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
