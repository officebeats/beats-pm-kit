import subprocess
import json
import argparse
import sys
import os

def get_clipboard_text():
    """Get text from macOS clipboard using pbpaste."""
    try:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    return None

def get_teams_messages_ui(count=15):
    """
    Attempt to scrape Teams via UI Scripting (requires Accessibility/Admin).
    """
    script = f'''
    tell application "System Events"
        if not (exists process "Microsoft Teams") then
            return "ERROR: Microsoft Teams is not running."
        end if
        
        tell process "Microsoft Teams"
            set frontmost to true
            delay 0.5
            try
                set outputText to ""
                set msgList to (first UI element of window 1 whose role description is "Message list")
                set msgItems to every UI element of msgList
                repeat with msgItem in msgItems
                    set outputText to outputText & (description of msgItem) & "|||"
                end repeat
                return outputText
            on error
                return "ERROR: No access"
            end try
        end tell
    end tell
    '''
    try:
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=5)
        raw = proc.stdout.strip()
        if raw and not raw.startswith("ERROR"):
            return [m.strip() for m in raw.split("|||") if m.strip()][-count:]
    except:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Beats PM Teams Bridge")
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    # 1. Try UI Scripting first (Autonomous)
    messages = get_teams_messages_ui(args.count)
    source = "UI Scripting"
    
    # 2. Fallback to Clipboard (User-assisted / Non-Admin)
    if not messages:
        clipboard = get_clipboard_text()
        if clipboard:
            messages = [m.strip() for m in clipboard.split('\n') if m.strip()][-args.count:]
            source = "Clipboard (pbpaste)"
    
    if not messages:
        print("\n[!] Teams Bridge: Access Denied or Empty.")
        print("TIP: Since you don't have Admin permissions for Accessibility:")
        print("  1. Go to Teams and Select All (CMD+A) + Copy (CMD+C)")
        print("  2. Run this command again.\n")
        sys.exit(1)
        
    if args.json:
        print(json.dumps(messages, indent=2))
    else:
        print(f"\n=== CAPTURED {len(messages)} TEAMS FRAGMENTS ({source}) ===")
        for i, msg in enumerate(messages):
            print(f"[{i}] {msg}")
        print("\n--- END OF CAPTURE ---")

if __name__ == "__main__":
    main()
