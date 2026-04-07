import subprocess
import json
import argparse

def get_outlook_messages(count=5):
    """Fetch recent messages from Outlook using AppleScript.
    
    Uses osascript to query the local Microsoft Outlook app.
    Handles mixed message types (standard + meeting invites) gracefully.
    """
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
            set dt to (time received of msg) as string
            
            -- Sender: handle missing name gracefully
            set senderName to ""
            set senderAddr to ""
            try
                set snd to sender of msg
                try
                    set senderName to name of snd
                end try
                try
                    set senderAddr to address of snd
                end try
            end try
            if senderName is "" then set senderName to senderAddr
            
            -- Snippet: truncate HTML body to 200 chars
            set snp to ""
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
            
            set output to output & sub & "||" & senderName & " <" & senderAddr & ">" & "||" & dt & "||" & snp & "///"
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


def get_full_email_body(subject_filter):
    """Fetch the full plain-text body of emails matching a subject filter.
    
    Uses osascript to query the local Microsoft Outlook app.
    Returns full email content for targeted extraction (not just snippets).
    
    Args:
        subject_filter: String to match against email subjects (case-sensitive contains).
    
    Returns:
        List of dicts with subject, date, body keys.
    """
    script = f'''
    tell application "Microsoft Outlook"
        set msgs to messages of inbox
        set output to ""
        set counter to 0
        repeat with msg in msgs
            if counter < 20 then
                set subj to subject of msg
                if subj contains "{subject_filter}" then
                    set output to output & "===== SUBJECT: " & subj & " =====" & return
                    set output to output & "DATE: " & (time received of msg as string) & return
                    set output to output & "BODY:" & return
                    try
                        set output to output & (plain text content of msg) & return
                    on error
                        try
                            set output to output & (content of msg) & return
                        end try
                    end try
                    set output to output & "===== END =====" & return & return
                end if
                set counter to counter + 1
            end if
        end repeat
        return output
    end tell
    '''
    try:
        result = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
        return result
    except Exception as e:
        return f"Error: {{str(e)}}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--search", type=str, default=None,
                        help="Search for full email body by subject keyword")
    args = parser.parse_args()
    
    if args.search:
        print(get_full_email_body(args.search))
    else:
        print(json.dumps(get_outlook_messages(args.count), indent=2))
