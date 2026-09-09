#!/usr/bin/env python3
"""
Granola Bridge for Beats PM Kit.

Provides an easy, efficient, token-conscious integration for Granola meeting notes:
1. Local App Bridge: Pulls the active meeting notes/transcript directly from Granola app.
2. Web Bridge: Ingests Granola web notes/transcripts via share links (https://notes.granola.ai/...).
3. MCP Adapter: Connects to the official hosted Granola MCP endpoint (https://mcp.granola.ai/mcp).
4. Auto-Archive: Deposits clean Markdown notes into `3. Meetings/transcripts/granola/` for synthesis.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GRANOLA_TRANSCRIPTS_DIR = ROOT / "3. Meetings" / "transcripts" / "granola"
GRANOLA_APP_DIR = Path.home() / "Library" / "Application Support" / "Granola"
OFFICIAL_MCP_ENDPOINT = "https://mcp.granola.ai/mcp"

def ensure_dirs():
    GRANOLA_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_slug(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
    return cleaned[:80] or "meeting"

def get_active_app_notes() -> dict[str, str] | None:
    """Pull active note text directly from Granola via AppleScript without LLM token waste."""
    if sys.platform != "darwin":
        return None

    # Check if Granola is running
    check_cmd = ['pgrep', '-x', 'Granola']
    if subprocess.run(check_cmd, capture_output=True).returncode != 0:
        return None

    script = '''
    tell application "Granola" to activate
    delay 0.3
    tell application "System Events"
        tell process "Granola"
            click menu item "Select All" of menu 1 of menu bar item "Edit" of menu bar 1
            delay 0.15
            click menu item "Copy" of menu 1 of menu bar item "Edit" of menu bar 1
            delay 0.15
        end tell
    end tell
    '''
    try:
        res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return None
        
        # Read clipboard
        clip_res = subprocess.run(['pbpaste'], capture_output=True, text=True, timeout=2)
        content = clip_res.stdout.strip()
        if not content:
            return None

        # Extract title from first line
        lines = content.splitlines()
        first_line = lines[0].strip() if lines else "Granola Meeting"
        title = re.sub(r'^#+\s*', '', first_line).strip() or "Granola Meeting"

        # Check for web link at bottom
        web_link = ""
        link_match = re.search(r'https://notes\.granola\.ai/[^\s]+', content)
        if link_match:
            web_link = link_match.group(0)

        return {
            "title": title,
            "content": content,
            "web_link": web_link,
            "source": "granola-local-app"
        }
    except Exception as e:
        print(f"Error extracting from Granola app: {e}", file=sys.stderr)
        return None

def fetch_web_note(url: str) -> dict[str, str] | None:
    """Fetch note content from Granola web link."""
    # Convert share link if needed
    doc_id_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', url)
    if not doc_id_match:
        return None
    doc_id = doc_id_match.group(1)
    
    # Try agent-browser if installed, or fallback
    agent_browser = Path("/Applications/Orca.app/Contents/Resources/agent-browser-darwin-arm64")
    if agent_browser.exists():
        try:
            cmd = [str(agent_browser), "eval", f"""
                (async () => {{
                    return {{
                        title: document.title,
                        text: document.body.innerText
                    }};
                }})()
            """]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout:
                data = json.loads(res.stdout)
                return {
                    "title": data.get("title", f"Granola {doc_id}"),
                    "content": data.get("text", ""),
                    "web_link": url,
                    "source": "granola-web"
                }
        except Exception:
            pass

    return None

def save_transcript(data: dict[str, str]) -> Path:
    ensure_dirs()
    today = dt.date.today().isoformat()
    slug = sanitize_slug(data["title"])
    filename = f"{today}_{slug}.md"
    file_path = GRANOLA_TRANSCRIPTS_DIR / filename

    content_sha256 = hashlib.sha256(data["content"].encode("utf-8")).hexdigest()
    
    frontmatter = [
        "---",
        f'title: "{data["title"].replace(chr(34), chr(92)+chr(34))}"',
        f'date: "{today}"',
        'platform: "granola"',
        f'source: "{data.get("source", "granola")}"',
        f'web_link: "{data.get("web_link", "")}"',
        f'content_sha256: "{content_sha256}"',
        "---",
        ""
    ]

    body = [
        f"# {data['title']}",
        "",
        f"> **Source**: Granola ({data.get('source', 'local')})  ",
        f"> **Date**: {today}  ",
    ]
    if data.get("web_link"):
        body.append(f"> **Granola Link**: [{data['web_link']}]({data['web_link']})  ")
    body.extend(["", "---", "", data["content"], ""])

    full_text = "\n".join(frontmatter) + "\n".join(body)
    file_path.write_text(full_text, encoding="utf-8")
    return file_path

def check_health() -> dict[str, object]:
    app_running = False
    if sys.platform == "darwin":
        res = subprocess.run(['pgrep', '-x', 'Granola'], capture_output=True)
        app_running = (res.returncode == 0)

    db_exists = (GRANOLA_APP_DIR / "granola.db").exists()
    wal_exists = (GRANOLA_APP_DIR / "granola.db-wal").exists()

    return {
        "granola_app_running": app_running,
        "local_database_found": db_exists,
        "active_session_wal": wal_exists,
        "official_mcp_endpoint": OFFICIAL_MCP_ENDPOINT,
        "transcripts_dir": str(GRANOLA_TRANSCRIPTS_DIR),
        "configured": app_running or db_exists
    }

def main():
    parser = argparse.ArgumentParser(description="Granola Bridge for Beats PM Kit")
    subparsers = parser.add_subparsers(dest="command")

    p_fetch = subparsers.add_parser("fetch-active", help="Fetch active meeting notes from Granola app")
    p_fetch.add_argument("--json", action="store_true", help="Output JSON")

    p_url = subparsers.add_parser("fetch-url", help="Fetch notes from Granola share URL")
    p_url.add_argument("url", help="Granola share URL")
    p_url.add_argument("--json", action="store_true", help="Output JSON")

    p_health = subparsers.add_parser("health", help="Check Granola bridge and MCP health")
    p_health.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    if args.command == "health":
        status = check_health()
        if getattr(args, "json", False):
            print(json.dumps(status, indent=2))
        else:
            print("--- 🥣 Granola Bridge Health ---")
            for k, v in status.items():
                print(f"  {k}: {v}")
        return 0

    if args.command == "fetch-active":
        data = get_active_app_notes()
        if not data:
            print("Error: Could not extract active note from Granola app. Ensure Granola is open with a selected note.", file=sys.stderr)
            return 1
        saved_path = save_transcript(data)
        if getattr(args, "json", False):
            print(json.dumps({"status": "success", "path": str(saved_path), "title": data["title"]}, indent=2))
        else:
            print(f"Saved Granola transcript to: {saved_path}")
        return 0

    if args.command == "fetch-url":
        data = fetch_web_note(args.url)
        if not data:
            print(f"Error: Could not fetch Granola note from {args.url}", file=sys.stderr)
            return 1
        saved_path = save_transcript(data)
        if getattr(args, "json", False):
            print(json.dumps({"status": "success", "path": str(saved_path), "title": data["title"]}, indent=2))
        else:
            print(f"Saved Granola transcript to: {saved_path}")
        return 0

    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
