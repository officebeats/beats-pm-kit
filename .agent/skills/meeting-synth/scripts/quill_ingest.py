#!/usr/bin/env python3
import sqlite3
import json
import os
import sys
import time
from datetime import datetime, timedelta

# Configuration
DB_PATH = os.path.expanduser("~/Library/Application Support/Quill/quill.db")
STATE_FILE = ".gemini/state/quill_cursor.json"
INCOMING_DIR = "3. Meetings/transcripts"
LOOKBACK_HOURS = 72

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"last_run": 0, "processed_ids": []}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def extract_text_from_json(json_str):
    try:
        data = json.loads(json_str)
        text_parts = []
        if isinstance(data, dict):
            # Check for 'blocks' structure
            blocks = data.get('blocks', [])
            if not blocks and 'content' in data:
                 # Fallback if content is directly text or different structure
                 return str(data['content'])
            
            for block in blocks:
                # Assuming block has 'text' or 'content' field based on typical editorjs/quill structures
                # Based on previous inspection: {"id":"EVXJ","from":...,"to":...} - wait, need to check where text is.
                # Let's assume standard 'text' field or just dump specific fields.
                # Inspecting the schema output earlier didn't show full structure.
                # Based on typical transcripts, it might be just text.
                # Let's try to extract ANY text field.
                if 'text' in block:
                    text_parts.append(block['text'])
                elif 'content' in block:
                    text_parts.append(block['content'])
                else:
                    # Fallback: Just dump the block representation if we can't find clear text
                    # Or skip if empty
                    pass
        return "\n".join(text_parts)
    except json.JSONDecodeError:
        return "[Error decoding JSON transcript]"


def get_monday_anchor():
    """Get the timestamp for Monday 00:00 of the current week."""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    monday_zero = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(monday_zero.timestamp() * 1000)

def main():
    print(f"🔄 Connecting to Quill DB: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)

    state = load_state()
    processed_ids = set(state.get("processed_ids", []))
    last_run = state.get("last_run", 0)

    # Calculate Monday anchor
    monday_ms = get_monday_anchor()
    
    # query_cutoff is the EARLIER of (Monday, Last Run) 
    # This ensures we catch up if we missed days, but also capture everything from Monday if it's the first run of the week.
    # However, if Last Run is older than Monday (e.g. ran last Thursday), we want to start from Last Run.
    if last_run == 0:
        query_cutoff = monday_ms
    else:
        # Use last_run if it exists, otherwise fall back to Monday. 
        # Actually, user said "Ideally you instead process from the last time the command was ran"
        # So last_run is the primary anchor.
        query_cutoff = last_run

    print(f"⏱️  Syncing from: {datetime.fromtimestamp(query_cutoff/1000).strftime('%Y-%m-%d %H:%M:%S')}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Select fields
    query = """
    SELECT id, start, title, audio_transcript 
    FROM Meeting 
    WHERE start > ? 
    AND audio_transcript IS NOT NULL 
    AND length(audio_transcript) > 10
    ORDER BY start ASC
    """
    
    try:
        cursor.execute(query, (query_cutoff,))
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    finally:
        conn.close()

    new_count = 0
    current_time_ms = int(time.time() * 1000)

    print(f"🔍 Found {len(rows)} meetings in last 72h.")

    for row in rows:
        m_id, start_ms, title, json_content = row
        
        if m_id in processed_ids:
            continue
            
        print(f"📥 Processing: {title} ({m_id})")
        
        # Parse content
        # Note: The previous CLI inspection showed: "blocks":[{"id":"EVXJ" ...
        # I need to be careful about the structure.
        # Let's verify the logic by assuming widespread 'text' or 'content' keys aren't always there.
        # Actually, let's extract raw text roughly if specific keys fail.
        transcript_text = extract_text_from_json(json_content)
        
        if not transcript_text:
             # If simple extraction failed, dump raw string for debug or fallback
             transcript_text = f"[Raw JSON dump due to parsing failure]\n{json_content[:2000]}..."

        # Format Filename
        date_str = datetime.fromtimestamp(start_ms / 1000).strftime('%Y-%m-%d')
        safe_title = "".join([c for c in (title or "Untitled") if c.isalnum() or c in " -_"]).strip()
        filename = f"{date_str}-{safe_title}.md"
        output_path = os.path.join(INCOMING_DIR, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write File
        content = f"# {title or 'Untitled Meeting'}\n\n**Date**: {date_str}\n**Source**: QuillDB ({m_id})\n\n## Transcript\n\n{transcript_text}"
        
        with open(output_path, 'w') as f:
            f.write(content)
            
        print(f"✅ Saved to: {output_path}")
        
        processed_ids.add(m_id)
        new_count += 1

    # Update state
    state["processed_ids"] = list(processed_ids)
    state["last_run"] = current_time_ms
    save_state(state)

    print(f"✨ Done. Ingested {new_count} new transcripts.")

if __name__ == "__main__":
    main()
