#!/usr/bin/env python3
"""
Quill Ingest Script (Centrifuge Protocol)

Stateful ingestion of meeting transcripts from the Quill SQLite database.
"""

import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configuration
DB_PATH = Path.home() / "Library/Application Support/Quill/quill.db"
STATE_FILE = Path(".gemini/state/quill_cursor.json")
OUTPUT_DIR = Path("3. Meetings/transcripts")


def load_state() -> Dict[str, Any]:
    """Load the ingestion state from the cursor file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"last_run": 0, "processed_ids": []}


def save_state(state: Dict[str, Any]) -> None:
    """Save the ingestion state to the cursor file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def extract_text_from_json(json_str: str) -> str:
    """Extract legible text from the Quill JSON transcript block."""
    try:
        data = json.loads(json_str)
        text_parts = []
        if isinstance(data, dict):
            blocks = data.get("blocks", [])
            if not blocks and "content" in data:
                return str(data["content"])

            for block in blocks:
                if "text" in block:
                    text_parts.append(block["text"])
                elif "content" in block:
                    text_parts.append(block["content"])

        return "\n".join(text_parts)
    except json.JSONDecodeError:
        return "[Error decoding JSON transcript]"


def get_monday_anchor() -> int:
    """Get the timestamp for Monday 00:00 of the current week (ms)."""
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    monday_zero = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(monday_zero.timestamp() * 1000)


def main() -> None:
    """Main ingestion pipeline."""
    print(f"🔄 Connecting to Quill DB: {DB_PATH}")

    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)

    state = load_state()
    processed_ids: Set[str] = set(state.get("processed_ids", []))
    last_run = state.get("last_run", 0)

    # Calculate Monday anchor
    monday_ms = get_monday_anchor()

    # Use last_run if it exists, otherwise fall back to Monday.
    query_cutoff = last_run if last_run > 0 else monday_ms

    dt_str = datetime.fromtimestamp(query_cutoff / 1000).strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏱️  Syncing from: {dt_str}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    print(f"🔍 Found {len(rows)} meetings since cutoff.")

    for row in rows:
        m_id, start_ms, title, json_content = row

        if m_id in processed_ids:
            continue

        print(f"📥 Processing: {title} ({m_id})")
        transcript_text = extract_text_from_json(json_content)

        if not transcript_text:
            transcript_text = (
                f"[Raw JSON dump due to parsing failure]\n{json_content[:2000]}..."
            )

        # Format Filename
        date_str = datetime.fromtimestamp(start_ms / 1000).strftime("%Y-%m-%d")
        safe_title = "".join(
            [c for c in (title or "Untitled") if c.isalnum() or c in " -_"]
        ).strip()
        filename = f"{date_str}-{safe_title}.md"
        output_path = OUTPUT_DIR / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write File
        content = (
            f"# {title or 'Untitled Meeting'}\n\n"
            f"**Date**: {date_str}\n"
            f"**Source**: QuillDB ({m_id})\n\n"
            f"## Transcript\n\n{transcript_text}"
        )

        with open(output_path, "w") as f:
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
