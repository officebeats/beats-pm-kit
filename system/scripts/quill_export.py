import sqlite3
import os
import json
import sys
from pathlib import Path

def get_last_5_meetings():
    db_path = str(Path.home() / "Library" / "Application Support" / "Quill" / "quill.db")
    if not os.path.exists(db_path):
        return []
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = """
        SELECT 
            COALESCE(title, llmTitle, manualTitle, 'Untitled Meeting') as title, 
            observedAt, 
            participants, 
            audio_transcript 
        FROM Meeting 
        WHERE audio_transcript IS NOT NULL 
        ORDER BY observedAt DESC 
        LIMIT 5
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def extract_text(transcript_json):
    if not transcript_json:
        return ""
    try:
        data = json.loads(transcript_json)
        if isinstance(data, dict):
            blocks = data.get("blocks", [])
            return " ".join([b.get("text", "") for b in blocks if b.get("text")])
        return transcript_json
    except Exception:
        return transcript_json

if __name__ == "__main__":
    meetings = get_last_5_meetings()
    data = []
    for m in meetings:
        data.append({
            "title": m[0],
            "timestamp": m[1],
            "participants": m[2],
            "transcript": extract_text(m[3])
        })
    print(json.dumps(data))
