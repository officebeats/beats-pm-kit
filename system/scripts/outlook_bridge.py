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
        result = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip().replace('\r', '\n')
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
        -- Search Inbox
        set msgs to messages of inbox
        set output to ""
        set counter to 0
        repeat with msg in msgs
            if counter < 100 then
                set subj to subject of msg
                if subj contains "{subject_filter}" then
                    set output to output & "===== SUBJECT: " & subj & " =====" & return
                    set output to output & "DATE: " & (time received of msg as string) & return
                    set output to output & "FOLDER: Inbox" & return
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
        
        -- Search Sent Items
        set sentFolder to sent items
        set sentMsgs to messages of sentFolder
        set counter to 0
        repeat with msg in sentMsgs
            if counter < 100 then
                set subj to subject of msg
                if subj contains "{subject_filter}" then
                    set output to output & "===== SUBJECT: " & subj & " =====" & return
                    set output to output & "DATE: " & (time received of msg as string) & return
                    set output to output & "FOLDER: Sent Items" & return
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
        result = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip().replace('\r', '\n')
        return result
    except Exception as e:
        return f"Error: {str(e)}"



def get_calendar_events(days=14):
    """Fetch upcoming calendar events using AppleScript with de-duplication.
    
    Queries the local Microsoft Outlook app for calendar events within N days.
    Only returns events from the user's personal 'Calendar' — excludes shared
    and subscribed calendars (e.g., manager's calendar) to prevent ghost meetings.
    Returns plain text listing of unique events.
    """
    script = f'''
    tell application "Microsoft Outlook"
        set today to current date
        set limit to today + ({days} * days)
        set myEvents to calendar events whose start time >= today and start time <= limit
        set output to ""
        repeat with evt in myEvents
            set calName to name of calendar of evt
            set evtStart to (start time of evt as string)
            set output to output & subject of evt & "||" & evtStart & "||"
            try
                set l to location of evt
                set output to output & l
            on error
                set output to output & "N/A"
            end try
            set output to output & "||" & calName & "///"
        end repeat
        return output
    end tell
    '''
    try:
        result = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip().replace('\r', '\n')
        if not result:
            return "No upcoming events found from Outlook AppleScript."
        
        seen = set()
        clean_events = []
        for raw in result.split('///'):
            if not raw.strip(): continue
            parts = raw.split('||')
            if len(parts) >= 3:
                cal_name = parts[3].strip() if len(parts) > 3 else "Unknown"
                # FILTER: Only include events from the user's personal calendar
                if cal_name != "Calendar":
                    continue
                key = (parts[0].strip(), parts[1].strip())
                if key not in seen:
                    seen.add(key)
                    clean_events.append({
                        "subject": parts[0],
                        "start": parts[1],
                        "location": parts[2] if len(parts) > 2 else "N/A"
                    })
        
        # Format the unique events into a readable list
        output = "📅 CALENDAR (Personal Events Only)\n"
        output += "========================================\n\n"
        for event in sorted(clean_events, key=lambda x: x['start']):
            output += f"===== SUBJECT: {event['subject']} =====\n"
            output += f"START: {event['start']}\n"
            output += f"LOCATION: {event['location']}\n"
            output += "===== END =====\n\n"
            
        return output
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--search", type=str, default=None,
                        help="Search for full email body by subject keyword")
    parser.add_argument("--calendar", type=int, default=None,
                        help="Fetch calendar events for the next N days")
    args = parser.parse_args()
    
    if args.calendar is not None:
        print(get_calendar_events(args.calendar))
    elif args.search:        print(get_full_email_body(args.search))
    else:
        print(json.dumps(get_outlook_messages(args.count), indent=2))
