"""
Quill MCP Client
Connects to Quill via MCP Bridge to fetch recent transcripts.
"""

import asyncio
import sys
import subprocess
import os
import json
import datetime
import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Path settings — dynamic resolution; no hardcoded personal paths
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent    # system/
BRAIN_DIR = SYSTEM_ROOT.parent              # beats-pm-antigravity-brain/
INCOMING_DIR = BRAIN_DIR / "0. Incoming"
TRANSCRIPT_ARCHIVE_DIR = BRAIN_DIR / "3. Meetings" / "transcripts"
REPORT_DIR = BRAIN_DIR / "3. Meetings" / "reports"

# Quill MCP bridge — falls back to user-configured env var for portability
_DEFAULT_QUILL_BRIDGE = (
    Path.home() / "Library" / "Application Support" / "Quill" / "mcp-stdio-bridge.js"
)
MCP_BRIDGE_PATH = str(os.environ.get("QUILL_MCP_BRIDGE", str(_DEFAULT_QUILL_BRIDGE)))

DAYS_TO_FETCH = 10

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()

async def main():
    if not os.path.exists(MCP_BRIDGE_PATH):
        print(f"Error: MCP Bridge not found at {MCP_BRIDGE_PATH}")
        sys.exit(1)
        
    env = os.environ.copy()
    process = subprocess.Popen(
        ["node", MCP_BRIDGE_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        env=env
    )
    
    async def send_request(method, params=None, id=1):
        request = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": id}
        process.stdin.write(json.dumps(request).encode('utf-8') + b'\n')
        process.stdin.flush()

    def read_response():
        while True:
            line = process.stdout.readline()
            if not line: return None
            try:
                data = json.loads(line.decode('utf-8'))
                if "id" in data or "method" in data:
                    return data
            except json.JSONDecodeError:
                continue

    print("[mcp-stdio-bridge] Connected to Quill MCP server")
    
    # Initialize
    await send_request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "quill-mcp-client", "version": "1.0.0"}}, id=1)
    read_response()
    await send_request("notifications/initialized", id=2)
    
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DAYS_TO_FETCH)
    print(f"Fetching transcripts from the last {DAYS_TO_FETCH} days...")

    req_id = 3
    await send_request("tools/call", {
        "name": "search_meetings",
        "arguments": {"query": ""}
    }, id=req_id)
    req_id += 1
    
    res = read_response()
    if not res or "result" not in res or not res["result"].get("content"):
        print("Failed to get response from search_meetings.")
        process.terminate()
        return

    xml_content = res["result"]["content"][0].get("text", "")
    
    meetings = []
    # Parse XML safely using regex to extract meetings
    meeting_blocks = re.findall(r'<meeting\s+id="([^"]+)"\s+date="([^"]+)"[^>]*>.*?<title>([^<]+)</title>', xml_content, re.DOTALL)
    
    for meeting_id, date_str, title in meeting_blocks:
        try:
            # Handle standard UTC string from JS
            dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            if dt >= cutoff_date:
                meetings.append((meeting_id, dt, title.strip()))
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            continue

    print(f"Found {len(meetings)} meetings via MCP within the last {DAYS_TO_FETCH} days.")
    
    new_meetings_count = 0
    for meeting_id, dt, title in meetings:
        date_prefix = dt.strftime("%Y-%m-%d")
        safe_title = sanitize_filename(title)
        
        # We don't have the explicit filename from MCP, so we use date and title.
        base_filename = f"{date_prefix}_{safe_title}.txt"
        incoming_path = INCOMING_DIR / base_filename
        archive_path = TRANSCRIPT_ARCHIVE_DIR / base_filename
        report_path = REPORT_DIR / f"{date_prefix}_{safe_title}.md"
        
        # Check if we already processed or have this
        if archive_path.exists() or report_path.exists() or incoming_path.exists():
            continue
            
        print(f"Fetching: {title} ({date_prefix})")
        
        await send_request("tools/call", {
            "name": "get_transcript",
            "arguments": {"id": meeting_id}
        }, id=req_id)
        req_id += 1
        
        t_res = read_response()
        if t_res and "result" in t_res and t_res["result"].get("content"):
            t_xml = t_res["result"]["content"][0].get("text", "")
            
            # Extract transcript content using regex out of <transcript> tag
            match = re.search(r'<transcript[^>]*>(.*?)</transcript>', t_xml, re.DOTALL)
            if match:
                transcript_text = match.group(1).strip()
            else:
                transcript_text = t_xml  # fallback
            
            # Write to incoming directory
            with open(incoming_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            new_meetings_count += 1
        else:
            print(f"Failed to fetch transcript for {title}")

    if new_meetings_count == 0:
        print("No new meetings to import.")
    else:
        print(f"Successfully imported {new_meetings_count} new transcripts into 0. Incoming/")

    process.terminate()

if __name__ == "__main__":
    asyncio.run(main())
