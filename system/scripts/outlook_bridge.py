import subprocess
import json
import argparse

def get_outlook_messages(count=5):
    """Fetch recent messages from Outlook using AppleScript."""
    script = f'''
    tell application "Microsoft Outlook"
        set inboxFolder to inbox
        set allMessages to messages of inboxFolder
        set msgCount to count of allMessages
        if msgCount > {count} then set msgCount to {count}
        
        set output to ""
        repeat with i from 1 to msgCount
            set msg to item i of allMessages
            set sub to subject of msg
            set snd to sender of msg
            set nm to name of snd
            set ad to address of snd
            set dt to (time received of msg) as string
            
            try
                set bdy to content of msg
                if length of bdy > 200 then
                    set snp to text 1 thru 200 of bdy
                else
                    set snp to bdy
                end if
            on error
                set snp to "[Unreadable content]"
            end try
            
            set output to output & sub & "||" & nm & " <" & ad & ">" & "||" & dt & "||" & snp & "///"
        end repeat
        return output
    end tell
    '''
    try:
        result = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
        messages = []
        for raw in result.split('///'):
            if not raw.strip(): continue
            parts = raw.split('||')
            if len(parts) >= 4:
                messages.append({
                    "subject": parts[0],
                    "sender": parts[1],
                    "date": parts[2],
                    "snippet": parts[3].replace('\r', ' ').replace('\n', ' ')
                })
        return messages
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(get_outlook_messages(args.count), indent=2))
